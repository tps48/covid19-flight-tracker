"""empty message

Revision ID: 707e10d65688
Revises: 934bff66a118
Create Date: 2020-10-12 22:52:52.212050

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '707e10d65688'
down_revision = '934bff66a118'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('route',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('source_airport_id', sa.Integer(), nullable=True),
    sa.Column('dest_airport_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['dest_airport_id'], ['airport.id'], ),
    sa.ForeignKeyConstraint(['source_airport_id'], ['airport.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('route')
    # ### end Alembic commands ###
