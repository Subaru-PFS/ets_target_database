"""create index on proposal.grade

Revision ID: 5b40ed8dcd48
Revises: 0b72e62efd44
Create Date: 2025-03-31 12:11:54.201748

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "5b40ed8dcd48"
down_revision = "0b72e62efd44"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, "partner", ["partner_id"])
    op.alter_column(
        "proposal",
        "proposal_id",
        existing_type=sa.VARCHAR(),
        comment="Unique identifier for proposal (e.g, S21B-OT06)",
        existing_comment="Unique identifier for proposal (e.g, S21B-OT06?)",
        existing_nullable=False,
        autoincrement=False,
    )
    op.alter_column(
        "proposal",
        "group_id",
        existing_type=sa.VARCHAR(),
        comment="Group ID in STARS (e.g., o21195)",
        existing_comment="Group ID in STARS (e.g., o21195?)",
        existing_nullable=False,
        autoincrement=False,
    )
    op.alter_column(
        "proposal",
        "grade",
        existing_type=sa.VARCHAR(),
        comment="TAC grade (A/B/C/F and N/A)",
        existing_comment="TAC grade (A/B/C/F in the case of HSC queue)",
        existing_nullable=False,
    )
    op.create_index("idx_proposal_grade", "proposal", ["grade"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index("idx_proposal_grade", table_name="proposal")
    op.alter_column(
        "proposal",
        "grade",
        existing_type=sa.VARCHAR(),
        comment="TAC grade (A/B/C/F in the case of HSC queue)",
        existing_comment="TAC grade (A/B/C/F and N/A)",
        existing_nullable=False,
    )
    op.alter_column(
        "proposal",
        "group_id",
        existing_type=sa.VARCHAR(),
        comment="Group ID in STARS (e.g., o21195?)",
        existing_comment="Group ID in STARS (e.g., o21195)",
        existing_nullable=False,
        autoincrement=False,
    )
    op.alter_column(
        "proposal",
        "proposal_id",
        existing_type=sa.VARCHAR(),
        comment="Unique identifier for proposal (e.g, S21B-OT06?)",
        existing_comment="Unique identifier for proposal (e.g, S21B-OT06)",
        existing_nullable=False,
        autoincrement=False,
    )
    op.drop_constraint(None, "partner", type_="unique")
    # ### end Alembic commands ###
