import functools

from loguru import logger

from .session import Session


def ensure_close(func):
    @functools.wraps(func)
    def wrapped(*args, **kwargs):
        session: Session = args[0].session

        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            if not session.is_closed:
                session.send_sync(f"`❗ {str(e).strip()}`")

            logger.exception(e)

        if not session.is_closed:
            session.close_and_inform()

        return result

    return wrapped
