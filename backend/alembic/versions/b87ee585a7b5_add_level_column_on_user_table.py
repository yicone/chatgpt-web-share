"""Add level column on user table

Revision ID: b87ee585a7b5
Revises: 6014dec49e0a
Create Date: 2023-04-11 16:05:32.924568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b87ee585a7b5'
down_revision = '6014dec49e0a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('plan_level', sa.Enum('basic', 'standard', 'plus', 'premium', name='planlevel'), server_default="basic", nullable=False, comment='套餐等级'))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'plan_level')
    # ### end Alembic commands ###