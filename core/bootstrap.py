from init_db import initialize_database

_bootstrapped = False


def bootstrap():

    global _bootstrapped

    if _bootstrapped:
        return

    initialize_database()

    _bootstrapped = True
