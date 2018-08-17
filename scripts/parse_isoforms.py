import os
import pandas as pd


GDAC_DIR = '/reference/tcga/gdac'
# cohorts = os.listdir(GDAC_DIR + 'stddata__2016_07_15')
cohorts = [
 'ACC',
 'BLCA',
 'BRCA',
 'CESC',
 'CHOL',
 'COAD',
 'COADREAD',
 'DLBC',
 'ESCA',
 'GBM',
 'HNSC',
 'KICH',
 'KIRC',
 'KIRP',
 'LAML',
 'LGG',
 'LIHC',
 'LUAD',
 'LUSC',
 'MESO',
 'OV',
 'PAAD',
 'PCPG',
 'PRAD',
 'READ',
 'SARC',
 'SKCM',
 'STAD',
 'STES',
 'TGCT',
 'THCA',
 'THYM',
 'UCEC',
 'UCS',
 'UVM']


def parse_tcga_isoform(fpath):
    mat = pd.read_csv(fpath, sep='\t', skiprows=2, header=None)
    header = pd.read_csv(fpath, sep='\t', nrows=0)
    mat.columns = header.columns

    df = (
        mat
        .rename(columns={'Hybridization REF': 'transcript_id'})
        .melt(
            id_vars=['transcript_id'],
            var_name='barcode',
            value_name='rsem_normalized')
    )
    return df


for cohort in cohorts:
    if cohort == 'BRCA':
        fpath = GDAC_DIR + f'/stddata__2016_07_15/BRCA/20160715/gdac.broadinstitute.org_BRCA.Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_isoforms__data.Level_3.2016012800.0.0/BRCA.rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_isoforms__data.data.txt'
    else:
        fpath = GDAC_DIR + f'/stddata__2016_07_15/{cohort}/20160715/gdac.broadinstitute.org_{cohort}.Merge_rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_isoforms_normalized__data.Level_3.2016071500.0.0/{cohort}.rnaseqv2__illuminahiseq_rnaseqv2__unc_edu__Level_3__RSEM_isoforms_normalized__data.data.txt'

    if not os.path.exists(fpath):
        print(cohort, ' not available')
        continue

    print(f'Parsing {cohort}')
    df = parse_tcga_isoform(fpath)
    df.to_csv(GDAC_DIR + f'/tables/{cohort}.isoform.csv', index=False)
