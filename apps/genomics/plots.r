plot_tcga_by_cohort <- function(df) {
  print(df)
  ggplot(
    df,
    aes(x = cohort_id, y = log2(normalized_counts + 1), color = sample_type)
  ) +
    facet_grid(symbol ~ .) +
    geom_boxplot(fill = NA) +
    theme_bw() +
    theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0)) +
    labs(
      x = "",
      y = "log2 normalized counts"
    )
}

plot_tcga_expr_immune_subtype <- function(df) {
  ggplot(
    df,
    aes(x = immune_subtype, y = log2(normalized_counts + 1))
  ) +
    facet_grid(symbol ~ .) +
    geom_boxplot(fill = NA) +
    theme_bw() +
    theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 0)) +
    labs(
      x = "",
      y = "log2 normalized counts"
    )
}

plot_tcga_expr_immune_composition <- function(df) {
  ggplot(
    df,
    aes(x = fraction, y = log2(normalized_counts + 1), color = cohort_id)
  ) +
    facet_grid(symbol ~ component, scales = "free") +
    geom_point() +
    theme_bw() +
    labs(
      x = "tumor fraction",
      y = "log2 normalized counts"
    )
}

plot_tcga_expr_signature_score <- function(df) {
  ggplot(
    df,
    aes(x = signature_score, y = log2(normalized_counts + 1), color = cohort_id)
  ) +
    facet_grid(symbol ~ signature, scales = "free") +
    geom_point() +
    theme_bw() +
    labs(
      x = "signature score",
      y = "log2 normalized counts"
    )
}

plot_gtex_by_tissue <- function(df) {
  ggplot(
    df,
    aes(x = tissue_id, y = log2(median_tpm + 1))
  ) +
    facet_grid(symbol ~ .) +
    geom_point() +
    theme_bw() +
    theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 1)) +
    labs(
      x = "",
      y = "log2 median TPM"
    )
}

plot_tcga_mutations <- function(df) {
  df %>%
    ggplot(aes(x = cohort_id, fill = `variant classification`)) +
    facet_grid(symbol ~ .) +
    geom_bar() +
    theme_bw() +
    theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 1)) +
    labs(
      x = "",
      y = "Number of patients"
    )
}

plot_hpa_by_cell_type <- function(df) {
  ggplot(df, aes(x = cell_type_id, y = `detection level`)) +
    facet_grid(symbol ~ .) +
    geom_point() +
    theme_bw() +
    theme(axis.text.x = element_text(angle = 90, hjust = 1, vjust = 1)) +
    labs(
      x = "",
      y = "Detection level"
    )
}

plot_gtex_vs_hpa <- function(df) {
  ggplot(df, aes(x = log2(GTEx + 1), y = log2(HPA + 1), color = tissue)) +
    facet_wrap(~symbol, scales = "free") +
    geom_point(aes(text = paste0(tissue, " - ", subtype))) +
    theme_bw() +
    theme(
      axis.text.x = element_text(angle = 90, hjust = 1, vjust = 1),
      legend.position = "none"
    ) +
    labs(
      x = "GTEx expression (median TPM)",
      y = "HPA expression (TPM)"
    )
}


plot_hpa_prot_vs_expr <- function(df) {
  ggplot(df, aes(x = `detection level`, y = log2(TPM + 1), color = tissue)) +
    facet_wrap(~symbol, scales = "free") +
    geom_point(aes(text = paste0(tissue, " - ", subtype))) +
    theme_bw() +
    theme(
      axis.text.x = element_text(angle = 90, hjust = 1, vjust = 1),
      legend.position = "none"
    ) +
    labs(
      x = "HPA protein level",
      y = "HPA expression (TPM)"
    )
}

plot_tcga_expr_pair <- function(df, gene_x, gene_y) {
  ggplot(
    df,
    aes(x = get(gene_x), y = (gene_y), color = cohort_id, shape = sample_type)
  ) +
    geom_point(aes(text = paste0(cohort_id, ": ", sample_id)), alpha = 0.5) +
    theme_bw() +
    theme(
      axis.text.x = element_text(angle = 90, hjust = 1, vjust = 1),
      legend.position = "none"
    ) +
    labs(
      x = paste0(gene_x, " log2(normalized counts)"),
      y = paste0(gene_y, " log2(normalized counts)")
    )
}

plot_tcga_expr_by_clinical <- function(df, gene, clinical_attr) {
  p <- ggplot(df, aes(x = get(clinical_attr), y = get(gene)), color = cohort_id)
  if (class(df[[clinical_attr]]) == "character") {
    p <- p + geom_boxplot() +
      geom_jitter(
        alpha = 0.5,
        position = position_jitter(width = 0.1, height = 0)
      )
  } else {
    p <- p + geom_point(
      aes(text = paste0(cohort_id, ": ", patient_id)),
      alpha = 0.5
    )
  }

  p + theme_bw() +
    theme(
      axis.text.x = element_text(angle = 90, hjust = 1, vjust = 1),
      legend.position = "none"
    ) +
    labs(
      x = clinical_attr,
      y = paste0(gene, " log2(normalized counts)")
    )
}

plot_gtex_expr_pair <- function(df, gene_x, gene_y) {
  ggplot(df, aes(x = get(gene_x), y = get(gene_y), color = tissue_id)) +
    geom_point(aes(text = paste0(tissue, ": ", subtype)), alpha = 0.5) +
    theme_bw() +
    theme(
      axis.text.x = element_text(angle = 90, hjust = 1, vjust = 1),
      legend.position = "none"
    ) +
    labs(
      x = paste0(gene_x, " log2(median TPM)"),
      y = paste0(gene_y, " log2(median TPM)")
    )
}

plot_hpa_expr_pair <- function(df, gene_x, gene_y) {
  ggplot(df, aes(x = get(gene_x), y = get(gene_y), color = tissue)) +
    geom_point(aes(text = paste0(tissue, ": ", subtype)), alpha = 0.5) +
    theme_bw() +
    theme(
      axis.text.x = element_text(angle = 90, hjust = 1, vjust = 1),
      legend.position = "none"
    ) +
    labs(
      x = paste0(gene_x, " log2(TPM)"),
      y = paste0(gene_y, " log2(TPM)")
    )
}
