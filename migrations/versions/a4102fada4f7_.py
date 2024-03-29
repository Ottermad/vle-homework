"""empty message

Revision ID: a4102fada4f7
Revises: be9d1ecd987c
Create Date: 2017-12-23 22:24:17.213581

"""

# revision identifiers, used by Alembic.
revision = 'a4102fada4f7'
down_revision = 'be9d1ecd987c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('homework',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lesson_id', sa.Integer(), nullable=True),
    sa.Column('title', sa.String(length=200), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.Column('date_due', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('submission',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('homework_id', sa.Integer(), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('datetime_submitted', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['homework_id'], ['homework.id'], ),
    sa.ForeignKeyConstraint(['type_id'], ['type.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('comment',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('submission_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.ForeignKeyConstraint(['submission_id'], ['submission.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('comment')
    op.drop_table('submission')
    op.drop_table('homework')
    # ### end Alembic commands ###
