"""Starting over

Revision ID: 0369d0b6ea22
Revises: 
Create Date: 2024-05-28 19:32:56.915863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utc


# revision identifiers, used by Alembic.
revision: str = '0369d0b6ea22'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_role_association',
                    sa.Column('id', sa.Integer(),
                              autoincrement=True, nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('role_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sqlalchemy_utc.sqltypes.UtcDateTime(
                        timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
                    sa.Column('udpated_at', sqlalchemy_utc.sqltypes.UtcDateTime(
                        timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
                    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
                    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('user_id', 'role_id')
                    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_role_association')
    # ### end Alembic commands ###
