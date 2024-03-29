"""empty message

Revision ID: be9d1ecd987c
Revises: None
Create Date: 2017-12-23 22:20:10.920359

"""

# revision identifiers, used by Alembic.
revision = 'be9d1ecd987c'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('type')
    # ### end Alembic commands ###
