from typing import Any


class SelfDefinedException(Exception):
    def __init__(self, reason: Any = None, message: str = "") -> None:
        self.reason = reason  # 异常主要原因
        self.message = message  # 更细节的描述


class AuthorityDenyException(SelfDefinedException):
    def __init__(self, message: str = ""):
        super().__init__("errors.authorityDeny", message)


class UserNotExistException(SelfDefinedException):
    def __init__(self, message: str = ""):
        super().__init__("errors.userNotExist", message)


class InvalidParamsException(SelfDefinedException):
    def __init__(self, message: str = ""):
        super().__init__("errors.invalidParams", message)


class ResourceNotFoundException(SelfDefinedException):
    def __init__(self, message: str = ""):
        super().__init__("errors.resourceNotFound", message)


class InvalidRequestException(SelfDefinedException):
    def __init__(self, message: str = ""):
        super().__init__("errors.invalidRequest", message)


class UsernameExistsException(SelfDefinedException):
    def __init__(self, message: str = ""):
        super().__init__("errors.usernameExists", message)


class EmailExistsException(SelfDefinedException):
    def __init__(self, message: str = ""):
        super().__init__("errors.emailExists", message)


class UserNotVerifiedException(SelfDefinedException):
    def __init__(self, message: str = ""):
        super().__init__("errors.userNotVerified", message)


class InternalException(SelfDefinedException):
    def __init__(self, message: str = ""):
        super().__init__("errors.internal", message)
