from .string import StringHelper


def unzip_arguments(args, kwargs, pairs):
    unzipped = []
    for pair in pairs:
        try:
            unzipped.append(args[pair[0]])
        except IndexError:
            unzipped.append(kwargs[pair[1]])

    return unzipped
