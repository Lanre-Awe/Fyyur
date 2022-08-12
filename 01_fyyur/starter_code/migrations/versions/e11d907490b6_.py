"""empty message

Revision ID: e11d907490b6
Revises: 20ae7acd5b8e
Create Date: 2022-08-08 15:34:02.952028

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e11d907490b6'
down_revision = '20ae7acd5b8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'shows', 'venues', ['venue_id'], ['id'])
    op.create_foreign_key(None, 'shows', 'artists', ['artist_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'shows', type_='foreignkey')
    op.drop_constraint(None, 'shows', type_='foreignkey')
    # ### end Alembic commands ###
