import os.path as op

import luigi
from luigi import Task, Parameter, Target, LocalTarget
from luigi.contrib.s3 import S3Target
import pandas as pd

from ob_genomics.config import cfg
import ob_genomics.database as db
import ob_genomics.gtex as gtex
import ob_genomics.hpa as hpa
import ob_genomics.tcga as tcga

REFERENCE = cfg['REFERENCE']
SCRATCH = cfg['SCRATCH']

ReferenceTarget = S3Target if REFERENCE.startswith('s3://') else LocalTarget


class DatabaseTarget(Target):
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


class DownloadGDAC(Task):

    data_type = Parameter()
    cohort = Parameter()

    def run(self):
        tcga.download_gdac(self.data_type, self.cohort)

    def output(self):
        fpath = f'{folder}/*{self.data_type}*./{self.cohort}'
        return ReferenceTarget(fpath)


class BuildGDACTable(Task):

    data_type = Parameter()
    cohort = Parameter()

    def requires(self):
        return DownloadGDAC()

    def run(self):
        with self.input().open() as f:
            tcga.gdac_to_table(f)

    def output(self):
        suffix = tcga.gdac_params[self.data_type]['suffix']
        path = f'{REFERENCE}/tcga/gdac/tables/{self.cohort}.{suffix}'
        return ReferenceTarget(path)


class LoadTCGAClinical(Task):

    cohort = Parameter()

    def requires(self):
        return (LoadTCGASampleMeta(),
                BuildGDACTable(data_type='clinical', cohort=self.cohort))

    def run(self):
        _, table = self.input()
        tcga.load_tcga_clinical(table.path)
        self.output().touch()

    def output(self):
        update_id = f'TCGA {self.cohort} clinical'
        return DatabaseTarget('patient_value,patient_text_value', update_id)


class LoadTCGASampleMeta(Task):
    def run(self):
        tcga.load_tcga_sample_meta()
        self.output().touch()

    def output(self):
        return DatabaseTarget('cohort,patient,sample', 'TCGA sample metadata')


class LoadImmuneLandscape(Task):

    def requires(self):
        return LoadTCGASampleMeta()

    def run(self):
        tcga.load_immune_value('Immune Subtype')
        self.output().touch()

    def output(self):
        return DatabaseTarget('patient_value', 'immune subtype')


class LoadTCGAMutation(Task):

    cohort = Parameter()

    def requires(self):
        return (LoadTCGASampleMeta(),
                BuildGDACTable(data_type='mutation', cohort=self.cohort))

    def run(self):
        _, table = self.input()
        tcga.load_tcga_mutation(table.path)
        self.output().touch()

    def output(self):
        update_id = f'TCGA {self.cohort} mutation'
        return DatabaseTarget('sample_gene_value', update_id)


class LoadTCGAProfile(Task):

    data_type = Parameter()
    cohort = Parameter()

    def requires(self):
        return (LoadTCGASampleMeta(),
                BuildGDACTable(data_type=self.data_type, cohort=self.cohort))

    def run(self):
        _, table = self.input()
        tcga.load_tcga_profile(self.data_type, table.path)
        self.output().touch()

    def output(self):
        update_id = f'TCGA {self.cohort} {self.data_type}'
        return DatabaseTarget('sample_gene_value', update_id)


class LoadTCGA(Task):
    def requires(self):
        if cfg['ENV'] == 'test':
            cohorts = ['ACC', 'CHOL', 'DLBC']
        else:
            cohorts = pd.read_csv(tcga.TCGA_COHORT_META)['cohort_id']

        for cohort in cohorts:
            if cohort in ['LCML', 'FPPP', 'CNTL', 'MISC']:
                continue
            yield LoadTCGAClinical(cohort=cohort)
            yield LoadTCGAMutation(cohort=cohort)
            yield LoadTCGAProfile(data_type='copy number', cohort=cohort)
            yield LoadTCGAProfile(data_type='expression', cohort=cohort)


class LoadGTEx(Task):
    def run(self):
        gtex.load_gtex_median_tpm()
        self.output().touch()

    def output(self):
        return DatabaseTarget('tissue_gene_value', 'GTEx median')


class LoadHPAProtein(Task):
    def run(self):
        hpa.load_hpa_protein()
        self.output().touch()

    def output(self):
        return DatabaseTarget('cell_type_gene_text_value', 'HPA proteomics')


class LoadHPAExpression(Task):
    def run(self):
        hpa.load_hpa_expression()
        self.output().touch()

    def output(self):
        return DatabaseTarget('tissue_gene_value', 'HPA expression')


def build():
    luigi.build([
        LoadTCGASampleMeta(),
        LoadTCGA(),
        LoadImmuneLandscape(),
        LoadGTEx(),
        LoadHPAProtein(),
        LoadHPAExpression()
    ], local_scheduler=True)
