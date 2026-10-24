"""add indexes and cascade

Revision ID: d566770077e7
Revises: bcb0baa75ad0
Create Date: 2026-10-24 21:31:23.201967

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd566770077e7'
down_revision: Union[str, Sequence[str], None] = 'bcb0baa75ad0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('expense_shares_expense_id_fkey', 'expense_shares', type_='foreignkey')
    op.create_foreign_key(
        'expense_shares_expense_id_fkey', 'expense_shares', 'expenses',
        ['expense_id'], ['id'], ondelete='CASCADE',
    )

    op.create_index(op.f('ix_expenses_group_id'), 'expenses', ['group_id'], unique=False)
    op.drop_constraint('expenses_group_id_fkey', 'expenses', type_='foreignkey')
    op.create_foreign_key(
        'expenses_group_id_fkey', 'expenses', 'groups',
        ['group_id'], ['id'], ondelete='CASCADE',
    )

    op.create_index(op.f('ix_group_members_user_id'), 'group_members', ['user_id'], unique=False)
    op.drop_constraint('group_members_group_id_fkey', 'group_members', type_='foreignkey')
    op.create_foreign_key(
        'group_members_group_id_fkey', 'group_members', 'groups',
        ['group_id'], ['id'], ondelete='CASCADE',
    )

    op.create_index(op.f('ix_settlements_group_id'), 'settlements', ['group_id'], unique=False)
    op.drop_constraint('settlements_group_id_fkey', 'settlements', type_='foreignkey')
    op.create_foreign_key(
        'settlements_group_id_fkey', 'settlements', 'groups',
        ['group_id'], ['id'], ondelete='CASCADE',
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('settlements_group_id_fkey', 'settlements', type_='foreignkey')
    op.create_foreign_key(
        'settlements_group_id_fkey', 'settlements', 'groups', ['group_id'], ['id']
    )
    op.drop_index(op.f('ix_settlements_group_id'), table_name='settlements')

    op.drop_constraint('group_members_group_id_fkey', 'group_members', type_='foreignkey')
    op.create_foreign_key(
        'group_members_group_id_fkey', 'group_members', 'groups', ['group_id'], ['id']
    )
    op.drop_index(op.f('ix_group_members_user_id'), table_name='group_members')

    op.drop_constraint('expenses_group_id_fkey', 'expenses', type_='foreignkey')
    op.create_foreign_key(
        'expenses_group_id_fkey', 'expenses', 'groups', ['group_id'], ['id']
    )
    op.drop_index(op.f('ix_expenses_group_id'), table_name='expenses')

    op.drop_constraint('expense_shares_expense_id_fkey', 'expense_shares', type_='foreignkey')
    op.create_foreign_key(
        'expense_shares_expense_id_fkey', 'expense_shares', 'expenses', ['expense_id'], ['id']
    )