import numpy as np
import pandas as pd
from ob_genomics.config import cfg


def summarize_gtex_isoform(
        data_fpath=cfg['GTEX_ISOFORM'],
        sample_fpath=cfg['GTEX_SAMPLE'],
        out_fpath=cfg['GTEX_MEDIAN_ISOFORM']):
    """Calculate median transcript value per tissue"""
    # Get metadata and create tissue ID ("<tissue> - <subtype>")
    meta = pd.read_csv(sample_fpath, sep='\t')[['SAMPID', 'SMTS', 'SMTSD']]
    meta.columns = ['sample_id', 'tissue', 'subtype']
    meta.loc[:, 'tissue_id'] = [f'{tissue} - {subtype}'
                                for tissue, subtype
                                in zip(meta['tissue'], meta['subtype'])]
    df = (
        pd.read_csv(data_fpath, sep='\t')
        .melt(id_vars=['transcript_id', 'gene_id'],
              var_name='sample_id', value_name='tpm')
        .rename(columns={'transcript_id': 'isoform_id'}))
    df.to_csv(cfg['GTEX_ISOFORM_TALL'], index=False)

        .merge(meta, on='sample_id')
        .groupby('tissue_id')
        .agg({'median_tpm': np.median})
    )
    df.write_csv(out_fpath, index=False)