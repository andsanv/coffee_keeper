import const




# message parsing

def contains_a_command(message: dict) -> bool:
    """
    Returns true if there is at least one command entity in the message, false otherwise
    """
    
    if "entities" not in message:
        return False
    
    for entity in message["entities"]:
        if entity["type"] == "bot_command":
            return True
        
    return False




# database management

def is_chat_registered(database, chat_id: str) -> bool:
    """
    Returns true if chat is already registered in the database, i.e. if '/start' command was already given
    """

    return "Item" in database.get_item(
        TableName=const.CHATS_TABLE_NAME,
        Key={
            "chat_id": {
                'N': chat_id
            }
        }
    )


def is_user_subscribed(database, chat_id: str, user_id: str) -> bool:
    """
    Returns true if user is already registered in the database, i.e. '/subscribe' command was already given
    """

    return "Item" in database.get_item(
        TableName=const.COUNTER_TABLE_NAME,
        Key={
            "chat_id": {
                'N': chat_id
            },
            "user_id": {
                'N': user_id
            }
        }
    )




# shortcuts

def get_username_or_firstname(user: dict) -> str:
    """
    Returns the user's username (which is optional) if it exists, else his first name (which is mandatory)
    """

    return user["username"] if "username" in user else user["first_name"]


def get_mention_or_sender(database, sender: dict, mention: str) -> str:
    """
    Makes the selection of the id of the user of interest atomic.
    Used where commands may be related to a mention rather than the sender.
    Returns sender id if mention is None, mentioned user's id if mention not None and found in the database, None otherwise
    """

    if not mention: # if there is no mention, return sender's id
        return str(sender["id"])
    
    return get_user_id_by_username(database, mention)   # return mentioned user's id
    

def get_user_id_by_username(database, username: str) -> str:
    """
    Queries the database to try and find a user by his username.
    If the user has changed his username since the last time he sent a message, this function will fail
    """

    response = database.scan(
        TableName=const.COUNTER_TABLE_NAME,
        FilterExpression="username = :username_value",
        ExpressionAttributeValues={":username_value": {'S': username}}
    )

    if not response["Items"]:   # no user with that username was found
        return None
    
    return str(response["Items"][0]["user_id"])  # returns the id of the user found ("[0] to select the first in case more users were found")