"""empty message

Revision ID: f915d0f83cc6
Revises: 0f4a9de9279c
Create Date: 2022-08-07 17:54:12.480197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f915d0f83cc6'
down_revision = '0f4a9de9279c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('address', sa.String(length=120), nullable=True))
    op.add_column('artists', sa.Column('seeking_talent', sa.Boolean(), nullable=True))
    op.drop_column('artists', 'looking_for_talent')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artists', sa.Column('looking_for_talent', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.drop_column('artists', 'seeking_talent')
    op.drop_column('artists', 'address')
    # ### end Alembic commands ###