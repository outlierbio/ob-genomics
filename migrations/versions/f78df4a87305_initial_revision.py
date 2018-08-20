"""Initial revision

Revision ID: f78df4a87305
Revises: 
Create Date: 2018-08-20 11:04:46.276923

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f78df4a87305'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Rename gene symbol index to auto-generated pattern
    op.create_index(op.f('ix_gene_symbol'), 'gene', ['symbol'], unique=False)
    op.drop_index('gene_symbol_idx', table_name='gene')


def downgrade():
    op.create_index('gene_symbol_idx', 'gene', ['symbol'])
    op.drop_index(op.f('ix_gene_symbol'), table_name='gene')
