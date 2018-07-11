# ob-genomics

Pipelines and ETL for aggregating public genomics data.

Usage
-----

## Create and populate the database
	$ ob-genomics init
	$ ob-genomics build

## Start up the Shiny app
	$ ob-genomics shiny

## Connect to the data via R/dplyr
	> source('database.r')
	> kras <- expression %>%
	>     filter(symbol == 'KRAS')

Installation
------------
From the ob-genomics directory,

	$ pip install -e .

To configure, open `config.yml` and point to your reference data folder (S3 buckets are ok) and the database URI