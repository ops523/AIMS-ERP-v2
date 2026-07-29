from core.bootstrap import bootstrap


_started = False


def startup():

    global _started

    if _started:
        return

    bootstrap()

    _started = True
