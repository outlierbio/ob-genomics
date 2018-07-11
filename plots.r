plot_tcga_by_cohort <- function(df) {
  ggplot(df, aes(x=cohort_id, y=log2(normalized_counts + 1), color=sample_type)) + 
    facet_grid(symbol ~ .) +
    geom_boxplot(outlier.shape=NA, fill=NA) +
    theme_bw() +
    theme(axis.text.x = element_text(angle=90, hjust=1, vjust=0)) +
    labs(
      x = '',
      y = 'log2 normalized counts'
    )
}

plot_gtex_by_tissue <- function(df) {
  ggplot(df, aes(x=tissue_id, y=log2(median_tpm + 1))) + 
    facet_grid(symbol ~ .) +
    geom_point() +
    theme_bw() +
    theme(axis.text.x = element_text(angle=90, hjust=1, vjust=1)) +
    labs(
      x = '',
      y = 'log2 median TPM'
    )
}