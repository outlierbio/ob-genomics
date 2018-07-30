library(dbplyr)
library(RPostgreSQL)
library(tidyverse)
library(tidyr)

source('creds.r')

# Connect to DB
db <- DBI::dbConnect(
  dbDriver('PostgreSQL'), 
  host=host,
  user=user,
  password=password,
  dbname=dbname
)

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

patient_immune_composition <- data_tbls$patient_value %>%
  filter(unit == 'fraction') %>%
  inner_join(patient, by='patient_id') %>%
  select(cohort_id, patient_id, component=data_type, fraction=value)

patient_signature_score <- data_tbls$patient_value %>%
  filter(unit == 'signature score') %>%
  inner_join(patient, by='patient_id') %>%
  select(cohort_id, patient_id, signature=data_type, signature_score=value)

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

all_clinical_attributes <- function() {
  c(
    patient_clinical_value %>%
      dplyr::select(data_type) %>%
      dplyr::distinct() %>%
      collect %>%
      .$data_type %>%
      as.character(),
    patient_clinical_text %>%
      dplyr::select(data_type) %>%
      dplyr::distinct() %>%
      collect %>%
      .$data_type %>%
      as.character())
}


all_components <- function() {
  patient_immune_composition %>%
    select(component) %>%
    distinct() %>%
    collect %>%
    .$component %>%
    as.character()
}

all_signatures <- function() {
  patient_signature_score %>%
    select(signature) %>%
    distinct() %>%
    collect %>%
    .$signature %>%
    as.character()
}

tcga_clinical_by_attr <- function(clinical_attr) {
  txt_clinical <- patient_clinical_text %>%
    filter(data_type == clinical_attr) %>%
    collect %>%
    spread(data_type, value)
  
  num_clinical <- patient_clinical_value %>%
    filter(data_type == clinical_attr) %>%
    collect %>%
    spread(data_type, value)
  
  rbind(txt_clinical, num_clinical)  # one of these should be empty
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

tcga_expr_immune_subtype_by_gene <- function(gene) {
  tcga_expr_by_gene(gene) %>%
    inner_join(patient_immune_subtype %>% collect)
}

tcga_expr_immune_composition_by_gene <- function(gene, comp) {
  df <- patient_immune_composition %>%
    filter(component %in% comp) %>%
    collect
  tcga_expr_by_gene(gene) %>%
    inner_join(df)
}

tcga_expr_signature_score_by_gene <- function(gene, sig) {
  scores <- patient_signature_score %>%
    filter(signature %in% sig) %>%
    collect
  tcga_expr_by_gene(gene) %>%
    inner_join(scores)
}

tcga_expr_pair_by_gene <- function(gene_x, gene_y) {
  df_x <- tcga_expr_by_gene(gene_x) %>%
    mutate(log2_counts = log2(normalized_counts + 1)) %>%
    spread(symbol, log2_counts) %>%
    select(-gene_id, -ensembl_id, -normalized_counts)
  df_y <- tcga_expr_by_gene(gene_y) %>%
    mutate(log2_counts = log2(normalized_counts + 1)) %>%
    spread(symbol, log2_counts) %>%
    select(-gene_id, -ensembl_id, -normalized_counts)
  df_x %>% inner_join(df_y)
}

tcga_expr_by_clinical_attr <- function(symbol, clinical_attr) {
  tcga_clinical_by_attr(clinical_attr) %>%
    inner_join(tcga_expr_by_gene(symbol)) %>%
    mutate(log2_counts = log2(normalized_counts + 1)) %>%
    spread(symbol, log2_counts)
}

gtex_expr_pair_by_gene <- function(gene_x, gene_y) {
  df_x <- gtex_expr_by_gene(gene_x) %>%
    mutate(log2_tpm = log2(median_tpm + 1)) %>%
    spread(symbol, log2_tpm) %>%
    select(-gene_id, -ensembl_id, -median_tpm)
  df_y <- gtex_expr_by_gene(gene_y) %>%
    mutate(log2_tpm = log2(median_tpm + 1)) %>%
    spread(symbol, log2_tpm) %>%
    select(-gene_id, -ensembl_id, -median_tpm)
  df_x %>% inner_join(df_y)
}

hpa_expr_pair_by_gene <- function(gene_x, gene_y) {
  df_x <- hpa_expr_by_gene(gene_x) %>%
    mutate(log2_tpm = log2(TPM + 1)) %>%
    spread(symbol, log2_tpm) %>%
    select(-gene_id, -ensembl_id, -TPM)
  df_y <- hpa_expr_by_gene(gene_y) %>%
    mutate(log2_tpm = log2(TPM + 1)) %>%
    spread(symbol, log2_tpm) %>%
    select(-gene_id, -ensembl_id, -TPM)
  df_x %>% inner_join(df_y)
}

