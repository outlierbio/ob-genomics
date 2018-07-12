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
        'data_type': 'Mutation_Packager_Oncotated_Calls.Level_3',
        'run_type': 'stddata',
        'suffix': 'maf.txt'
    },
    'expression': {
        'data_type': 'Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_genes_normalized__data.Level_3',
        'run_type': 'stddata',
        'suffix': 'rsem_normalized.csv'
    },
    'copy number': {
        'data_type': 'CopyNumber_Gistic2.Level_4',
        'run_type': 'analyses',
        'suffix': 'copy_number.csv'
    },
    'clinical': {
        'data_type': 'Clinical_Pick_Tier1.Level_4',
        'run_type': 'stddata',
        'suffix': 'clin.merged.picked.txt'
    }
}


def download_gdac(data_type, cohort, date=GDAC_LATEST):
        params = gdac_params['data_type']
        short_date = date.replace('_', '')
        folder = f"{params['run_type']}__{date}/{cohort}/{short_date}"
        check_output(f'''
            firehose_get -o {params['data_type']} \
                {params['run_type']} {date} {cohort}
            tar -xvf {folder}/gdac.broadinstitute.org_{cohort}.{params['data_type']}*.tar.gz -C {folder}/
            cp {folder}/*{cohort}.{params['data_type']}*/*{params['clinical']['filename']}
        ''', shell=True)


def extract_gdac(data_type):
    if data_type == 'mutation':
        check_output(f'''
            for cohort in `ls stddata__2016_07_15`
            do
                folder=stddata__2016_07_15/$cohort/20160715/gdac.broadinstitute.org_$cohort.Mutation_Packager_Calls.Level_3.2016071500.0.0
                first_file=`ls $folder/TCGA* | head -1`
                head -1 $first_file \
                    > tables/$cohort.maf.txt
                cat $folder/TCGA*.maf.txt \
                    | grep -v Hugo_Symbol \
                    >> tables/$cohort.maf.txt
            done
        ''')


def load_tcga_sample_meta(fpath=TCGA_SAMPLE_META):
    meta = pd.read_csv(fpath)
    meta = meta[['cohort', 'patient', 'sample', 'sample_code', 'sample_type']]
    meta.columns = ['cohort_id', 'patient_id', 'sample_id', 'sample_code',
                    'sample_type']
    meta['source_id'] = 'TCGA'

    conn = db.engine.connect()
    conn.execute("INSERT INTO source (source_id) VALUES ('TCGA')")
    (meta
        [['cohort_id', 'source_id']]
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


def is_numeric(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


def load_immune_landscape(fpath=IMMUNE_LANDSCAPE):
    df = (
        pd.read_csv(fpath)
        .drop('TCGA Study', axis=1)
        .rename(columns={
            'TCGA Participant Barcode': 'patient_id',
            'Eosinophils.0': 'Eosinophils score',
            'Neutrophils.0': 'Neutrophils score',
            'Eosinophils.1': 'Eosinophils',
            'Neutrophils.1': 'Neutrophils'})
        .melt(id_vars='patient_id', var_name='data_type', value_name='value')
    )

    immune_landscape_units = {'Immune Subtype': 'subtype', 'TCGA Subtype': 'subtype', 'Leukocyte Fraction': 'fraction', 'Stromal Fraction': 'fraction', 'Intratumor Heterogeneity': 'fraction', 'TIL Regional Fraction': 'fraction', 'Proliferation': 'score', 'Wound Healing': 'score', 'Macrophage Regulation': 'score', 'Lymphocyte Infiltration Signature Score': 'score', 'IFN-gamma Response': 'score', 'TGF-beta Response': 'score', 'SNV Neoantigens': 'count', 'Indel Neoantigens': 'count', 'Silent Mutation Rate': 'rate', 'Nonsilent Mutation Rate': 'rate', 'Number of Segments': 'count', 'Fraction Altered': 'fraction', 'Aneuploidy Score': 'score', 'Homologous Recombination Defects': 'count', 'BCR Evenness': 'fraction', 'BCR Shannon': 'fraction', 'BCR Richness': 'fraction', 'TCR Shannon': 'fraction', 'TCR Richness': 'fraction', 'TCR Evenness': 'fraction', 'CTA Score': 'score', 'Th1 Cells': 'score', 'Th2 Cells': 'score', 'Th17 Cells': 'score', 'OS': 'censored', 'OS Time': 'days', 'PFI': 'censored', 'PFI Time': 'days', 'B Cells Memory': 'signature score', 'B Cells Naive': 'signature score', 'Dendritic Cells Activated': 'signature score', 'Dendritic Cells Resting': 'signature score', 'Eosinophils score': 'signature score', 'Macrophages M0': 'signature score', 'Macrophages M1': 'signature score', 'Macrophages M2': 'signature score', 'Mast Cells Activated': 'signature score', 'Mast Cells Resting': 'signature score', 'Monocytes': 'signature score', 'Neutrophils score': 'signature score', 'NK Cells Activated': 'signature score', 'NK Cells Resting': 'signature score', 'Plasma Cells': 'signature score', 'T Cells CD4 Memory Activated': 'signature score', 'T Cells CD4 Memory Resting': 'signature score', 'T Cells CD4 Naive': 'signature score', 'T Cells CD8': 'signature score', 'T Cells Follicular Helper': 'signature score', 'T Cells gamma delta': 'signature score', 'T Cells Regulatory Tregs': 'signature score', 'Lymphocytes': 'signature score', 'Neutrophils': 'signature score', 'Eosinophils': 'signature score', 'Mast Cells': 'signature score', 'Dendritic Cells': 'signature score', 'Macrophages': 'signature score'}
    df['unit'] = df['data_type'].map(lambda dt: immune_landscape_units[dt])

    # Split into numeric values and text values
    df['is_numeric'] = df['value'].map(is_numeric)
    df_numeric = df[df['is_numeric']]
    df_numeric['value'] = df_numeric['value'].map(float)
    df_text = df[~df['is_numeric']]

    # Load to database in respective tables
    conn = db.engine.connect()
    (df_numeric[['patient_id', 'data_type', 'unit', 'value']]
        .drop_duplicates(subset=['patient_id', 'data_type'])
        .dropna(subset=['value'])
        .to_sql('patient_value', conn, if_exists='append', index=False))
    (df_text[['patient_id', 'data_type', 'unit', 'value']]
        .drop_duplicates(subset=['patient_id', 'data_type'])
        .dropna(subset=['value'])
        .to_sql('patient_text_value', conn, if_exists='append', index=False))
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


def load_tcga_clinical(fpath):
    mat = pd.read_csv(fpath, sep='\t')
    df = mat.melt(id_vars='Hybridization REF', var_name='patient_id',
                  value_name='value')
    df = df[df['Hybridization REF'] != 'Composite Element REF']
    df['patient_id'] = df['patient_id'].str.upper()
    df['unit'] = 'clinical'
    df = df.rename(columns={'Hybridization REF': 'data_type'})
    df = df.drop_duplicates(subset=['patient_id', 'data_type'])
    df = df.dropna(subset=['value'])

    df['is_numeric'] = df['value'].map(is_numeric)
    df_numeric = df[df['is_numeric']]
    df_text = df[~df['is_numeric']]

    conn = db.engine.connect()

    (df_numeric[['patient_id', 'data_type', 'unit', 'value']]
        .to_sql('patient_value', conn, if_exists='append', index=False))
    (df_text[['patient_id', 'data_type', 'unit', 'value']]
        .to_sql('patient_text_value', conn, if_exists='append', index=False))
    conn.close()


def load_tcga_mutation(fpath):
    maf = pd.read_csv(fpath, sep='\t')
    df = maf[['Entrez_Gene_Id', 'Tumor_Sample_Barcode',
              'Variant_Classification', 'Variant_Type', 'AAChange']]
    df['sample_id'] = df['Tumor_Sample_Barcode'].map(lambda s: s[:15])
    df = df.drop('Tumor_Sample_Barcode', axis=1)
    df = df.rename(columns={
        'Entrez_Gene_Id': 'gene_id',
        'Variant_Type': 'variant type',
        'Variant_Classification': 'variant classification',
        'AAChange': 'AA change'})
    df = df.melt(id_vars=['sample_id', 'gene_id'],
                 var_name='data_type', value_name='value')
    df['unit'] = 'mutation'
    df = df.drop_duplicates(subset=['gene_id', 'sample_id', 'data_type'])
    df = df.dropna(subset=['value'])

    conn = db.engine.connect()

    (df[['sample_id', 'gene_id', 'data_type', 'unit', 'value']]
        .to_sql('sample_gene_text_value', conn, if_exists='append', index=False))
    conn.close()
