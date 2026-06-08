"""create medical schema

Revision ID: 539d910b57d8
Revises: 
Create Date: 2026-06-05 15:57:20.227144

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '539d910b57d8'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=20), nullable=False),
        sa.Column('nationality', sa.Enum('korean', 'foreigner', name='nationality'), nullable=False),
        sa.Column('last_name', sa.String(length=20), nullable=True),
        sa.Column('first_name', sa.String(length=20), nullable=False),
        sa.Column('middle_name', sa.String(length=20), nullable=True),
        sa.Column('employee_number', sa.String(length=20), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=False),
        sa.Column('gender', sa.Enum('male', 'female', name='gender'), nullable=False),
        sa.Column(
            'department',
            sa.Enum('developer', 'medical team', 'researcher', name='department'),
            nullable=False,
        ),
        sa.Column('role', sa.Enum('pending', 'staff', 'admin', name='role'), server_default='pending', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default='1', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('employee_number'),
        sa.UniqueConstraint('phone_number'),
    )
    op.create_table(
        'patients',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('name', sa.String(length=30), nullable=False),
        sa.Column('age', sa.SmallInteger(), nullable=False),
        sa.Column('gender', sa.Enum('male', 'female', name='gender'), nullable=False),
        sa.Column('phone', sa.String(length=11), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'medical_records',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('patient_id', sa.BigInteger(), nullable=False),
        sa.Column('chart_number', sa.String(length=50), nullable=False),
        sa.Column('symptoms', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=True),
        sa.ForeignKeyConstraint(['patient_id'], ['patients.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chart_number'),
    )
    op.create_table(
        'ai_analysis_results',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('record_id', sa.BigInteger(), nullable=False),
        sa.Column('is_pneumonia', sa.Boolean(), nullable=False),
        sa.Column('confidence', sa.DECIMAL(precision=5, scale=2), nullable=False),
        sa.Column('heatmap_url', sa.String(length=255), nullable=False),
        sa.Column('ai_model', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=True),
        sa.ForeignKeyConstraint(['record_id'], ['medical_records.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'xray_images',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('record_id', sa.BigInteger(), nullable=False),
        sa.Column('uploader_id', sa.BigInteger(), nullable=False),
        sa.Column('image_url', sa.String(length=2048), nullable=False),
        sa.Column('shooting_datetime', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('current_timestamp(0)'), nullable=True),
        sa.ForeignKeyConstraint(['record_id'], ['medical_records.id']),
        sa.ForeignKeyConstraint(['uploader_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('xray_images')
    op.drop_table('ai_analysis_results')
    op.drop_table('medical_records')
    op.drop_table('patients')
    op.drop_table('users')
