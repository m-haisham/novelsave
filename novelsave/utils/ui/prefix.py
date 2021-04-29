
class PrinterPrefix:
    """
    An enum class holding should_prefix information
    """

    SUCCESS = ''
    NEUTRAL = ''
    ERROR   = ''
    WARNING = ''
    QUERY   = '?'
    PADDING = ''
    LIST    = '-'

    LENGTH = len(PADDING)

    fields = ['SUCCESS', 'NEUTRAL', 'ERROR', 'WARNING', 'LIST']
    values = [SUCCESS, NEUTRAL, ERROR, WARNING, LIST]
