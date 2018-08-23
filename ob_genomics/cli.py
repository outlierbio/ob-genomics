import click

from ob_genomics.config import cfg
from ob_genomics import pipeline
from ob_genomics import database
from ob_genomics import tcga

REFERENCE = cfg['REFERENCE']


@click.group()
def cli():
    pass


@click.command()
def init():
    print('Dropping all tables')
    database.destroy()

    print('Creating tables')
    database.create()

    print('Loading genes')
    database.load_genes()

    print('Loading isoforms')
    database.load_isoforms()

    print('Loading tissues')
    database.load_tissues()

    print('Loading cell types')
    database.load_cell_types()

    print('Loading sources, samples, and cohorts')
    tcga.load_tcga_sample_meta()


@click.command()
def build():
    pipeline.build()


@click.command()
def test():
    pass


cli.add_command(init)
cli.add_command(build)
cli.add_command(test)
