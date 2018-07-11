plot_tcga_by_cohort <- function(df) {
  ggplot(df, aes(x=cohort_id, y=log2(normalized_counts + 1), color=sample_type)) + 
    facet_grid(symbol ~ .) +
    geom_boxplot(fill=NA) +
    theme_bw() +
    theme(axis.text.x = element_text(angle=90, hjust=1, vjust=0)) +
    labs(
      x = '',
      y = 'log2 normalized counts'
    )
}

plot_expr_by_immune_subtype <- function(df) {
  ggplot(df, aes(x=immune_subtype, y=log2(normalized_counts + 1))) + 
    facet_grid(symbol ~ .) +
    geom_boxplot(fill=NA) +
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

plot_tcga_mutations <- function(df) {
  df %>%
    #group_by(cohort_id, symbol, `variant classification`) %>%
    #summarize(n_samples = n()) %>%
    ggplot(aes(x=cohort_id, fill=`variant classification`)) + 
      facet_grid(symbol ~ .) +
      geom_bar() +
      theme_bw() +
      theme(axis.text.x = element_text(angle=90, hjust=1, vjust=1)) +
      labs(
        x = '',
        y = 'Number of patients'
      )
}

plot_hpa_by_cell_type <- function(df) {
  ggplot(df, aes(x=cell_type_id, y=`detection level`)) + 
    facet_grid(symbol ~ .) +
    geom_point() +
    theme_bw() +
    theme(axis.text.x = element_text(angle=90, hjust=1, vjust=1)) +
    labs(
      x = '',
      y = 'Detection level'
    )
}