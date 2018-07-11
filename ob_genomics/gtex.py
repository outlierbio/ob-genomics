import os.path as op
from subprocess import check_output

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


def load_gtex_median_tpm(fpath=GTEX_MEDIAN_TPM):
    df = (
        pd.read_csv(fpath, sep='\t', skiprows=2)
        .melt(id_vars=['gene_id', 'Description'],
              var_name='tissue', value_name='median_tpm')
        )
    df['ensembl_id'] = df['gene_id'].map(lambda s: s.split('.')[0])

    conn = db.engine.connect()
    conn.execute("INSERT INTO source (source_id) VALUES ('GTEx')")

    (df[['ensembl_id', 'tissue', 'median_tpm']]
        .to_sql('tmp_gtex', conn, if_exists='replace', index=False))
    conn.execute('''
        INSERT INTO tissue_gene_value
        (source_id, tissue_id, gene_id, data_type, unit, value)
        SELECT 'GTEx', t.tissue_id, g.gene_id, 'expression',
               'median_tpm', tmp.median_tpm
        FROM tmp_gtex tmp
        INNER JOIN tissue t ON t.gtex_id = tmp.tissue
        INNER JOIN gene g ON g.ensembl_id = tmp.ensembl_id
    ''')
