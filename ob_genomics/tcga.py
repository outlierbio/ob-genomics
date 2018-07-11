import os.path as op
from subprocess import check_output

import pandas as pd

from ob_genomics.config import cfg
import ob_genomics.database as db

REFERENCE = cfg['REFERENCE']
IMMUNE_LANDSCAPE = op.join(REFERENCE, 'tcga', 'immune_landscape.csv')
TCGA_SAMPLE_META = op.join(REFERENCE, 'tcga', 'sample_meta.csv')
TCGA_COHORT_META = op.join(REFERENCE, 'tcga', 'cohort.csv')
TCGA_SAMPLE_CODE = op.join(REFERENCE, 'tcga', 'sample_code.csv')
GDAC_LATEST = '2016_07_15'

gdac_params = {
    'mutation': {
        'data_type': 'Mutation_Packager_Oncotated',
        'run_type': 'stddata'
    },
    'expression': {
        'data_type': 'RSEM_genes_normalized',
        'run_type': 'stddata'
    },
    'copy_number': {
        'data_type': 'Gistic2',
        'run_type': 'analyses'
    }
}


def download_gdac(data_type, cohort, date=GDAC_LATEST):
        params = gdac_params['data_type']
        short_date = date.replace('_', '')
        folder = f"{params['run_type']}__{date}/{cohort}/{short_date}"
        check_output(f'''
            firehose_get -o {params['data_type']} \
                {params['run_type']} {date} {cohort}
            tar -xvf {folder}/*{params['data_type']}*.tar.gz -C {folder}/
        ''', shell=True)


def gdac_to_table(f, ncols=2):
    pass


def load_tcga_sample_meta(fpath=TCGA_SAMPLE_META):
    meta = pd.read_csv(fpath)
    meta = meta[['cohort', 'patient', 'sample', 'sample_code', 'sample_type']]
    meta.columns = ['cohort_id', 'patient_id', 'sample_id', 'sample_code',
                    'sample_type']

    conn = db.engine.connect()
    (meta
        [['cohort_id']]
        .drop_duplicates()
        .to_sql('cohort', conn, if_exists='replace', index=False))
    (meta
        [['patient_id', 'cohort_id']]
        .drop_duplicates()
        .to_sql('patient', conn, if_exists='replace', index=False))
    (meta
        [['sample_id', 'patient_id', 'sample_code', 'sample_type']]
        .drop_duplicates()
        .to_sql('sample', conn, if_exists='replace', index=False))
    conn.close()


def load_immune_value(col, fpath=IMMUNE_LANDSCAPE):
    df = pd.read_csv(fpath)
    df['data_type'] = col.lower()
    reordered = df[['TCGA Participant Barcode', 'data_type', col]]
    reordered.columns = ['patient_id', 'data_type', 'value']

    if reordered.dtypes[2] == object:
        table = 'patient_text_value'
    else:
        table = 'patient_value'

    conn = db.engine.connect()
    (reordered
        .dropna(subset=['value'])
        .to_sql(table, conn, if_exists='append', index=False))
    conn.close()


def load_tcga_profile(data_type, fpath):
        if data_type == 'copy number':
            cols = ['entrez_id', 'sample', 'data_type', 'unit', 'copy_number']
            unit = 'log2 ratio'
        elif data_type == 'expression':
            cols = ['entrez_id', 'sample', 'data_type', 'unit', 'normalized_counts']
            unit = 'normalized_counts'
        else:
            raise ValueError('Data type not recognized')

        db.load_sample_gene_values(fpath, data_type, cols, unit)
