import os.path as op

import luigi
from luigi.contrib.s3 import S3Target
import pandas as pd

from ob_genomics.config import cfg
import ob_genomics.database as db
import ob_genomics.gtex as gtex
import ob_genomics.tcga as tcga

REFERENCE = cfg['REFERENCE']


class DatabaseTarget(luigi.Target):
    def __init__(self, table, update_id):
        """
        Args:
            update_id (str): An identifier for this data set
        """
        self.table = table
        self.update_id = update_id

    def touch(self, connection=None):
        """Mark this update as complete."""
        conn = db.engine.connect()
        conn.execute(f'''
            INSERT INTO table_updates (update_id, target_table)
            VALUES ('{self.update_id}', '{self.table}')
        ''')
        conn.close()

    def exists(self):
        conn = db.engine.connect()
        res = conn.execute(f'''
            SELECT 1 FROM table_updates
            WHERE update_id = '{self.update_id}'
            LIMIT 1
        ''')
        row = res.fetchone()
        conn.close()

        return row is not None


class DownloadGDAC(luigi.Task):

    data_type = luigi.Parameter()
    cohort = luigi.Parameter()

    def run(self):
        tcga.download_gdac(self.data_type, self.cohort)

    def output(self):
        fpath = f'{folder}/*{self.data_type}*./{self.cohort}'
        return luigi.LocalTarget(fpath)


class BuildGDACTable(luigi.Task):

    data_type = luigi.Parameter()
    cohort = luigi.Parameter()

    def requires(self):
        return DownloadGDAC()

    def run(self):
        with self.input().open() as f:
            tcga.gdac_to_table(f)

    def output(self):
        dt_string = {
            'expression': 'rsem_normalized',
            'copy number': 'copy_number'
        }[self.data_type]
        path = f'{REFERENCE}/tcga/gdac/tables/{self.cohort}.{dt_string}.csv'
        return luigi.LocalTarget(path)
        # return S3Target(s3_path)


class LoadTCGASampleMeta(luigi.Task):
    def run(self):
        tcga.load_tcga_sample_meta()
        self.output().touch()

    def output(self):
        return DatabaseTarget('cohort,patient,sample', 'TCGA sample metadata')


class LoadImmuneLandscape(luigi.Task):

    def requires(self):
        return LoadTCGASampleMeta()

    def run(self):
        db.load_immune_value('Immune Subtype')


class LoadTCGAProfile(luigi.Task):

    data_type = luigi.Parameter()
    cohort = luigi.Parameter()

    def requires(self):
        return (LoadTCGASampleMeta(),
                BuildGDACTable(data_type=self.data_type, cohort=self.cohort))

    def run(self):
        _, table = self.input()
        tcga.load_tcga_profile(self.data_type, table.path)
        self.output().touch()

    def output(self):
        update_id = f'{self.cohort} {self.data_type}'
        return DatabaseTarget('sample_gene_value', update_id)


class LoadTCGA(luigi.Task):
    def requires(self):
        cohorts = pd.read_csv(tcga.TCGA_COHORT_META)['cohort_id']
        for cohort in cohorts:
            if cohort in ['LCML', 'FPPP', 'CNTL', 'MISC']:
                continue
            yield LoadTCGAProfile(data_type='copy number', cohort=cohort)
            yield LoadTCGAProfile(data_type='expression', cohort=cohort)


class LoadGTExMedian(luigi.Task):
    def run(self):
        gtex.load_gtex_median_tpm()
        self.output().touch()

    def output(self):
        return DatabaseTarget('tissue_gene_value', 'GTEx median')


def build():
    luigi.build([
        LoadTCGA(),
        LoadGTExMedian()
    ], local_scheduler=True)
