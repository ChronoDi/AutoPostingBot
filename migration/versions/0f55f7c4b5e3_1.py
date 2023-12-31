"""1

Revision ID: 0f55f7c4b5e3
Revises: 
Create Date: 2023-10-25 16:11:03.350763

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f55f7c4b5e3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('groups',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tg_id', sa.BigInteger(), nullable=False),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.PrimaryKeyConstraint('id', 'tg_id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('tg_id')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('group', sa.String(), nullable=False),
    sa.Column('group_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('text', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('group_id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('taskiq_schedules',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('task_name', sa.String(), nullable=False),
    sa.Column('args', sa.JSON(), nullable=True),
    sa.Column('kwargs', sa.JSON(), nullable=True),
    sa.Column('labels', sa.JSON(), nullable=True),
    sa.Column('time', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tg_id', sa.BigInteger(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('second_name', sa.String(), nullable=True),
    sa.Column('user_name', sa.String(), nullable=True),
    sa.Column('role', sa.Enum('SUPER_ADMIN', 'ADMIN', 'USER', name='role'), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('tg_id')
    )
    op.create_table('malling',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('count_posts', sa.Integer(), nullable=False),
    sa.Column('is_sent', sa.Boolean(), nullable=False),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('group_id', sa.BigInteger(), nullable=False),
    sa.Column('mailing_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['groups.tg_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('urls',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('url', sa.String(), nullable=False),
    sa.Column('group', sa.String(), nullable=False),
    sa.Column('post_id', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['posts.group_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('post_mailing',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('post_id', sa.Integer(), nullable=False),
    sa.Column('mailing_id', sa.Integer(), nullable=False),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['mailing_id'], ['malling.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_mailing')
    op.drop_table('urls')
    op.drop_table('malling')
    op.drop_table('user')
    op.drop_table('taskiq_schedules')
    op.drop_table('posts')
    op.drop_table('groups')
    # ### end Alembic commands ###
