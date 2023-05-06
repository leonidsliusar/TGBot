"""migration_3

Revision ID: 0c5e591104dc
Revises: 6a7e93e93744
Create Date: 2023-05-04 14:24:56.466355

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Text

# revision identifiers, used by Alembic.
revision = '0c5e591104dc'
down_revision = '6a7e93e93744'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column('messages', 'message', type_=Text())

def downgrade():
    op.alter_column('messages', 'message', type_=sa.String())
