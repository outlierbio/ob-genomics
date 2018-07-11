import os.path as op

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ob_genomics.config import cfg
from ob_genomics import models

DATABASE_URI = cfg['DATABASE_URI']
REFERENCE = cfg['REFERENCE']
GENE_INFO = op.join(REFERENCE, 'ncbi', 'Homo_sapiens.gene_info')
TISSUE = op.join(REFERENCE, 'tissue', 'tissue.csv')
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


def get_ensembl_gene(ref_str):
    '''Extract Ensembl ID from NCBI gene_info dbXrefs column'''
    refs = ref_str.split('|')
    ensembl_str = [ref for ref in refs if ref.startswith('Ensembl')]
    if len(ensembl_str) == 0:
        return None
    if len(ensembl_str) == 1:
        return ensembl_str[0].split(':')[1]


def load_genes(fpath=GENE_INFO):
    gene_info = pd.read_csv(fpath, sep='\t')
    gene_info['ensembl_id'] = gene_info['dbXrefs'].map(get_ensembl_gene)
    gene_info = gene_info[['GeneID', 'ensembl_id', 'Symbol']]
    gene_info.columns = ['gene_id', 'ensembl_id', 'symbol']

    conn = engine.connect()
    gene_info.to_sql('gene', conn, if_exists='append', index=False)
    conn.close()


def load_tissues(fpath=TISSUE):
    tissue = pd.read_csv(fpath)

    conn = engine.connect()
    tissue.to_sql('tissue', conn, if_exists='append', index=False)


def load_sample_gene_values(fpath, data_type, cols, unit, env=cfg['ENV']):
    df = pd.read_csv(fpath)
    if 'data_type' not in df.columns:
        df['data_type'] = data_type
    if 'unit' not in df.columns:
        df['unit'] = unit
    df = df[cols]
    df.columns = ['gene_id', 'sample_id', 'data_type', 'unit', 'value']
    df = df.drop_duplicates(subset=['gene_id', 'sample_id', 'data_type'])

    if env == 'test':
        df = df[df['gene_id'].isin(TEST_GENES)]

    conn = engine.connect()
    df.to_sql(f'tmp_sample_gene_values', conn,
              if_exists='replace', index=False)

    # Insert from tmp table ignoring duplicates
    conn.execute('''
        INSERT OR IGNORE
        INTO sample_gene_value (gene_id, sample_id, data_type, unit, value)
        SELECT gene_id, sample_id, data_type, unit, value
        FROM tmp_sample_gene_values
    ''')
    conn.execute('DROP TABLE tmp_sample_gene_values')
    conn.close()
