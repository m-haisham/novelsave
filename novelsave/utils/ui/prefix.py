
class PrinterPrefix:
    """
    An enum class holding should_prefix information
    """

    SUCCESS = '[SUCCESS]'
    NEUTRAL = '   [INFO]'
    ERROR   = '  [ERROR]'
    WARNING = '[WARNING]'
    LIST    = '   ------'

    fields = ['SUCCESS', 'NEUTRAL', 'ERROR', 'WARNING', 'LIST']
    values = [SUCCESS, NEUTRAL, ERROR, WARNING, LIST]
