# Copyright (C) 2024 - Scalizer (<https://www.scalizer.fr>).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).

from .logging import get_logger
import psycopg
from psycopg.rows import dict_row
import pymssql


logger = get_logger(__name__)


class SqlConnection:
    _name = "SQL"
    connection = None

    def __init__(self, db_type, url, dbname, username, password, port=5432, **kwargs):
        self.db_type = db_type
        self.url = url
        self.dbname = dbname
        self.username = username
        self.password = password
        self.port = port
        if self.db_type == "postgresql":
            self.connection = psycopg.connect(
                user=self.username,
                password=self.password,
                host=self.url,
                dbname=self.dbname,
                port=self.port,
                row_factory=dict_row
            )
        elif self.db_type == "mssql":
            self.connection = pymssql.connect(
                server=self.url,
                user=self.username,
                password=self.password,
                database=self.dbname
            )

    def execute(self, query):
        return self.connection.execute(query)
