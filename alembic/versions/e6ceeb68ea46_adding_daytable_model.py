"""Adding DayTable model

Revision ID: e6ceeb68ea46
Revises: ad5bd4d60045
Create Date: 2021-11-28 12:44:18.941573

"""
from alembic import op
import sqlalchemy as sa
from fastapi_users_db_sqlalchemy import GUID


# revision identifiers, used by Alembic.
revision = "e6ceeb68ea46"
down_revision = "ad5bd4d60045"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "day",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=True),
        sa.Column("points_remaining", sa.Integer(), nullable=True),
        sa.Column("points_used", sa.Integer(), nullable=True),
        sa.Column("activity_points", sa.Integer(), nullable=True),
        sa.Column(
            "day_of_week",
            sa.Enum(
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                name="weekdayenum",
            ),
            nullable=True,
        ),
        sa.Column("date", sa.Date(), nullable=True),
        sa.Column("week_id", sa.Integer(), nullable=True),
        sa.Column("user_id", GUID, nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["week_id"],
            ["week.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("day")
    # ### end Alembic commands ###
