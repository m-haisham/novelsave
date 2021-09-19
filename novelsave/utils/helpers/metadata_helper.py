import json

from novelsave.core.entities.novel import MetaData


def display_value(data: MetaData):
    try:
        others = json.loads(data.others)
    except json.JSONDecodeError:
        others = {}

    others = [f'{key}={value}' for key, value in others.items()]
    postfix = f'(' + ', '.join(others) + ')' if others else ''

    return f'{data.value}{postfix}'
