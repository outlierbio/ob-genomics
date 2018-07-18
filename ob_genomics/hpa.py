import os.path as op

import pandas as pd

from ob_genomics.config import cfg
import ob_genomics.database as db

REFERENCE = cfg['REFERENCE']
HPA_NORMAL_TISSUE = op.join(REFERENCE, 'hpa', 'normal_tissue.tsv')
HPA_RNA_TISSUE = op.join(REFERENCE, 'hpa', 'rna_tissue.tsv')
CELL_TYPES = op.join(REFERENCE, 'tissue', 'cell_type.csv')
TISSUES = op.join(REFERENCE, 'tissue', 'tissue.csv')
TEST_GENES = ['GAPDH', 'MYC', 'KRAS', 'TP53']


def load_hpa_protein(fpath=HPA_NORMAL_TISSUE, env=cfg['ENV']):
    cell_types = pd.read_csv(CELL_TYPES)
    df = pd.read_csv(fpath, sep='\t')

    # if env == 'test':
    #     df = df[df['Gene name'].isin(TEST_GENES)]

    formatted = (
        df[df['Reliability'] != 'Uncertain']
        .merge(
            cell_types,
            left_on=['Tissue', 'Cell type'],
            right_on=['hpa_tissue_id', 'cell_type'])
        [['Gene', 'cell_type_id', 'Level']]
        .drop_duplicates(subset=['cell_type_id', 'Gene']))

    conn = db.engine.connect()

    conn.execute("INSERT INTO source (source_id) VALUES ('HPA')")

    # Load to temp table
    conn.execute('DROP TABLE IF EXISTS tmp_hpa_prot')
    conn.execute('''
        CREATE TABLE tmp_hpa_prot
        (Gene varchar, cell_type_id varchar, Level varchar)
    ''')
    db.copy_from_df(formatted, 'tmp_hpa_prot')

    # Insert from temp, joining to existing keys (cell type, gene)
    conn.execute('''
        INSERT INTO cell_type_gene_text_value
        (source_id, cell_type_id, gene_id, data_type, unit, value)
        SELECT 'HPA', tmp.cell_type_id, g.gene_id, 'protein',
               'detection level', tmp.Level
        FROM tmp_hpa_prot tmp
        INNER JOIN gene g ON g.ensembl_id = tmp.Gene
    ''')

    conn.close()


def load_hpa_expression(fpath=HPA_RNA_TISSUE, env=cfg['ENV']):
    tissues = pd.read_csv(TISSUES)
    df = pd.read_csv(fpath, sep='\t')

    # if env == 'test':
    #     df = df[df['Gene name'].isin(TEST_GENES)]

    formatted = (
        df
        .merge(
            tissues,
            left_on='Sample', right_on='hpa_id')
        [['Gene', 'tissue_id', 'Value']]
        .drop_duplicates(subset=['tissue_id', 'Gene']))

    conn = db.engine.connect()

    # Load to temp table
    conn.execute('DROP TABLE IF EXISTS tmp_hpa_expr')
    conn.execute('''
        CREATE TABLE tmp_hpa_expr
        (Gene varchar, tissue_id varchar, Value numeric)
    ''')
    db.copy_from_df(formatted, 'tmp_hpa_expr')

    # Insert from temp, joining to existing keys (cell type, gene)
    conn.execute('''
        INSERT INTO tissue_gene_value
        (source_id, tissue_id, gene_id, data_type, unit, value)
        SELECT 'HPA', tmp.tissue_id, g.gene_id, 'expression',
               'TPM', tmp.Value
        FROM tmp_hpa_expr tmp
        INNER JOIN gene g ON g.ensembl_id = tmp.Gene
    ''')
    conn.execute('DROP TABLE IF EXISTS tmp_hpa_expr')
    conn.close()
