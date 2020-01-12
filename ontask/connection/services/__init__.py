# -*- coding: utf-8 -*-

"""Services to manage connections."""
from ontask.connection.services.athena import (
    create_athena_connection_admintable, create_athena_connection_runtable,
)
from ontask.connection.services.crud import (
    ConnectionTableAdmin, ConnectionTableSelect, clone_connection, delete,
    toggle,
)
from ontask.connection.services.sql import (
    create_sql_connection_admintable, sql_connection_select_table,
)
