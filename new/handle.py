import const
import logging
import util




# update handler

def update_user_info(database, chat_id: int, user_id: int, new_username: str) -> bool:
    logging.info("updating user information")

    response = database.query(
        TableName=const.COUNTER_TABLE_NAME,
        KeyConditionExpression=f"{const.COUNTER_TABLE_PARTITION_KEY_NAME} = :pk_value AND {const.COUNTER_TABLE_SORT_KEY_NAME} = :sk_value",
        ExpressionAttributeValues={
            ":pk_value": {'N': chat_id},
            ":sk_value": {'N': user_id}
        }
    )

    if response["Items"] == []:
        logging.info("nothing to update: user not subscribed")
        return

    old_username = response["Items"][0]["username"]["S"]
    
    if old_username == new_username:
        logging.info(f"username up to date: {new_username}")
        return

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
    text: str = message["text"]
    entities: list[dict] = message["entities"]
    
    command: dict = None
    mention: dict = None
    value: int = None

    min_command_offset: int = len(text)
    min_mention_offset: int = len(text)

    for entity in entities: # saving in 'command' and 'mention' the first occurrencies in the message
        if entity["type"] == "bot_command" and entity["offset"] < min_command_offset:
            command = entity
            command["text"] = text[entity["offset"] : entity["offset"] + entity["length"]]
            min_command_offset = entity["offset"]
        elif entity["type"] == "mention" and entity["offset"] < min_mention_offset:
            mention = entity
            mention["text"] = text[entity["offset"] : entity["offset"] + entity["length"]]
            min_mention_offset = entity["offset"]


    # filter command and mention in the text
    text = text.replace(command["text"], "")
    command["text"] = command["text"].replace("/", "").replace(f"@{const.TELEGRAM_BOT_NAME}", "")

    if mention != None:
        text = text.replace(mention["text"], "") 
        mention["text"] = mention["text"].replace("@", "")

    for token in text.split(" "):   # searching for a value through message
        try:    # saves first int value found
            value = int(token)
            break
        except:
            continue

    match command["text"]:
        case "help":
            return handle_help()
        case "start":
            return handle_start(database, message["chat"]["id"])
        case "subscribe":
            return handle_subscribe(database, message)
        case "unsubscribe":
            return handle_unsubscribe(database, mention=mention)
        case "get":
            return handle_get(body, mention=mention)
        case "getall":
            return handle_getall(body)
        case "set":
            return handle_set(body, mention=mention, value=value)
        case "setall":
            return handle_setall(body, value=value)
        case "reset":
            return handle_reset(body, mention=mention)
        case "resetall":
            return handle_resetall(body)
        case "increment":
            return handle_increment(body, mention=mention, value=value)
        case others:
            pass

    return None




# commands handlers

def handle_help() -> str:
    return "help - prints the commands list\n\nstart - registers the chat\n\nsubscribe - subscribes a user\n\nunsubscribe [@user] - unsubscribes a user (default: sender)\n\nget [@user] - returns the count of a user (default: sender)\n\ngetall - returns the count of all subscribed users\n\nset [@user] <value> - sets the count of a user (default: sender) to the value\n\nsetall <value> - sets the count of all users to the value\n\nreset [@user] - resets the count of a user (default: sender)\n\nresetall - resets the count of all users\n\nincrement [@user] [value] - increments the count of a user (default: sender) of the value (default: 1)"

def handle_start(database, chat_id: str) -> str:
    logging.info("handling start command")

    if util.is_chat_registered(database, chat_id):
        logging.info("start failed as chat is already registered")
        return "chat already registered"
    
    database.update_item(
        TableName=const.CHATS_TABLE_NAME,
        Key={ "chat_id": { 'N': chat_id } }
    )

    logging.info(f"start successful: chat {chat_id} initialized")
    return "chat successfully registered"

def handle_subscribe(database, message: dict) -> str:
    logging.info("handling subscribe command")
    chat_id = str(message["chat"]["id"])
    user_id = str(message["from"]["id"])

    if not util.is_chat_registered(database, chat_id):
        logging.info("subscribe failed as chat is not registered")
        return "chat not registered yet"
    
    if util.is_user_subscribed(database, chat_id, user_id):
        logging.info("subscribe failed as user is already subscribed")
        return "user already subscribed"

    database.put_item(
        TableName=const.COUNTER_TABLE_NAME,
        Item={
            "chat_id": {'N': chat_id},
            "user_id": {'N': user_id},
            "username": {'S': util.get_username_or_firstname(message["from"])},
            "count": {'N': "0"}
        }
    )

    logging.info(f"subscribe successful: user {user_id} ({util.get_username_or_firstname(message["from"])}) initialized")
    return "user succesfully subscribed"

#def handle_unsubscribe(database, body: dict, mention: dict):
#    chat_id = body["message"]["chat"]["id"]
#    user_id = get_user_or_mention(body, mention)
#
#    if not util.is_chat_registered(database, chat_id):
#        return "chat not registered yet"
#    
#    if not util.is_user_subscribed(chat_id, user_id):
#        return "user is not subscribed"
#
#    boto3.client("dynamodb").delete_item(
#        TableName=const.CHATS_TABLE_NAME,
#        Key={
#            "chat_id": {
#                'N': chat_id
#            },
#            "user_id": {
#                'N': user_id
#            }
#        }
#    )
#
#def handle_get(body: dict, mention: dict) -> str:
#    chat_id = body["message"]["chat"]["id"]
#    user_id = get_user_or_mention(body, mention)
#
#    if not is_chat_registered(chat_id):
#        return "chat not registered yet"
#    
#    if not is_user_subscribed(chat_id, user_id):
#        return "user is not subscribed"
#    
#    response = boto3.client("dynamodb").query(
#        KeyConditionExpression=Key("chat_id").eq(chat_id) & Key("user_id").eq(user_id)
#    )
#
#    table_entry = response["Items"]
#
#    if table_entry != []:
#        try:
#            return f"{get_username(body, mention)}'s count: {table_entry["count"]}"
#        except KeyError:
#            return "could not retrieve user's count"
#        
#    return "cannot find user in the database"
