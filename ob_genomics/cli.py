import os.path as op
import click

from ob_genomics.config import cfg
from ob_genomics import pipeline
from ob_genomics import database
from ob_genomics import gtex
from ob_genomics import tcga

REFERENCE = cfg['REFERENCE']

@click.group()
def cli():
    pass


@click.command()
def init():
    database.init_db()
    database.load_genes()
    database.load_tissues()


@click.command()
def build():
    pipeline.build()


@click.command()
def test():
    gtex.load_gtex_median_tpm()

    tcga.load_tcga_sample_meta()
    tcga.load_tcga_profile(
        'expression',
        op.join(REFERENCE, 'tcga', 'gdac', 'tables', 'ACC.rsem_normalized.csv')
    )


cli.add_command(init)
cli.add_command(build)
cli.add_command(test)
