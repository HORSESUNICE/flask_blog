"""fake post

Revision ID: d77b7a980621
Revises: 97e8a66d87c5
Create Date: 2017-06-18 20:24:18.982225

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd77b7a980621'
down_revision = '97e8a66d87c5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('title', sa.String(length=32), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'title')
    # ### end Alembic commands ###
