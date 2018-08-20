import os.path as op
from subprocess import check_output

import pandas as pd

from ob_genomics.config import cfg
import ob_genomics.database as db
from ob_genomics.utils import is_numeric

REFERENCE = cfg['REFERENCE']

# TODO: move these to config.yml
IMMUNE_LANDSCAPE = op.join(REFERENCE, 'tcga', 'immune_landscape.csv')
TCIA_PATIENT = op.join(REFERENCE, 'tcga', 'tcia', 'patientsAll.tsv')
TCIA_GSEA_DEPLETION = op.join(REFERENCE, 'tcga', 'tcia',
                              'TCIA_GSEA_depletion.tsv')
TCIA_GSEA_ENRICHMENT = op.join(REFERENCE, 'tcga', 'tcia',
                               'TCIA_GSEA_enrichment.tsv')
TCGA_SAMPLE_META = op.join(REFERENCE, 'tcga', 'sample_meta', 'sample.csv')
TCGA_PATIENT_META = op.join(REFERENCE, 'tcga', 'sample_meta', 'patient.csv')
TCGA_COHORT_META = op.join(REFERENCE, 'tcga', 'sample_meta', 'cohort.csv')
TCGA_SAMPLE_CODE = op.join(REFERENCE, 'tcga', 'sample_code.csv')
GDAC_LATEST = '2016_07_15'
TEST_GENES = [3845, 7157, 4609, 2597]
IMMUNE_LANDSCAPE_UNITS = {
    'Immune Subtype': 'subtype',
    'TCGA Subtype': 'subtype',
    'Leukocyte Fraction': 'fraction',
    'Stromal Fraction': 'fraction',
    'Intratumor Heterogeneity': 'fraction',
    'TIL Regional Fraction': 'fraction',
    'Proliferation': 'score',
    'Wound Healing': 'score',
    'Macrophage Regulation': 'score',
    'Lymphocyte Infiltration Signature Score': 'score',
    'IFN-gamma Response': 'score',
    'TGF-beta Response': 'score',
    'SNV Neoantigens': 'count',
    'Indel Neoantigens': 'count',
    'Silent Mutation Rate': 'rate',
    'Nonsilent Mutation Rate': 'rate',
    'Number of Segments': 'count',
    'Fraction Altered': 'fraction',
    'Aneuploidy Score': 'score',
    'Homologous Recombination Defects': 'count',
    'BCR Evenness': 'score',
    'BCR Shannon': 'score',
    'BCR Richness': 'score',
    'TCR Shannon': 'score',
    'TCR Richness': 'score',
    'TCR Evenness': 'score',
    'CTA Score': 'score',
    'Th1 Cells': 'score',
    'Th2 Cells': 'score',
    'Th17 Cells': 'score',
    'OS': 'censored',
    'OS Time': 'days',
    'PFI': 'censored',
    'PFI Time': 'days',
    'B Cells Memory': 'signature score',
    'B Cells Naive': 'signature score',
    'Dendritic Cells Activated': 'signature score',
    'Dendritic Cells Resting': 'signature score',
    'Eosinophils score': 'signature score',
    'Macrophages M0': 'signature score',
    'Macrophages M1': 'signature score',
    'Macrophages M2': 'signature score',
    'Mast Cells Activated': 'signature score',
    'Mast Cells Resting': 'signature score',
    'Monocytes': 'signature score',
    'Neutrophils score': 'signature score',
    'NK Cells Activated': 'signature score',
    'NK Cells Resting': 'signature score',
    'Plasma Cells': 'signature score',
    'T Cells CD4 Memory Activated': 'signature score',
    'T Cells CD4 Memory Resting': 'signature score',
    'T Cells CD4 Naive': 'signature score',
    'T Cells CD8': 'signature score',
    'T Cells Follicular Helper': 'signature score',
    'T Cells gamma delta': 'signature score',
    'T Cells Regulatory Tregs': 'signature score',
    'Lymphocytes': 'signature score',
    'Neutrophils': 'signature score',
    'Eosinophils': 'signature score',
    'Mast Cells': 'signature score',
    'Dendritic Cells': 'signature score',
    'Macrophages': 'signature score',
}

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
    'isoforms': {
        'data_type': 'Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_isoforms_normalized__data.Level_3',
        'run_type': 'stddata',
        'suffix': 'isoform.csv'
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


def load_tcga_sample_meta(cohort_fpath=TCGA_COHORT_META,
                          patient_fpath=TCGA_PATIENT_META,
                          sample_fpath=TCGA_SAMPLE_META):

    conn = db.engine.connect()
    conn.execute("INSERT INTO source (source_id) VALUES ('TCGA')")

    cohort = (pd.read_csv(cohort_fpath)
              .assign(source_id='TCGA')
              [['cohort_id', 'source_id', 'cohort_name']]
              .drop_duplicates())
    db.copy_from_df(cohort, 'cohort')

    patient = (pd.read_csv(patient_fpath)
               [['patient_id', 'cohort_id']]
               .drop_duplicates(subset=['patient_id']))
    db.copy_from_df(patient, 'patient')

    sample = (pd.read_csv(sample_fpath)
              [['sample_id', 'patient_id', 'sample_code', 'sample_type']]
              .drop_duplicates())
    db.copy_from_df(sample, 'sample')

    conn.close()


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
        .dropna(subset=['Wound Healing'])
        .melt(id_vars='patient_id', var_name='data_type', value_name='value')
    )

    df["unit"] = df["data_type"].map(lambda dt: IMMUNE_LANDSCAPE_UNITS[dt])

    # Split into numeric values and text values
    df['is_numeric'] = df['value'].map(is_numeric)
    df_numeric = df[df['is_numeric']]
    df_numeric['value'] = df_numeric['value'].map(float)
    df_text = df[~df['is_numeric']]

    # Load to database in respective tables
    conn = db.engine.connect()
    df_numeric = (df_numeric[['patient_id', 'data_type', 'unit', 'value']]
                  .drop_duplicates(subset=['patient_id', 'data_type'])
                  .dropna(subset=['value']))
    db.copy_from_df(df_numeric,  'patient_value')

    df_text = (df_text[['patient_id', 'data_type', 'unit', 'value']]
               .drop_duplicates(subset=['patient_id', 'data_type'])
               .dropna(subset=['value']))
    db.copy_from_df(df_text, 'patient_text_value')
    conn.close()


def load_tcia_patient(fpath=TCIA_PATIENT):
    df = (
        pd.read_csv(fpath, sep='\t', low_memory=False)
        .drop(['datasource', 'disease'], axis=1)
        .melt(id_vars='barcode', var_name='data_type', value_name='value')
        .rename(columns={'barcode': 'patient_id'}))
    df['data_type'] = df['data_type'].str.replace('clinical_data_', '')
    df['unit'] = 'clinical'

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


def load_tcia_pathways(up_fpath=TCIA_GSEA_ENRICHMENT,
                       down_fpath=TCIA_GSEA_DEPLETION):
    for fpath in up_fpath, down_fpath:
        df = (
            pd.read_csv(fpath, sep='\t')
            .drop(['disease'], axis=1)
            .rename(columns={
                'patients': 'patient_id',
                'cellType': 'data_type',
                'qValue < 1%Enriched': 'qvalue',
                'qValue < 1%Depleted': 'qvalue',
                'NES > 0': 'value'}))
        df = df[df['qvalue'] < 0.05]
        df['unit'] = 'normalized enrichment score'

        # Load to database in respective tables
        df = (df[['patient_id', 'data_type', 'unit', 'value']]
              .drop_duplicates(subset=['patient_id', 'data_type'])
              .dropna(subset=['value']))
        db.copy_from_df(df, 'patient_value')


def load_tcga_profile(data_type, fpath):
    if data_type == "copy number":
        cols = ["sample", "entrez_id", "data_type", "unit", "copy_number"]
        unit = "log2 ratio"
    elif data_type == "expression":
        cols = [
            "sample",
            "entrez_id",
            "data_type",
            "unit",
            "normalized_counts",
        ]
        unit = "normalized_counts"
    else:
        raise ValueError("Data type not recognized")

    db.load_sample_gene_values(fpath, data_type, cols, unit)


def parse_tcga_isoforms(fpath):
    mat = pd.read_csv(fpath, sep='\t', skiprows=2, header=None)
    header = pd.read_csv(fpath, sep='\t', nrows=0)
    mat.columns = header.columns

    df = (
        mat
        .rename(columns={'Hybridization REF': 'transcript_id'})
        .melt(
            id_vars=['transcript_id'],
            var_name='barcode',
            value_name='value')
    )
    return df


def load_tcga_isoforms(fpath, env=cfg['ENV']):
    df = (
        pd.read_csv(fpath)
        .rename(columns={
            'transcript_id': 'isoform_id',
            'rsem_normalized': 'value'})
    )
    df['sample_id'] = df['barcode'].map(lambda s: s[:15])
    df['unit'] = 'normalized_counts'
    df = df[['sample_id', 'isoform_id', 'unit', 'value']]
    df = df.drop_duplicates(subset=['sample_id', 'isoform_id'])

    if env == 'dev':
        df = df[df['isoform_id'].isin(cfg['TEST_ISOFORMS'])]

    db.copy_from_df(df, 'sample_isoform_value')


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

    df_numeric = df_numeric[['patient_id', 'data_type', 'unit', 'value']]
    db.copy_from_df(df_numeric, 'patient_value')
    df_text = df_text[['patient_id', 'data_type', 'unit', 'value']]
    db.copy_from_df(df_text, 'patient_text_value')


def load_tcga_mutation(fpath, env=cfg['ENV']):
    maf = pd.read_csv(fpath, sep='\t')
    if 'Protein_Change' in maf.columns:
        df = maf[
            [
                'Entrez_Gene_Id',
                'Tumor_Sample_Barcode',
                'Variant_Classification',
                'Variant_Type',
                'Protein_Change',
            ]
        ]
    elif 'AAChange' in maf.columns:
        df = maf[
            [
                'Entrez_Gene_Id',
                'Tumor_Sample_Barcode',
                'Variant_Classification',
                'Variant_Type',
                'AAChange',
            ]
        ]
    elif 'amino_acid_change':
        df = maf[
            [
                'Entrez_Gene_Id',
                'Tumor_Sample_Barcode',
                'Variant_Classification',
                'Variant_Type',
                'amino_acid_change',
            ]
        ]
    else:
        raise Exception(
            'MAF file should have either "Protein_Change", "AAChange", '
            'or "amino_acid_change" column'
        )
    df['sample_id'] = df['Tumor_Sample_Barcode'].map(lambda s: s[:15])
    df = df.drop('Tumor_Sample_Barcode', axis=1)
    df = df.rename(columns={
        'Entrez_Gene_Id': 'gene_id',
        'Variant_Type': 'variant type',
        'Variant_Classification': 'variant classification',
        'AAChange': 'AA change'})
    df = df[df['gene_id'] > 0]

    if env == 'dev':
        df = df[df['gene_id'].isin(TEST_GENES)]

    df = df.melt(id_vars=['sample_id', 'gene_id'],
                 var_name='data_type', value_name='value')
    df['unit'] = 'mutation'
    df = df.drop_duplicates(subset=['gene_id', 'sample_id', 'data_type'])
    df = df.dropna(subset=['value'])

    df = df[['sample_id', 'gene_id', 'data_type', 'unit', 'value']]
    db.copy_from_df(df, 'sample_gene_text_value')
