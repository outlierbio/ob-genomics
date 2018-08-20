import pandas as pd

from ob_genomics.config import cfg

TX_TO_GENE_FPATH = cfg['REFERENCE'] + '/tcga/rnaseqv2/unc_knownToLocus.txt'
OUT_FPATH = TX_TO_GENE_FPATH.replace('.txt', '.formatted.txt')

df = pd.read_csv(TX_TO_GENE_FPATH, sep='\t', header=False)
df.columns = ['mapping', 'isoform_id']

df['symbol'] = df['mapping'].map(
    lambda s: s.split('|')[0] if '|' in s else None)
df['gene_id'] = df['mapping'].map(
    lambda s: s.split('|')[1] if '|' in s else None)
df['source'] = 'UCSC knownGene'

df[['isoform_id', 'gene_id', 'source']].to_csv(OUT_FPATH, index=False)
