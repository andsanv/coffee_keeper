import boto3
import json
import commands
import const
import logging

def update_user_info(chat_id: int, user_id: int, username: str, subscription: bool = False) -> bool:
    database = boto3.client("dynamodb")
    
    if not subscription:
        response = database.query(
            TableName=const.COUNTER_TABLE_NAME,
            KeyConditionExpression=f"{const.COUNTER_TABLE_PARTITION_KEY_NAME} = :pk_value AND {const.COUNTER_TABLE_SORT_KEY_NAME} = :sk_value",
            ExpressionAttributeValues={
                ":pk_value": {'N': chat_id},
                ":sk_value": {'N': user_id}
            }
        )

        if response["Items"] == []:
            logging.info("user has not subscripted to the bot. update phase closed.")
            return

    database.put_item(
        TableName=const.COUNTER_TABLE_NAME,
        Item={
            const.COUNTER_TABLE_PARTITION_KEY_NAME: {'N': chat_id},
            const.COUNTER_TABLE_SORT_KEY_NAME: {'N': user_id},
            "username": {'S': username}
        }
    )

    logging.info("user information correctly added." if subscription else "username correctly updated.")
    return True

def handle_message(body: dict) -> str:
    message = body["message"]["text"]
    text: str = message["text"]

    commands = [
        "help",
        "start",
        "subscribe",
        "unsubscribe",
        "get",
        "getall",
        "set",
        "setall",
        "reset",
        "resetall",
        "increment"
    ]

    try:
        entities = message["entities"]      # entities: list of dict
    except:
        return None
    
    command: dict = None
    mention: dict = None
    value: int = None

    min_command_offset = len(text)
    min_mention_offset = len(text)

    for entity in entities:
        if entity["type"] == "bot_command" and entity["offset"] < min_command_offset:
            command = entity
            command["text"] = text[entity["offset"] : entity["offset"] + entity["length"]]
            min_command_offset = entity["offset"]
        elif entity["type"] == "mention" and entity["offset"] < min_mention_offset:
            mention = entity
            mention["text"] = text[entity["offset"] : entity["offset"] + entity["length"]]
            min_mention_offset = entity["offset"]


    # filter command and mention in the text, to find if user has inputted values
    if command == None:
        return None
    else:
        text = text.replace(command["text"], "")
        command["text"] = command["text"].replace("/", "")

    if mention != None:
        text = text.replace(mention["text"], "") 
        mention["text"] = mention["text"].replace("@", "")

    for token in text.split(" "):   # searching for a value through message
        try:    # saves first int value found
            value = int(token)
            break
        except:
            continue

    match command:
        case "help":
            return commands.handle_help()
        case "start":
            return commands.handle_start(body)
        case "subscribe":
            return commands.handle_subscribe(body, mention=mention)
        case "unsubscribe":
            return commands.handle_unsubscribe(body, mention=mention)
        case "get":
            return commands.handle_get(body, mention=mention)
        case "getall":
            return commands.handle_getall(body)
        case "set":
            return commands.handle_set(body, mention=mention, value=value)
        case "setall":
            return commands.handle_setall(body, value=value)
        case "reset":
            return commands.handle_reset(body, mention=mention)
        case "resetall":
            return commands.handle_resetall(body)
        case "increment":
            return commands.handle_increment(body, mention=mention, value=value)
        case others:
            pass

    return None



if __name__ == "__main__":
    event = json_string = '{"body": {"update_id": 123456789,"message": {"message_id": 1,"from": {"id": 987654321,"is_bot": false,"first_name": "John","last_name": "Doe","username": "johndoe","language_code": "en"},"chat": {"id": 987654321,"first_name": "John","last_name": "Doe","username": "johndoe","type": "private"},"date": 1627918741,"text": "/start 5 @anotheruser /subscribe 7","entities": [{"offset": 0,"length": 6,"type": "bot_command"},{"offset": 9,"length": 12,"type": "mention"},{"offset": 22,"length": 10,"type": "bot_command"}]}}}'

    print(handle_message(json.loads(event)["body"]))
