# ob-genomics

Pipelines and ETL for aggregating public genomics data.

Installation
------------
From the ob-genomics directory,

	$ pip install -e .

## Set up a config file
To configure, make a file `config.yml` from the template:

	$ cp config-template.yml config.yml

Adjust paths to your temp folder, reference data folder, and database.


Usage
-----
## Create and populate the database
	$ ob-genomics init  # DELETES and creates a new database
	$ ob-genomics meta  # Loads gene, tissue, and sample metadata
	$ ob-genomics build  # Luigi pipeline for loading genomics data

## Start up the Shiny app
Start up the Shiny app from the Dockerfile.shiny image, mounting this directory and binding port 80.

	$ sh run_shiny.sh

## Connect to the database directly via R/dplyr
	> source('apps/genomics/database.r')
	> kras <- tcga_expr_by_gene('KRAS')
