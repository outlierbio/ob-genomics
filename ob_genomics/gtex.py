import os.path as op

import pandas as pd

from ob_genomics.config import cfg
import ob_genomics.database as db

REFERENCE = cfg['REFERENCE']
GTEX_TPM = op.join(
    REFERENCE, 'gtex',
    'GTEx_Analysis_2016-01-15_v7_RNASeQCv1.1.8_gene_tpm.gct')
GTEX_MEDIAN_TPM = op.join(
    REFERENCE, 'gtex',
    'GTEx_Analysis_2016-01-15_v7_RNASeQCv1.1.8_gene_median_tpm.gct')
TEST_GENES = ['GAPDH', 'MYC', 'KRAS', 'TP53']


def load_gtex_median_tpm(fpath=GTEX_MEDIAN_TPM, env=cfg['ENV']):
    df = (
        pd.read_csv(fpath, sep='\t', skiprows=2)
        .melt(id_vars=['gene_id', 'Description'],
              var_name='tissue', value_name='median_tpm')
        )
    df['ensembl_id'] = df['gene_id'].map(lambda s: s.split('.')[0])

    if env == 'dev':
        df = df[df['Description'].isin(TEST_GENES)]

    conn = db.engine.connect()
    conn.execute("INSERT INTO source (source_id) VALUES ('GTEx')")

    conn.execute('''
        CREATE TABLE tmp_gtex
        (ensembl_id varchar, tissue varchar, median_tpm numeric)
    ''')

    selected = df[['ensembl_id', 'tissue', 'median_tpm']]
    db.copy_from_df(selected, 'tmp_gtex')

    conn.execute('''
        INSERT INTO tissue_gene_value
        (source_id, tissue_id, gene_id, data_type, unit, value)
        SELECT 'GTEx', t.tissue_id, g.gene_id, 'expression',
               'median_tpm', tmp.median_tpm
        FROM tmp_gtex tmp
        INNER JOIN tissue t ON t.gtex_id = tmp.tissue
        INNER JOIN gene g ON g.ensembl_id = tmp.ensembl_id
    ''')

    conn.execute('DROP TABLE tmp_gtex')

    conn.close()
