import io
import os.path as op

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ob_genomics.config import cfg
from ob_genomics import models

DATABASE_URI = cfg['DATABASE_URI']
REFERENCE = cfg['REFERENCE']
GENE = op.join(REFERENCE, 'ncbi', 'genes.hs.csv')
GENE_HISTORY = op.join(REFERENCE, 'ncbi', 'gene_history.hs.tsv')
UNC_TX_TO_GENE_FPATH = cfg['REFERENCE'] + '/tcga/rnaseqv2/unc_knownToLocus.txt'
GENCODE_TX_TO_GENE_FPATH = cfg['REFERENCE'] + '/gencode/gencode.v19.metadata.HGNC.txt'
TISSUE = op.join(REFERENCE, 'tissue', 'tissue.csv')
CELL_TYPE = op.join(REFERENCE, 'tissue', 'cell_type.csv')
TEST_GENES = [3845, 7157, 4609, 2597]

engine = create_engine(DATABASE_URI)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
current_session = Session()


def safe_commit(session):
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        raise


def destroy():
    models.base.metadata.drop_all(bind=engine)


def create():
    models.base.metadata.create_all(bind=engine)


def copy(output, table):
    '''Use Postgres COPY command in production'''
    conn = engine.raw_connection()
    cur = conn.cursor()
    cur.copy_from(output, table)
    conn.commit()
    conn.close()


def copy_from_df(df, table):
    output = io.StringIO()
    df.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)
    output.getvalue()
    copy(output, table)


def copy_from_csv(fpath, table):
    with open(fpath, 'r') as f:
        copy(f, table)


def get_ensembl_gene(ref_str):
    '''Extract Ensembl ID from NCBI gene_info dbXrefs column'''
    refs = ref_str.split('|')
    ensembl_str = [ref for ref in refs if ref.startswith('Ensembl')]
    if len(ensembl_str) == 0:
        return None
    if len(ensembl_str) == 1:
        return ensembl_str[0].split(':')[1]


def load_genes(gene_info_fpath=GENE, gene_history_fpath=GENE_HISTORY):
    gene_info = pd.read_csv(gene_info_fpath)
    gene_info.columns = ['gene_id', 'ensembl_id', 'symbol']

    gene_history = pd.read_csv(gene_history_fpath, sep="\t")
    gene_history.columns = [
        "taxid",
        "new_gene_id",
        "gene_id",
        "symbol",
        "discontinued_date",
    ]
    gene_history["ensembl_id"] = None

    df = pd.concat([
        gene_info,
        gene_history[["gene_id", "ensembl_id", "symbol"]]
    ]).drop_duplicates(subset=['gene_id'])

    copy_from_df(df, 'gene')


def load_isoforms(
        unc_fpath=UNC_TX_TO_GENE_FPATH,
        gencode_fpath=GENCODE_TX_TO_GENE_FPATH):

    # UNC
    df = pd.read_csv(unc_fpath, sep='\t', header=None)
    df.columns = ['mapping', 'isoform_id']

    df['symbol'] = df['mapping'].map(
        lambda s: s.split('|')[0] if '|' in s else None)
    df['gene_id'] = df['mapping'].map(
        lambda s: s.split('|')[1] if '|' in s else '\\N')
    df.loc[:, 'source'] = 'UCSC knownGene'

    copy_from_df(df[['isoform_id', 'gene_id', 'source']], 'isoform')

    # GENCODE
    gencode = pd.read_csv(gencode_fpath, sep='\t', header=None)
    gencode.columns = ['isoform_id', 'symbol']
    gencode = gencode.drop_duplicates(subset='isoform_id')

    conn = engine.connect()
    conn.execute('''
        CREATE TABLE tmp_gencode_isoform
        (isoform_id varchar, symbol varchar)
    ''')

    try:
        copy_from_df(gencode, 'tmp_gencode_isoform')

        conn.execute('''
            INSERT INTO isoform
            (isoform_id, gene_id, source)
            SELECT tmp.isoform_id, MIN(g.gene_id), 'GENCODE v19'
            FROM tmp_gencode_isoform tmp
            INNER JOIN gene g ON g.symbol = tmp.symbol
            GROUP BY tmp.isoform_id
        ''')
    finally:
        conn.execute('DROP TABLE tmp_gencode_isoform')
        conn.close()


def load_tissues(fpath=TISSUE):
    tissue = pd.read_csv(fpath)
    copy_from_df(tissue, 'tissue')


def load_cell_types(fpath=CELL_TYPE):
    cell_type = (
        pd.read_csv(fpath)
        [['cell_type_id', 'tissue_id', 'cell_type']]
        .drop_duplicates(subset='cell_type_id')
    )
    copy_from_df(cell_type, 'cell_type')


def load_sample_gene_values(fpath, data_type, cols, unit, env=cfg['ENV']):
    df = pd.read_csv(fpath)
    if 'data_type' not in df.columns:
        df['data_type'] = data_type
    if 'unit' not in df.columns:
        df['unit'] = unit
    df = df[cols]
    df.columns = ['sample_id', 'gene_id', 'data_type', 'unit', 'value']
    df = df.drop_duplicates(subset=['sample_id', 'gene_id', 'data_type'])

    df = df[df['gene_id'] > 0]

    if env == 'dev':
        df = df[df['gene_id'].isin(TEST_GENES)]

    copy_from_df(df, 'sample_gene_value')
