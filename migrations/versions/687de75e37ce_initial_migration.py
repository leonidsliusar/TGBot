"""initial migration

Revision ID: 687de75e37ce
Revises: 
Create Date: 2023-05-01 11:21:23.383416

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '687de75e37ce'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chats',
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('chat_id')
    )
    op.create_table('messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('chat_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.chat_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('messages')
    op.drop_table('chats')
    # ### end Alembic commands ###
