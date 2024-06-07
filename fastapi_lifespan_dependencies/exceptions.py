from fastapi.exceptions import ValidationException


class LifespanDependencyError(ValidationException):
    pass
