library(dbplyr)
library(RSQLite)
library(tidyverse)
library(tidyr)

# Connect to DB
db <- DBI::dbConnect(RSQLite::SQLite(), 'ob_genomics.db')

###############
# Entity tables

gene <- tbl(db, 'gene')
cohort <- tbl(db, 'cohort')
patient <- tbl(db, 'patient') %>%
  inner_join(cohort, by='cohort_id')
tissue <- tbl(db, 'tissue')
cell_type <- tbl(db, 'cell_type') %>%
  inner_join(tissue, by='tissue_id')
sample <- tbl(db, 'sample') %>%
  inner_join(patient, by='patient_id')


#############
# Data tables

data_tbls <- list(
  patient_text_value = tbl(db, 'patient_text_value'),
  patient_value = tbl(db, 'patient_value'),
  sample_gene_value = tbl(db, 'sample_gene_value'),
  sample_gene_text_value = tbl(db, 'sample_gene_text_value'),
  tissue_gene_value = tbl(db, 'tissue_gene_value'),
  cell_type_gene_text_value = tbl(db, 'cell_type_gene_text_value')
)


################
# Derived tables

patient_immune_subtype <- data_tbls$patient_text_value %>%
  filter(data_type == 'Immune Subtype') %>%
  inner_join(patient, by='patient_id') %>%
  select(cohort_id, patient_id, immune_subtype=value)

patient_clinical_text <- data_tbls$patient_text_value %>%
  filter(unit == 'clinical') %>%
  inner_join(patient, by='patient_id')

patient_clinical_value <- data_tbls$patient_value %>%
  filter(unit == 'clinical') %>%
  inner_join(patient, by='patient_id')

sample_expression <- data_tbls$sample_gene_value %>%
  filter(data_type == 'expression') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(sample, by='sample_id') 

sample_copy_number <- data_tbls$sample_gene_value %>%
  filter(data_type == 'copy number') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(sample, by='sample_id') 

sample_mutation <- data_tbls$sample_gene_text_value %>%
  filter(unit == 'mutation') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(sample, by='sample_id')

tissue_expression <- data_tbls$tissue_gene_value %>%
  filter(data_type == 'expression') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(tissue, by='tissue_id') 

cell_type_protein <- data_tbls$cell_type_gene_text_value %>%
  filter(data_type == 'protein') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(cell_type, by='cell_type_id')


#######################
# Data access functions

get_tcga_clinical <- function() {
  txt_pivoted <- data_tbls$patient_clinical_text %>%
    collect %>%
    spread(data_type, value)
  
  num_pivoted <- data_tbls$patient_clinical_value %>%
    collect %>%
    spread(data_type, value)
  
  txt_pivoted %>%
    inner_join(num_pivoted)
}

tcga_expr_by_gene <- function(gene) {
  sample_expression %>%
    filter(symbol %in% gene) %>%
    collect %>%
    spread(unit, value)
}

gtex_expr_by_gene <- function(gene) {
  tissue_expression %>%
    filter(symbol %in% gene, source_id == 'GTEx') %>%
    collect %>%
    spread(unit, value)
}

hpa_expr_by_gene <- function(gene) {
  tissue_expression %>%
    filter(symbol %in% gene, source_id == 'HPA') %>%
    collect %>%
    spread(unit, value)
}

hpa_prot_by_gene <- function(gene) {
  cell_type_protein %>%
    filter(symbol %in% gene) %>%
    collect %>%
    spread(unit, value) %>%
    mutate(
      `detection level` = factor(`detection level`,
                                 levels=c('Not detected', 'Low', 'Medium', 'High')))
}

gtex_vs_hpa_by_gene <- function(gene) {
  hpa <- hpa_expr_by_gene(gene) %>% 
    select(tissue, subtype, symbol, HPA = TPM)
  gtex_expr_by_gene(gene) %>%
    select(tissue, subtype, symbol, GTEx = median_tpm) %>%
    inner_join(hpa)
}

hpa_prot_vs_expr_by_gene <- function(gene) {
  prot <- hpa_prot_by_gene(gene) %>%
    select(tissue, subtype, symbol, cell_type_id, `detection level`)
  hpa_expr_by_gene(gene) %>%
    select(tissue, subtype, symbol, TPM) %>%
    inner_join(prot)
}

tcga_mut_by_gene <- function(gene) {
  sample_mutation %>%
    filter(symbol %in% gene) %>%
    collect %>%
    spread(data_type, value)
}

expr_immune_subtype_by_gene <- function(gene) {
  tcga_expr_by_gene(gene) %>%
    inner_join(patient_immune_subtype %>% collect)
}