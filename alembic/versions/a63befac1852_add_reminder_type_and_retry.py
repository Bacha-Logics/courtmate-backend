"""add reminder type and retry

Revision ID: a63befac1852
Revises: 0822f255a6c4
Create Date: 2026-02-19

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a63befac1852'
down_revision = '0822f255a6c4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade schema."""

    # 1️⃣ Add new columns safely

    # Add type as nullable first
    op.add_column(
        'reminders',
        sa.Column('type', sa.String(length=30), nullable=True)
    )

    op.add_column(
        'reminders',
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True)
    )

    op.add_column(
        'reminders',
        sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False)
    )

    op.add_column(
        'reminders',
        sa.Column('max_retries', sa.Integer(), server_default='3', nullable=False)
    )

    # 2️⃣ Backfill existing rows
    op.execute("UPDATE reminders SET type = 'HEARING' WHERE type IS NULL")

    # 3️⃣ Enforce NOT NULL after data exists
    op.alter_column('reminders', 'type', nullable=False)

    # 4️⃣ Alter existing columns

    op.alter_column(
        'reminders',
        'hearing_id',
        existing_type=sa.INTEGER(),
        nullable=True
    )

    op.alter_column(
        'reminders',
        'user_id',
        existing_type=sa.INTEGER(),
        nullable=True
    )

    op.alter_column(
        'reminders',
        'remind_at',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=False
    )

    op.alter_column(
        'reminders',
        'created_at',
        existing_type=postgresql.TIMESTAMP(),
        type_=sa.DateTime(timezone=True),
        existing_nullable=True
    )

    # 5️⃣ Recreate foreign keys with CASCADE

    op.drop_constraint('reminders_hearing_id_fkey', 'reminders', type_='foreignkey')
    op.drop_constraint('reminders_user_id_fkey', 'reminders', type_='foreignkey')

    op.create_foreign_key(
        'reminders_hearing_id_fkey',
        'reminders',
        'hearings',
        ['hearing_id'],
        ['id'],
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        'reminders_user_id_fkey',
        'reminders',
        'users',
        ['user_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint('reminders_user_id_fkey', 'reminders', type_='foreignkey')
    op.drop_constraint('reminders_hearing_id_fkey', 'reminders', type_='foreignkey')

    op.alter_column(
        'reminders',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=True
    )

    op.alter_column(
        'reminders',
        'remind_at',
        existing_type=sa.DateTime(timezone=True),
        type_=postgresql.TIMESTAMP(),
        existing_nullable=False
    )

    op.alter_column(
        'reminders',
        'user_id',
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.alter_column(
        'reminders',
        'hearing_id',
        existing_type=sa.INTEGER(),
        nullable=False
    )

    op.drop_column('reminders', 'max_retries')
    op.drop_column('reminders', 'retry_count')
    op.drop_column('reminders', 'sent_at')
    op.drop_column('reminders', 'type')
