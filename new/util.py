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

    print("inside")

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
    Returns the user's username if it exists, else his first name (which is mandatory)
    """
    return user["username"] if "username" in user else user["first_name"]