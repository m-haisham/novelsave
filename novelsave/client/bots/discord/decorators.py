import functools

from loguru import logger

from .session import Session


def session_task(close_on_exit=True):
    def inner(func):
        """Ensures that when this method ends the session will be closed"""

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

                session.close_session()
                if not session.is_closed:
                    session.sync(session.close_and_inform)
            else:
                session.close_session()
                if close_on_exit and not session.is_closed:
                    session.sync(session.close_and_inform)

            return result

        return wrapped

    return inner


def log_error(func):
    """Catches and logs errors from the method and propagates the exception"""

    @functools.wraps(func)
    def wrapped(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            raise e

    return wrapped
