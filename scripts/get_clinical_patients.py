import pandas as pd
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

dfs = []
for cohort in cohorts:
    headers = pd.read_csv(f'{cohort}.clin.merged.picked.txt', sep='\t', nrows=0)
    patients = [pt.upper() for pt in headers.columns[1:]]
    df = pd.DataFrame({
        'cohort': cohort,
        'patient': patients
    })
    dfs.append(df)
pd.concat(dfs).to_csv('/Users/jfeala/reference/tcga/sample_meta/patient.clin.csv', index=False)