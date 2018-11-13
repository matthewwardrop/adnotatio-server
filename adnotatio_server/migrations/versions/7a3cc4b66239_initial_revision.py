"""Initial revision.

Revision ID: 7a3cc4b66239
Revises:
Create Date: 2018-11-13 14:29:51.925229

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a3cc4b66239'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('authors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=512), nullable=True),
    sa.Column('name', sa.String(length=512), nullable=True),
    sa.Column('avatar', sa.String(length=1024), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_authors_email'), 'authors', ['email'], unique=False)
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uuid', sa.String(length=512), nullable=True),
    sa.Column('authority', sa.String(length=512), nullable=True),
    sa.Column('document_id', sa.String(length=512), nullable=True),
    sa.Column('document_version', sa.String(length=512), nullable=True),
    sa.Column('reply_to_id', sa.Integer(), nullable=True),
    sa.Column('text', sa.Text(), nullable=True),
    sa.Column('annotations', sa.Text(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('ts_created', sa.BigInteger(), nullable=True),
    sa.Column('ts_updated', sa.BigInteger(), nullable=True),
    sa.Column('is_resolved', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ),
    sa.ForeignKeyConstraint(['reply_to_id'], ['comments.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_comments_uuid'), 'comments', ['uuid'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_comments_uuid'), table_name='comments')
    op.drop_table('comments')
    op.drop_index(op.f('ix_authors_email'), table_name='authors')
    op.drop_table('authors')
