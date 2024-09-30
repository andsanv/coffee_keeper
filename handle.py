import const
import logging
import util




# update handler

def update_user_info(database, chat_id: int, user_id: int, new_username: str) -> bool:
    """
    Allows to update user information in the database for every message sent by the group members.
    This way the database is always updated concering user information
    """

    logging.info("updating user information")

    response: dict = database.query(    # querying to know whether user is subscribed
        TableName=const.COUNTER_TABLE_NAME,
        KeyConditionExpression=f"{const.COUNTER_TABLE_PARTITION_KEY_NAME} = :pk_value AND {const.COUNTER_TABLE_SORT_KEY_NAME} = :sk_value",
        ExpressionAttributeValues={
            ":pk_value": {'N': chat_id},
            ":sk_value": {'N': user_id}
        }
    )

    if response["Items"] == []: # user not subscribed
        logging.info("nothing to update: user not subscribed")
        return

    # if his username changed since last message he sent, update it in the database
    old_username = response["Items"][0]["username"]["S"]
    if old_username == new_username:    # did not change
        logging.info(f"nothing to update: username up to date ({new_username})")
        return

    logging.info("updating database: new username found")   # changed
    database.put_item(
        TableName=const.COUNTER_TABLE_NAME,
        Item={
            const.COUNTER_TABLE_PARTITION_KEY_NAME: {'N': chat_id},
            const.COUNTER_TABLE_SORT_KEY_NAME: {'N': user_id},
            "username": {'S': new_username}
        }
    )

    logging.info(f"username correctly updated: '{old_username}' -> '{new_username}'")
    return True




# main handler

def handle_message(database, message: dict) -> str:
    """
    The main handler of the bot. Allows to parse the text message and handle the command given
    """

    text: str = message["text"] # the actual text of the message
    
    command: dict = None    # will contain information about the command given
    mention: dict = None    # will contain the mentioned user (if mentioned)
    value: str = None       # will contain the value specified (if specified)

    min_command_offset: int = len(text) # used to find the first command in the message
    min_mention_offset: int = len(text)

    for entity in message["entities"]: # saving in 'command' and 'mention' the first occurrencies in the message
        if entity["type"] == "bot_command" and entity["offset"] < min_command_offset:
            command = entity
            command["text"] = text[entity["offset"] : entity["offset"] + entity["length"]]
            min_command_offset = entity["offset"]
        elif entity["type"] == "mention" and entity["offset"] < min_mention_offset:
            mention = entity
            mention["text"] = text[entity["offset"] : entity["offset"] + entity["length"]]
            min_mention_offset = entity["offset"]

    text: str = text.replace(command["text"], "")    # filter command and mention in the text
    command["text"] = command["text"].replace("/", "").replace(f"@{const.TELEGRAM_BOT_NAME}", "")

    if mention != None:
        text = text.replace(mention["text"], "") 
        mention["text"] = mention["text"].replace("@", "")

    for token in text.split(" "):   # searching for a value through message
        try:    # saves first int value found and directly converts it into string
            value = str(int(token))
            break
        except:
            continue

    match command["text"]:  # execute commands' handlers
        case "help":
            return handle_help()
        case "start":
            return handle_start(database, str(message["chat"]["id"]))
        case "subscribe":
            return handle_subscribe(database, message["from"], str(message["chat"]["id"]))
        case "unsubscribe":
            return handle_unsubscribe(database, message["from"], str(message["chat"]["id"]), mention["text"] if mention else None)
        case "get":
            return handle_get(database, message["from"], str(message["chat"]["id"]), mention["text"] if mention else None)
        case "getall":
            return handle_getall(database, str(message["chat"]["id"]))
        case "set":
            return handle_set(database, message["from"], str(message["chat"]["id"]), mention["text"] if mention else None, value)
        case "setall":
            return handle_setall(database, str(message["chat"]["id"]), value)
        case "reset":
            return handle_reset(database, message["from"], str(message["chat"]["id"]), mention["text"] if mention else None)
        case "resetall":
            return handle_resetall(database, str(message["chat"]["id"]))
        case "increment":
            return handle_increment(database, message["from"], str(message["chat"]["id"]), mention["text"] if mention else None, value if value else "1")

    return None




# commands handlers

def handle_help() -> str:
    """
    Shows to user the list of available commands
    """

    logging.info("handling help command")
    logging.info("help successful: commands shown")
    return "help - prints the commands list\n\nstart - registers the chat\n\nsubscribe - subscribes a user\n\nunsubscribe [@user] - unsubscribes a user (default: sender)\n\nget [@user] - returns the count of a user (default: sender)\n\ngetall - returns the count of all subscribed users\n\nset [@user] <value> - sets the count of a user (default: sender) to the value\n\nsetall <value> - sets the count of all users to the value\n\nreset [@user] - resets the count of a user (default: sender)\n\nresetall - resets the count of all users\n\nincrement [@user] [value] - increments the count of a user (default: sender) of the value (default: 1)"


def handle_start(database, chat_id: str) -> str:
    """
    Allows a user to register a chat inside bot's database. Before any user subscribes, the chat needs to be registered.
    This allows a user to be in more groups that include the bot at the same time
    """

    logging.info("handling start command")

    if util.is_chat_registered(database, chat_id):
        logging.info("start failed: chat is already registered")
        return "chat already registered"
    
    logging.info("updating database: adding new chat")
    database.update_item(
        TableName=const.CHATS_TABLE_NAME,
        Key={ "chat_id": { 'N': chat_id } }
    )

    logging.info(f"start successful: chat {chat_id} initialized")
    return "chat successfully registered"


def handle_subscribe(database, user: dict, chat_id: str) -> str:
    """
    Allows a user to subscribe and start using the counter. Count is by default set to 0
    """

    logging.info("handling subscribe command")
    user_id: str = str(user["id"])

    if not util.is_chat_registered(database, chat_id):
        logging.info("subscribe failed: chat is not registered")
        return "chat not registered yet"
    
    if util.is_user_subscribed(database, chat_id, user_id):
        logging.info("subscribe failed: user is already subscribed")
        return "user already subscribed"

    logging.info("updating database: adding new user")
    database.put_item(
        TableName=const.COUNTER_TABLE_NAME,
        Item={
            "chat_id": {'N': chat_id},
            "user_id": {'N': user_id},
            "username": {'S': util.get_username_or_firstname(user)},
            "count": {'N': "0"}
        }
    )

    logging.info(f"subscribe successful: user {user_id} ({util.get_username_or_firstname(user)}) initialized")
    return "user successfully subscribed"


def handle_unsubscribe(database, sender: dict, chat_id: str, mention: str) -> str:
    """
    Allows a user to unsubscribe from the counter. Data related to the user is completely removed from the database
    """

    logging.info("handling unsubscribe command")
    
    if not util.is_chat_registered(database, chat_id):
        logging.info("unsubscribe failed: chat is not registered")
        return "chat not registered yet"
    
    user_id: str = util.get_mention_or_sender(database, sender, mention)

    if not user_id or not util.is_user_subscribed(database, chat_id, user_id):
        logging.info("unsubscribe failed: user is not subscribed")
        return "user is not subscribed"

    logging.info("updating database: deleting user")
    response: dict = database.delete_item(
        TableName=const.COUNTER_TABLE_NAME,
        Key={
            "chat_id": { 'N': chat_id },
            "user_id": { 'N': user_id }
        },
        ReturnValues="ALL_OLD"
    )

    removed_user_id: dict = response["Attributes"]["user_id"]
    username: dict = response["Attributes"]["username"]

    logging.info(f"unsubscribe successful: user {removed_user_id['N']} ({username['S']}) removed")
    return "user successfully unsubscribed"


def handle_get(database, sender: dict, chat_id: str, mention: str) -> str:
    """
    Allows a user to retrieve information about the counter of a member
    """

    logging.info("handling get command")

    if not util.is_chat_registered(database, chat_id):
        logging.info("get failed: chat is not registered")
        return "chat not registered yet"

    user_id: str = util.get_mention_or_sender(database, sender, mention)
    if not user_id or not util.is_user_subscribed(database, chat_id, user_id):
        logging.info("get failed: user is not subscribed")
        return "user is not subscribed"

    logging.info("querying database")
    response: dict = database.query(
        TableName=const.COUNTER_TABLE_NAME,
        KeyConditionExpression="chat_id = :chat_id_value AND user_id = :user_id_value",
        ExpressionAttributeValues={
            ":chat_id_value": {'N': chat_id},
            ":user_id_value": {'N': user_id}
        }
    )

    count: str = response["Items"][0]["count"]['N']
    logging.info(f"get successful: returned count = {count} for user {user_id} ({response['Items'][0]["username"]['S']})")
    return f"user's count: {count} coffee{'s' if int(count) != 1 else ''}"


def handle_getall(database, chat_id: str) -> str:
    """
    Shows the full list of counters related to the chat members
    """

    logging.info("handling getall command")

    if not util.is_chat_registered(database, chat_id):
        logging.info("getall failed: chat is not registered")
        return "chat not registered yet"
    
    logging.info("querying database")
    response: dict = database.query(
        TableName=const.COUNTER_TABLE_NAME,
        KeyConditionExpression="chat_id = :chat_id_value",
        ExpressionAttributeValues={
            ":chat_id_value": {'N': chat_id}
        }
    )

    if response["Count"] == 0:
        logging.info("getall failed: no user from the chat has subscribed")
        return "no user has subscribed"
    
    items: list[str] = []
    for item in response["Items"]:
        items.append(f"{item["username"]['S']}: {item["count"]['N']} coffee{'s' if int(item["count"]['N']) != 1 else ''}")

    logging.info(f"getall successful: returning users counts for chat {chat_id}")
    return '\n'.join(sorted(items))


def handle_set(database, sender: dict, chat_id: str, mention: str, value: str) -> str:
    """
    Allows a user to set a value for the counter of a chat member. Value must be positive and less equal than const.MAX_VALUE
    """

    logging.info("handling set command")

    if not util.is_chat_registered(database, chat_id):
        logging.info("set failed: chat is not registered")
        return "chat not registered yet"
    
    user_id: str = util.get_mention_or_sender(database, sender, mention)
    if not user_id or not util.is_user_subscribed(database, chat_id, user_id):
        logging.info("set failed: user is not subscribed")
        return "user is not subscribed"
    
    if not value or int(value) < 1 or int(value) > const.MAX_VALUE:
        logging.info(f"set failed: invalid value ({value})")
        return "value is not valid"

    logging.info("updating database: setting new counter value")
    response: dict = database.update_item(
        TableName=const.COUNTER_TABLE_NAME,
        Key={
            "chat_id": {'N': chat_id},
            "user_id": {'N': user_id}
        },
        UpdateExpression="SET #c = :new_count",
        ExpressionAttributeNames={
            "#c": "count"
        },
        ExpressionAttributeValues={
            ":new_count": {'N': value}
        },
        ReturnValues="ALL_OLD"
    )

    old_count: str = str(response["Attributes"]["count"]['N'])

    if old_count == value:
        logging.info(f"set successful: user {user_id}'s ({response["Attributes"]["username"]['S']}) count has not changed ({old_count})")
        return f"user's count has not changed: {value}"
    else:
        logging.info(f"set successful: user {user_id}'s ({response["Attributes"]["username"]['S']}) count updated, {old_count} -> {value}")
        return f"user's count updated: {old_count} -> {value}"


def handle_setall(database, chat_id: str, value: str) -> str:
    """
    Allows a user to set all counters of the chat members to a same fixed value
    """
    
    logging.info("handling setall command")

    if not util.is_chat_registered(database, chat_id):
        logging.info("setall failed: chat is not registered")
        return "chat not registered yet"
    
    if not value or int(value) < 1 or int(value) > const.MAX_VALUE:
        logging.info(f"setall failed: invalid value ({value})")
        return "value is not valid"
    
    logging.info("querying database: obtaining all chat members")
    response: dict = database.query(
        TableName=const.COUNTER_TABLE_NAME,
        KeyConditionExpression="chat_id = :chat_id_value",
        ExpressionAttributeValues={
            ":chat_id_value": {'N': chat_id}
        }
    )

    logging.info("updating database: setting new counter value to all members")
    
    for item in response["Items"]:
        database.update_item(
            TableName=const.COUNTER_TABLE_NAME,
            Key={
                "chat_id": {'N': chat_id},
                "user_id": {'N': item["user_id"]['N']}
            },
            UpdateExpression="SET #c = :new_count",
            ExpressionAttributeNames={
                "#c": "count"
            },
            ExpressionAttributeValues={
                ":new_count": {'N': value}
            }
        )

    logging.info(f"setall successful: all counters of chat {chat_id} set to {value}")
    return "all users' counts updated"


def handle_reset(database, sender: dict, chat_id: str, mention: str) -> str:
    """
    Allows a user to reset a chat members's counter, i.e. set it to 0
    """

    logging.info("handling reset command")

    if not util.is_chat_registered(database, chat_id):
        logging.info("reset failed: chat is not registered")
        return "chat not registered yet"
    
    user_id: str = util.get_mention_or_sender(database, sender, mention)
    if not user_id or not util.is_user_subscribed(database, chat_id, user_id):
        logging.info("reset failed: user is not subscribed")
        return "user is not subscribed"

    logging.info(f"updating database: resetting user's counter")
    response: dict = database.update_item(
        TableName=const.COUNTER_TABLE_NAME,
        Key={
            "chat_id": {'N': chat_id},
            "user_id": {'N': user_id}
        },
        UpdateExpression="SET #c = :new_count",
        ExpressionAttributeNames={
            "#c": "count"
        },
        ExpressionAttributeValues={
            ":new_count": {'N': '0'}
        },
        ReturnValues="ALL_OLD"
    )

    old_count: str = str(response["Attributes"]["count"]['N'])

    if old_count == "0":
        logging.info(f"reset successful: user {user_id}'s ({response["Attributes"]["username"]['S']}) count has not changed ({old_count})")
        return f"user's count has not changed: 0"
    else:
        logging.info(f"reset successful: user {user_id}'s ({response["Attributes"]["username"]['S']}) counter reset ({response["Attributes"]["count"]['N']} -> 0)")
        return f"user's counter reset: {response["Attributes"]["count"]['N']} -> 0"
    

def handle_resetall(database, chat_id: str) -> str:
    """
    Allows a user to reset all chat members' counters, i.e. set them to 0
    """

    logging.info("handling resetall command")

    if not util.is_chat_registered(database, chat_id):
        logging.info("resetall failed: chat is not registered")
        return "chat not registered yet"
    
    logging.info("querying database: obtaining all chat members")
    response: dict = database.query(
        TableName=const.COUNTER_TABLE_NAME,
        KeyConditionExpression="chat_id = :chat_id_value",
        ExpressionAttributeValues={
            ":chat_id_value": {'N': chat_id}
        }
    )

    logging.info("updating database: resetting all members' counters")
    
    for item in response["Items"]:
        database.update_item(
            TableName=const.COUNTER_TABLE_NAME,
            Key={
                "chat_id": {'N': chat_id},
                "user_id": {'N': item["user_id"]['N']}
            },
            UpdateExpression="SET #c = :new_count",
            ExpressionAttributeNames={
                "#c": "count"
            },
            ExpressionAttributeValues={
                ":new_count": {'N': '0'}
            }
        )

    logging.info(f"resetall successful: all counters of chat {chat_id} reset")
    return "all users' counters reset"


def handle_increment(database, sender: dict, chat_id: str, mention: str, value: str) -> str:
    logging.info("handling increment command")

    if not util.is_chat_registered(database, chat_id):
        logging.info("increment failed: chat is not registered")
        return "chat not registered yet"
    
    if int(value) < 1:
        logging.info(f"increment failed: invalid value ({value})")
        return "value is not valid"
    
    user_id: str = util.get_mention_or_sender(database, sender, mention)
    if not user_id or not util.is_user_subscribed(database, chat_id, user_id):
        logging.info("increment failed: user is not subscribed")
        return "user is not subscribed"
    
    logging.info("querying database")
    response: dict = database.query(
        TableName=const.COUNTER_TABLE_NAME,
        KeyConditionExpression="chat_id = :chat_id_value AND user_id = :user_id_value",
        ExpressionAttributeValues={
            ":chat_id_value": {'N': chat_id},
            ":user_id_value": {'N': user_id}
        }
    )
    old_count: str = response["Items"][0]["count"]['N']

    if int(value) + int(old_count) > const.MAX_VALUE:
        logging.info(f"increment failed: upper boundary of {const.MAX_VALUE} coffes exceeded")
        return f"count limit ({const.MAX_VALUE}) exceeded"


    logging.info("updating database: increasing user's count")
    response: dict = database.update_item(
        TableName=const.COUNTER_TABLE_NAME,
        Key={
            "chat_id": {'N': chat_id},
            "user_id": {'N': user_id}
        },
        UpdateExpression="SET #c = :new_count",
        ExpressionAttributeNames={
            "#c": "count"
        },
        ExpressionAttributeValues={
            ":new_count": {'N': str(int(old_count) + int(value))}
        },
        ReturnValues="ALL_OLD"
    )

    logging.info(f"increment successful: user {user_id}'s ({response["Attributes"]["username"]['S']}) count increased: {old_count} -> {str(int(old_count) + int(value))}")
    return f"user's count increased: {old_count} -> {str(int(old_count) + int(value))}"