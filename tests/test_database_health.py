from services.database_health_service import DatabaseHealthService


def test_database_connection():
    assert DatabaseHealthService.check_connection() is True


def test_database_type_is_supported():
    database_type = DatabaseHealthService.get_database_type()

    assert database_type in {
        "PostgreSQL",
        "SQLite",
    }


def test_database_configuration_is_valid():
    DatabaseHealthService.validate_configuration()