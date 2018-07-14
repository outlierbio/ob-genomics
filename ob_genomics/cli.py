import click

from ob_genomics.config import cfg
from ob_genomics import pipeline
from ob_genomics import database

REFERENCE = cfg['REFERENCE']


@click.group()
def cli():
    pass


@click.command()
def init():
    database.init_db()
    database.load_genes()
    database.load_tissues()
    database.load_cell_types()


@click.command()
def build():
    pipeline.build()


@click.command()
def test():
    pass


cli.add_command(init)
cli.add_command(build)
cli.add_command(test)
