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


##########################
# Experimental data tables
# Think of these tables as the representing scientific observations from
# direct assay, and data derived directly from assays. These terms are meant to
# coincide with the general philosophy of scientific experimentation.

# In an experiment, one or more subjects are assayed to produce an observation.
# Multiple features (protocols for transcribing, interpreting, post-processing)
# can be applied to or derived from an observation, each
# resulting in a datapoint.

# In terms of data matrices, these can be mapped (roughly) to the dimensions of
# the matrix:
#   - Matrices: Assay
#   - Columns: Observation (Subject + Assay)
#   - Rows: Feature
#   - Cells: Datapoint
#
# For example, an expression matrix has
#   - Assay: RNA-sequencing run on a batch of samples
#   - Subject: cDNA library derived from an RNA aliquot
#   - Observation: reads from a sequencing run on a cDNA library
#   - Feature: read counts mapped to a genomic interval
#   - Datapoint: count values
#
# Some assays, e.g., clinical parameters like age, may have only one feature.
#

# Base for experimental entities
class Entity(base):
    __tablename__ = 'entity'
    entity_id = Column(Integer, primary_key=True)


class Assay(Entity):
    __tablename__ = 'assay'
    assay_id = Column(Integer, primary_key=True)


class Subject(Entity):
    __tablename__ = 'subject'
    subject_id = Column(Integer, primary_key=True)


class Observation(Entity):
    __tablename__ = 'observation'
    observation_id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey('subject.subject_id'),
                        primary_key=True)
    assay_id = Column(Integer, primary_key=True)


class Feature(Entity):
    __tablename__ = 'feature'
    feature_id = Column(Integer, primary_key=True)


class Datapoint(Entity):
    __tablename__ = 'datapoint'
    datapoint_id = Column(Integer, primary_key=True)
    feature_id = Column(Integer, ForeignKey('feature.feature_id'),
                        primary_key=True)
    observation_id = Column(Integer, ForeignKey('observation.observation_id'),
                            primary_key=True)


#####################
# Biological concepts
# These represent well-known biological concepts. They are abstract,
# or have complex or peripheral relationships to the experimental entities and
# to each other, therefore kept separate from experimental entities. They can
# have flexible and highly customized schemas, and can either inherit or link
# to experimental entities. Some could even be pulled into a separate database
# (e.g., NoSQL, RDF, etc) if they have fuzzier relationships.

class Concept(base):
    __tablename__ = 'concept'
    concept_id = Column(Integer, primary_key=True)


class EntityConcept(base):
    __tablename__ = 'entity_concept'
    entity_id = Column(Integer, primary_key=True)
    concept_id = Column(Integer, primary_key=True)


class Gene(Concept):
    __tablename__ = 'gene'
    gene_id = Column(Integer, primary_key=True)
    ensembl_id = Column(String)
    symbol = Column(String)


class GeneFeature(EntityConcept):
    __tablename__ = 'gene_feature'


class Source(Concept):
    __tablename__ = 'source'
    source_id = Column(String, primary_key=True)


class Cohort(Concept):
    __tablename__ = 'cohort'
    cohort_id = Column(String, primary_key=True)
    source_id = Column(String, ForeignKey('source.source_id'),
                       primary_key=True)


class Patient(Concept):
    __tablename__ = 'patient'
    patient_id = Column(String, primary_key=True)
    cohort_id = Column(String, ForeignKey('cohort.cohort_id'))


class PatientSubject(EntityConcept):
    __tablename__ = 'patient_subject'


class TissueSample(Concept):
    __tablename__ = 'tissue_sample'
    sample_id = Column(String, primary_key=True)
    patient_id = Column(String, ForeignKey('patient.patient_id'))
    sample_code = Column(String, nullable=False)
    sample_type = Column(String, nullable=False)


class TissueSampleSubject(EntityConcept):
    __tablename__ = 'tissue_sample_subject'


class Tissue(Concept):
    __tablename__ = 'tissue'
    tissue_id = Column(String, primary_key=True)
    tissue = Column(String, nullable=False)
    subtype = Column(String)
    gtex_id = Column(String)
    hpa_id = Column(String)


class TissueSubject(EntityConcept):
    __tablename__ = 'tissue_sample_subject'


class CellType(Concept):
    __tablename__ = 'cell_type'
    cell_type_id = Column(String, primary_key=True)
    tissue_id = Column(String, ForeignKey('tissue.tissue_id'))
    cell_type = Column(String, nullable=False)


class CellTypeSubject(EntityConcept):
    __tablename__ = 'cell_type_subject'


class CellLine(Concept):
    __tablename__ = 'cell_line'


class Pathway(Concept):
    __tablename__ = 'pathway'
    pathway_id = Column(String, primary_key=True)


class PathwayGene(base):
    __tablename__ = 'pathway'
    pathway_id = Column(String, primary_key=True)
    gene_id = Column(Integer, primary_key=True)


##############################
# Generalizable data entities
# (similar to Entity-Attribute-Value with foreign keys)

# Data is stored in E-A-V (entity-attribue-value) format, where an "entity"
# in this case means one of the dimensions. That way, any dimension can have
# flexible attributes. For example, clinical data is an attribute of a Patient
# Entity. Both TPM and counts can be attributes of a Measurement Datapoint.
# Genome change and protein change can be attributes of a Mutation Datapoint.

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
