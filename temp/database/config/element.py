from typing import Callable, Any


class ConfigElement:
    name: str
    default: Any
    validate: Callable[[Any], bool]

    def __init__(self, user, name, default=None, validate=None):
        self.user = user
        self.name = name
        self.default = default
        self.validate = validate

    def get(self):
        try:
            return self.user.data[self.name]
        except KeyError as e:
            if self.default is not None:
                return self.default
            else:
                raise e

    def put(self, value):
        valid = True
        if self.validate is not None:
            valid = self.validate(value)

        if valid:
            self.user.data[self.name] = value
            self.user.save()
        else:
            raise ValueError(f"Validation Failed; '{value}' is invalid for config '{self.name}'")
