"""Tests for the SQLAlchemy integration."""

from importlib.metadata import version

import pytest
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    text,
    create_engine,
)

import appmap.sqlalchemy  # pylint: disable=unused-import  # noqa: F401
from _appmap.metadata import Metadata

from ..test.helpers import DictIncluding
from .appmap_test_base import AppMapTestBase


class TestSQLAlchemy(AppMapTestBase):
    @staticmethod
    def test_sql_capture(connection, events):
        # Passing a string to execute is deprecated in 1.4
        # and removed in 2.0. We wrap it with text().
        # https://docs.sqlalchemy.org/en/14/core/connections.html#sqlalchemy.engine.Connection.execute
        connection.execute(text("SELECT 1"))
        assert events[0].sql_query == DictIncluding(
            {"sql": "SELECT 1", "database_type": "sqlite"}
        )
        assert events[0].sql_query["server_version"].startswith("3.")
        assert Metadata()["frameworks"] == [
            {"name": "SQLAlchemy", "version": version("sqlalchemy")},
        ]

    @staticmethod
    # pylint: disable=unused-argument
    def test_capture_ddl(events, schema):
        assert "CREATE TABLE addresses" in events[-2].sql_query["sql"]

    # pylint: disable=unused-argument
    def test_capture_insert(self, engine, schema, events):
        ins = self.users.insert().values(name="jack", fullname="Jack Jones")
        with engine.begin() as conn:
            conn.execute(ins)
        assert (
            events[-2].sql_query["sql"]
            == "INSERT INTO users (name, fullname) VALUES (?, ?)"
        )

    # pylint: disable=unused-argument
    def test_capture_insert_many(self, engine, schema, events):
        with engine.begin() as conn:
            conn.execute(
                self.addresses.insert(),
                [
                    {"user_id": 1, "email_address": "jack@yahoo.com"},
                    {"user_id": 1, "email_address": "jack@msn.com"},
                    {"user_id": 2, "email_address": "www@www.org"},
                    {"user_id": 2, "email_address": "wendy@aol.com"},
                ],
            )
        assert (
            events[-2].sql_query["sql"]
            == "-- 4 times\nINSERT INTO addresses (user_id, email_address) VALUES (?, ?)"
        )

    @staticmethod
    @pytest.fixture
    def engine():
        return create_engine("sqlite:///:memory:")

    @staticmethod
    @pytest.fixture
    def connection(engine):
        return engine.connect()

    metadata = MetaData()
    users = Table(
        "users",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String),
        Column("fullname", String),
    )
    addresses = Table(
        "addresses",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("user_id", None, ForeignKey("users.id")),
        Column("email_address", String, nullable=False),
    )

    @pytest.fixture
    def schema(self, engine):
        self.metadata.create_all(engine)
