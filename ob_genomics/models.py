from sqlalchemy import (Column, ForeignKey, Integer, Numeric, String,
                        Text, DateTime)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base


base = declarative_base()


class TableUpdates(base):
    __tablename__ = 'table_updates'
    update_id = Column(String, primary_key=True)
    target_table = Column(String)
    inserted = Column(DateTime(timezone=True), server_default=func.now())


class Gene(base):
    __tablename__ = 'gene'
    gene_id = Column(Integer, primary_key=True)
    ensembl_id = Column(String)
    symbol = Column(String)


class Source(base):
    __tablename__ = 'source'
    source_id = Column(String, primary_key=True)


class Cohort(base):
    __tablename__ = 'cohort'
    cohort_id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey('source.source_id'),
                       primary_key=True)


class Patient(base):
    __tablename__ = 'patient'
    patient_id = Column(String, primary_key=True)
    cohort_id = Column(String, ForeignKey('cohort.cohort_id'))


class Sample(base):
    __tablename__ = 'sample'
    sample_id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey('patient.patient_id'))
    sample_code = Column(String, nullable=False)
    sample_type = Column(String, nullable=False)


class Tissue(base):
    __tablename__ = 'tissue'
    tissue_id = Column(String, primary_key=True)
    tissue = Column(String, nullable=False)
    subtype = Column(String)
    gtex_id = Column(String)
    hpa_id = Column(String)


class CellType(base):
    __tablename__ = 'cell_type'
    cell_type_id = Column(String, primary_key=True)
    tissue_id = Column(String, ForeignKey('tissue.tissue_id'))
    cell_type = Column(String, nullable=False)


class Pathway(base):
    __tablename__ = 'pathway'
    pathway_id = Column(String, primary_key=True)


##############################
# Generalizable data entities
# (similar to Entity-Attribute-Value with foreign keys)

class PatientValue(base):
    __tablename__ = 'patient_value'
    patient_id = Column(String, ForeignKey('patient.patient_id'),
                        primary_key=True)
    data_type = Column(String, primary_key=True)
    unit = Column(String)
    value = Column(Numeric, nullable=False)


class PatientTextValue(base):
    __tablename__ = 'patient_text_value'
    patient_id = Column(String, ForeignKey('patient.patient_id'),
                        primary_key=True)
    data_type = Column(String, primary_key=True)
    unit = Column(String)
    value = Column(String, nullable=False)


class SampleGeneValue(base):
    __tablename__ = 'sample_gene_value'
    sample_id = Column(String, ForeignKey('sample.sample_id'),
                       primary_key=True)
    gene_id = Column(String, ForeignKey('gene.gene_id'), primary_key=True)
    data_type = Column(String, primary_key=True)
    unit = Column(String)
    value = Column(Numeric, nullable=False)


class SampleGeneTextValue(base):
    __tablename__ = 'sample_gene_text_value'
    sample_id = Column(String, ForeignKey('sample.sample_id'),
                       primary_key=True)
    gene_id = Column(String, ForeignKey('gene.gene_id'), primary_key=True)
    data_type = Column(String, primary_key=True)
    unit = Column(String)
    value = Column(String, nullable=False)


class TissueGeneValue(base):
    __tablename__ = 'tissue_gene_value'
    source_id = Column(String, ForeignKey('source.source_id'),
                       primary_key=True)
    tissue_id = Column(String, ForeignKey('tissue.tissue_id'),
                       primary_key=True)
    gene_id = Column(String, ForeignKey('gene.gene_id'), primary_key=True)
    data_type = Column(String, primary_key=True)
    unit = Column(String)
    value = Column(Numeric, nullable=False)


class CellTypeGeneTextValue(base):
    __tablename__ = 'cell_type_gene_text_value'
    source_id = Column(String, ForeignKey('source.source_id'),
                       primary_key=True)
    cell_type_id = Column(String, ForeignKey('cell_type.cell_type_id'),
                          primary_key=True)
    gene_id = Column(String, ForeignKey('gene.gene_id'), primary_key=True)
    data_type = Column(String, primary_key=True)
    unit = Column(String)
    value = Column(String, nullable=False)
