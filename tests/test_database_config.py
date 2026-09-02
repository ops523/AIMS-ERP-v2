from config import (
    DATABASE_IS_POSTGRES,
    DATABASE_IS_SQLITE,
    DATABASE_URL,
)


def test_database_url_is_configured():
    assert DATABASE_URL


def test_database_type_is_supported():
    assert DATABASE_IS_POSTGRES or DATABASE_IS_SQLITE