from dataclasses import dataclass, field

@dataclass
class User:
    username: str
    password: str
    role: str = "standard"

class UserFactory:
    
    # default valid user — works for most tests
    @staticmethod
    def standard() -> User:
        return User(
            username="standard_user",
            password="secret_sauce",
            role="standard"
        )

    # locked out user — for negative tests
    @staticmethod
    def locked() -> User:
        return User(
            username="locked_out_user",
            password="secret_sauce",
            role="locked"
        )

    # performance glitch user — slow UI tests
    @staticmethod
    def slow() -> User:
        return User(
            username="performance_glitch_user",
            password="secret_sauce",
            role="slow"
        )

    # custom — test overrides only what it cares about
    @staticmethod
    def build(username: str = "standard_user",
              password: str = "secret_sauce",
              role: str = "standard") -> User:
        return User(username=username, password=password, role=role)