library(dbplyr)
library(RSQLite)
library(tidyverse)
library(tidyr)

# Connect to DB and get tables
db <- DBI::dbConnect(RSQLite::SQLite(), 'ob_genomics.db')
gene <- tbl(db, 'gene')
patient <- tbl(db, 'patient')
tissue <- tbl(db, 'tissue')
sample <- tbl(db, 'sample') %>%
  inner_join(patient, by='patient_id')

immune_subtype <- tbl(db, 'patient_value') %>%
  filter(data_type == 'immune subtype') %>%
  inner_join(patient, by='patient_id') %>%
  select(cohort_id, patient_id, immune_subtype=value)

sample_expression <- tbl(db, 'sample_gene_value') %>%
  filter(data_type == 'expression') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(sample, by='sample_id') 

sample_copy_number <- tbl(db, 'sample_gene_value') %>%
  filter(data_type == 'copy number') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(sample, by='sample_id') 

tissue_expression <- tbl(db, 'tissue_gene_value') %>%
  inner_join(gene, by='gene_id') %>%
  inner_join(tissue, by='tissue_id') 