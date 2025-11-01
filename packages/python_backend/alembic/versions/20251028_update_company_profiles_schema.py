"""Align company_profiles schema with service expectations

Revision ID: 20251028_update_company_profiles_schema
Revises: 87efce0cab2b
Create Date: 2025-10-28 16:05:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '20251028_update_company_profiles_schema'
down_revision: Union[str, Sequence[str], None] = '87efce0cab2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Ensure company_profiles has the expected columns
    with op.batch_alter_table('company_profiles') as batch_op:
        # Rename legacy 'name' to 'company_name' if it exists
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        cols = {c['name'] for c in inspector.get_columns('company_profiles')}
        if 'name' in cols and 'company_name' not in cols:
            batch_op.alter_column('name', new_column_name='company_name', existing_type=sa.String())

        # Add new columns if missing
        cols = {c['name'] for c in inspector.get_columns('company_profiles')}
        if 'company_id' not in cols:
            batch_op.add_column(sa.Column('company_id', sa.String(), nullable=True))
        if 'industry' not in cols:
            batch_op.add_column(sa.Column('industry', sa.String(), nullable=True))
        if 'team_size' not in cols:
            batch_op.add_column(sa.Column('team_size', sa.Integer(), nullable=True))
        if 'primary_business' not in cols:
            batch_op.add_column(sa.Column('primary_business', sa.String(), nullable=True))
        if 'communication_style' not in cols:
            batch_op.add_column(sa.Column('communication_style', sa.String(), nullable=True))
        if 'main_channels' not in cols:
            batch_op.add_column(sa.Column('main_channels', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        if 'target_audience' not in cols:
            batch_op.add_column(sa.Column('target_audience', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
        if 'survey_data' in cols:
            # Ensure survey_data is JSONB
            batch_op.alter_column('survey_data', type_=postgresql.JSONB(astext_type=sa.Text()), existing_nullable=True)
        else:
            batch_op.add_column(sa.Column('survey_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # Create unique index for company_id (used in upsert ON CONFLICT)
    # Backfill NULL company_id to unique values if needed is out-of-scope; assume app sets it.
    op.create_unique_constraint(
        constraint_name='uq_company_profiles_company_id',
        table_name='company_profiles',
        columns=['company_id']
    )

    # Drop legacy index on name if exists (renamed above)
    try:
        op.drop_index('ix_company_profiles_name', table_name='company_profiles')
    except Exception:
        pass


def downgrade() -> None:
    # Best-effort rollback: remove added columns and unique constraint
    with op.batch_alter_table('company_profiles') as batch_op:
        try:
            batch_op.drop_constraint('uq_company_profiles_company_id', type_='unique')
        except Exception:
            pass
        for col in ['company_id','industry','team_size','primary_business','communication_style','main_channels','target_audience']:
            try:
                batch_op.drop_column(col)
            except Exception:
                pass
        # Recreate legacy index on name if column exists
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        cols = {c['name'] for c in inspector.get_columns('company_profiles')}
        if 'company_name' in cols and 'name' not in cols:
            batch_op.alter_column('company_name', new_column_name='name', existing_type=sa.String())
    try:
        op.create_index('ix_company_profiles_name', 'company_profiles', ['name'], unique=False)
    except Exception:
        pass

