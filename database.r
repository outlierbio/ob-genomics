library(dbplyr)
library(RSQLite)
library(tidyverse)
library(tidyr)

# Connect to DB and get tables

# Entity tables
db <- DBI::dbConnect(RSQLite::SQLite(), 'ob_genomics.db')
gene <- tbl(db, 'gene')
cohort <- tbl(db, 'cohort')
patient <- tbl(db, 'patient') %>%
  inner_join(cohort, by='cohort_id')
tissue <- tbl(db, 'tissue')
cell_type <- tbl(db, 'cell_type') %>%
  inner_join(tissue, by='tissue_id')
sample <- tbl(db, 'sample') %>%
  inner_join(patient, by='patient_id')

# Data tables
patient_immune_subtype <- tbl(db, 'patient_text_value') %>%
  filter(data_type == 'immune subtype') %>%
  inner_join(patient, by='patient_id') %>%
  select(cohort_id, patient_id, immune_subtype=value)

patient_clinical_text <- tbl(db, 'patient_text_value') %>%
  filter(unit == 'clinical') %>%
  inner_join(patient, by='patient_id')

patient_clinical_value <- tbl(db, 'patient_value') %>%
  filter(unit == 'clinical') %>%
  inner_join(patient, by='patient_id')

sample_expression <- tbl(db, 'sample_gene_value') %>%
  filter(data_type == 'expression') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(sample, by='sample_id') 

sample_copy_number <- tbl(db, 'sample_gene_value') %>%
  filter(data_type == 'copy number') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(sample, by='sample_id') 

sample_mutation <- tbl(db, 'sample_gene_text_value') %>%
  filter(unit == 'mutation') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(sample, by='sample_id')

tissue_expression <- tbl(db, 'tissue_gene_value') %>%
  filter(data_type == 'expression') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(tissue, by='tissue_id') 

cell_type_protein <- tbl(db, 'cell_type_gene_text_value') %>%
  filter(data_type == 'protein') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(cell_type, by='cell_type_id')

tcga_clinical <- {
  txt_pivoted <- patient_clinical_text %>%
    collect %>%
    spread(data_type, value)
  
  num_pivoted <- patient_clinical_value %>%
    collect %>%
    spread(data_type, value)
  
  txt_pivoted %>%
    inner_join(num_pivoted)
}
