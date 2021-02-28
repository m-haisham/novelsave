
class PrinterPrefix:
    """
    An enum class holding should_prefix information
    """

    SUCCESS = '[✓]'
    NEUTRAL = '[-]'
    ERROR = '[✗]'
    LIST = ' +--'

    fields = ['SUCCESS', 'NEUTRAL', 'ERROR', 'LIST']
    values = [SUCCESS, NEUTRAL, ERROR, LIST]
