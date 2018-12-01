from enum import Enum


class UserType(Enum):
    ADMIN = 1
    DEV = 2
    TEST = 3

    @staticmethod
    def convert_to_desc(val):
        if val == 1:
            return str("admin")
        elif val == 2:
            return str("dev")
        elif val == 3:
            return str("test")
        else:
            return str("dev")