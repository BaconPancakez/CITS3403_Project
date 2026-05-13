"""add course_quiz table

Revision ID: b4c3d2e1f0a9
Revises: 803924669398
Create Date: 2026-05-13

"""
from alembic import op
import sqlalchemy as sa


revision = "b4c3d2e1f0a9"
down_revision = "803924669398"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "course_quiz",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("course_code", sa.String(length=20), nullable=False),
        sa.Column("author_id", sa.Integer(), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("choices", sa.JSON(), nullable=False),
        sa.Column("correct_index", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("course_quiz", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_course_quiz_course_code"), ["course_code"], unique=False
        )


def downgrade():
    with op.batch_alter_table("course_quiz", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_course_quiz_course_code"))
    op.drop_table("course_quiz")
