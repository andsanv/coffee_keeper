from enum import Enum

class Errors(Enum):
    # group
    GROUP_NOT_REGISTERED = "group not registered yet"
    GROUP_ALREADY_REGISTERED = "group already registered"

    # user
    USER_ALREADY_SUBSCRIBED = "user already subscribed"
    USER_NOT_FOUND = "user not found"

    # other
    BAD_FORMAT = "badly formatted request\n\nuse the\"/help\" command for more info"
    ONLY_GROUP_CHATS = "this bot can only be used in a group chat"


    def __str__(self):
        return f"error: {self.value}"
    

class Info(Enum):
    # group
    GROUP_REGISTERED = "group successfully registered"

    # user
    USER_SUBSCRIBED = "user successfully subscribed"
    NO_USER_SUBSCRIBED = "no user has subscribed yet"

    # other
    SUCCESSFUL_OPERATION = "command successfully handled"

    def __str__(self):
        return f"info: {self.value}"