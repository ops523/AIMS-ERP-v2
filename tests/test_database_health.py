from services.database_health_service import DatabaseHealthService


def test_database_connection():
    assert DatabaseHealthService.check_connection() is True