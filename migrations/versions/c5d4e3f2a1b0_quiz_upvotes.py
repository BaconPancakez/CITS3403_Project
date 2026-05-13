"""quiz upvotes count and quiz_upvote table

Revision ID: c5d4e3f2a1b0
Revises: b4c3d2e1f0a9
Create Date: 2026-05-13

"""
from alembic import op
import sqlalchemy as sa


revision = "c5d4e3f2a1b0"
down_revision = "b4c3d2e1f0a9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("course_quiz", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "upvote_count",
                sa.Integer(),
                nullable=False,
                server_default="0",
            )
        )

    op.create_table(
        "quiz_upvote",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("quiz_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["quiz_id"], ["course_quiz.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "quiz_id", name="uq_quiz_upvote_user_quiz"),
    )
    with op.batch_alter_table("quiz_upvote", schema=None) as batch_op:
        batch_op.create_index(
            batch_op.f("ix_quiz_upvote_quiz_id"), ["quiz_id"], unique=False
        )


def downgrade():
    with op.batch_alter_table("quiz_upvote", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_quiz_upvote_quiz_id"))
    op.drop_table("quiz_upvote")
    with op.batch_alter_table("course_quiz", schema=None) as batch_op:
        batch_op.drop_column("upvote_count")
