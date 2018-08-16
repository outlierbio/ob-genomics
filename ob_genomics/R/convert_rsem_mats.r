library(tidyverse)
mats <- readRDS('/reference/tcga/rsem_normalized.rds')

# RSEM
cohorts <- names(mats)
for (cohort in cohorts) {
  mats[[cohort]] %>%
    gather(barcode, normalized_counts, -gene_symbol, -entrez_id) %>%
    mutate(
      sample = substr(barcode, 1, 15),
      patient = substr(barcode, 1, 12)
    ) %>%
    select(entrez_id, gene_symbol, patient, sample, barcode, normalized_counts) %>%
    write_csv(paste0('/reference/tcga/gdac/tables/', cohort, '.rsem_normalized.csv'))
}

# CNA by gene
for (cohort in cohorts) {
  read_tsv(paste0('/reference/tcga/gistic_genes/', 
                  cohort, '.all_data_by_genes.txt')) %>%
    gather(barcode, copy_number, -`Gene Symbol`, -`Locus ID`, -`Cytoband`) %>%
    mutate(
      sample = substr(barcode, 1, 15),
      patient = substr(barcode, 1, 12)
    ) %>%
    select(entrez_id=`Locus ID`, gene_symbol=`Gene Symbol`, cytoband=`Cytoband`,
           patient, sample, barcode, copy_number) %>%
    write_csv(paste0('/reference/tcga/gdac/tables/', cohort, '.copy_number.csv'))
}


meta_dfs = list()
for (cohort in cohorts) {
  cn_pts <- read_csv(paste0('/reference/tcga/gdac/tables/', cohort, '.copy_number.csv')) %>%
    select(patient, sample, barcode)
  expr_pts <- read_csv(paste0('/reference/tcga/gdac/tables/', cohort, '.rsem_normalized.csv')) %>%
    select(patient, sample, barcode)
  pts <- rbind(cn_pts, expr_pts) %>%
    unique %>%
    mutate(cohort = cohort) %>%
    select(cohort, patient, sample, barcode)
  meta_dfs[[cohort]] = pts
}
meta <- do.call('rbind', meta_dfs)
meta %>% 
  mutate(
    sample_code = substr(sample, 14, 16),
    sample_type = factor(sample_code < 10, levels=c(FALSE, TRUE), labels=c('normal', 'tumor'))
  ) %>%
  write_csv(paste0('/reference/tcga/sample_meta.csv'))
