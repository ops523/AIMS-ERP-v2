from init_db import initialize_database


_initialized = False


def bootstrap():

    global _initialized

    if _initialized:
        return

    initialize_database()

    _initialized = True