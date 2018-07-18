import io
import os.path as op

import pandas as pd
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ob_genomics.config import cfg
from ob_genomics import models

DATABASE_URI = cfg['DATABASE_URI']
REFERENCE = cfg['REFERENCE']
GENE = op.join(REFERENCE, 'ncbi', 'genes.hs.csv')
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


def init_db():
    models.base.metadata.drop_all(bind=engine)
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


def load_genes(fpath=GENE):
    gene_info = pd.read_csv(fpath)
    gene_info.columns = ['gene_id', 'ensembl_id', 'symbol']
    copy_from_df(gene_info, 'gene')


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
