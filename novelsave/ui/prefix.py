
class PrinterPrefix:
    """
    An enum class holding should_prefix information
    """

    SUCCESS = '[✓]'
    NEUTRAL = '[-]'
    ERROR = '[✗]'

    fields = ['SUCCESS', 'NEUTRAL', 'ERROR']
    values = [SUCCESS, NEUTRAL, ERROR]
