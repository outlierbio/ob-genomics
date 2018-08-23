import os
import os.path as op

import yaml

# All configuration is matched to an environment (ENV)
ENV = os.environ.get('ENV', 'test')

CONFIG_FILE = op.join(op.dirname(__file__), '..', 'config.yml')
with open(CONFIG_FILE) as f:
    cfg = yaml.load(f)[ENV]

# Expand reference and scratch folders if home or ~
REFERENCE = op.expanduser(cfg['REFERENCE'])
SCRATCH = op.expanduser(cfg['SCRATCH'])
cfg['REFERENCE'] = REFERENCE
cfg['SCRATCH'] = SCRATCH

# Add back the environment
cfg['ENV'] = ENV

# Test subsets
cfg['TEST_GENES'] = [3845, 7157, 4609, 2597]
cfg['TEST_SYMBOLS'] = ['GAPDH', 'MYC', 'KRAS', 'TP53']
#cfg['TEST_ENSEMBL_GENES'] = []
cfg['TEST_ISOFORMS'] = ['uc001aaa.3', 'uc001aab.3', 'uc001aac.3', 'uc001aae.3', 'uc001aah.3', 'uc001aai.1', 'uc001aak.2', 'uc001aal.1']


# Reference filepaths
cfg['TCGA'] = {
    
}
cfg['GTEX_TPM'] = op.join(
    REFERENCE, 'gtex',
    'GTEx_Analysis_2016-01-15_v7_RNASeQCv1.1.8_gene_tpm.gct')
cfg['GTEX_MEDIAN_TPM'] = op.join(
    REFERENCE, 'gtex',
    'GTEx_Analysis_2016-01-15_v7_RNASeQCv1.1.8_gene_median_tpm.gct')
cfg['GTEX_ISOFORM'] = op.join(
    REFERENCE, 'gtex',
    'GTEx_Analysis_2016-01-15_v7_RSEMv1.2.22_transcript_tpm.txt')
cfg['GTEX_ISOFORM_TALL'] = op.join(
    REFERENCE, 'gtex',
    'GTEx_Analysis_2016-01-15_v7_RSEMv1.2.22_transcript_tpm.tall.csv')
cfg['GTEX_MEDIAN_ISOFORM'] = op.join(
    REFERENCE, 'gtex',
    'GTEx_Analysis_2016-01-15_v7_RSEMv1.2.22_transcript_median_tpm.txt')
cfg['GTEX_SAMPLE'] = op.join(
    REFERENCE, 'gtex',
    'GTEx_v7_Annotations_SampleAttributesDS.txt')
