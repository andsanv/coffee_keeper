import boto3
import urllib3
import json


database = boto3.client("dynamodb")


def is_chat_registered(chat_id: str) -> bool:
    return "Item" in database.get_item(
        TableName=CHATS_TABLE_NAME,
        key={
            "chat_id": {
                'N': chat_id
            }
        }
    )

def is_user_subscribed(chat_id: str, user_id: str) -> bool:
    return "Item" in database.get_item(
        TableName=COUNTER_TABLE_NAME,
        key={
            "chat_id": {
                'N': chat_id
            },
            "user_id": {
                'N': user_id
            }
        }
    )


def get_user_id_by_username(username: str) -> tuple[int, str]:
    http = urllib3.PoolManager()

    url = f'{BASE_URL}/getChat'

    response = http.request("GET", url, fields={"chat_id": f"@{username}"})

    if response.status == 200:
        data = json.loads(response.data.decode("utf-8"))
        if data["ok"]:
            return 200, data['result']['id']
    elif response.status == 403:
        return 403, "user has never interacted with the bot yet, so it cannot retrieve his user id"
    
    return 404, "could not retrieve user id"

def get_user_or_mention(body: dict, mention: dict) -> int:
    if mention != None:
        result = get_user_id_by_username(mention["text"])

        if result[0] == 200:
            user_id = result[1]
    else:
        user_id = body["message"]["from"]["id"]

    return int(user_id)

def get_username(body: dict, mention: dict) -> str:
    return mention["text"] if mention != None else body["message"]["from"]["username"]

def handle_help() -> str:
    return "help - prints the commands list\n\nstart - registers the chat\n\nsubscribe [@user] - subscribes a user (default: sender)\n\nunsubscribe [@user] - unsubscribes a user (default: sender)\n\nget [@user] - returns the count of a user (default: sender)\n\ngetall - returns the count of all subscribed users\n\nset [@user] <value> - sets the count of a user (default: sender) to the value\n\nsetall <value> - sets the count of all users to the value\n\nreset [@user] - resets the count of a user (default: sender)\n\nresetall - resets the count of all users\n\nincrement [@user] [value] - increments the count of a user (default: sender) of the value (default: 1)"

def handle_start(body: dict) -> str:
    if is_chat_registered(body["message"]["chat"]["id"]):
        return "chat already registered"
    
    database.update_item(
        TableName=CHATS_TABLE_NAME,
        Key={
            "chat_id": {
                'N': body["message"]["chat"]["id"]
            }
        }
    )

    return "chat successfully registered"

def handle_subscribe(body: dict, mention: dict) -> str:
    chat_id = body["message"]["chat"]["id"]
    user_id = get_user_or_mention(body, mention)

    if not is_chat_registered(chat_id):
        return "chat not registered yet"
    
    if is_user_subscribed(chat_id, user_id):
        return "user already subscribed"
    
    database.put_item(
        TableName=COUNTER_TABLE_NAME,
        Item={
            "chat_id": {'N': chat_id},
            "user_id": {'N': user_id},
            "count": {'N': "0"}
        }
    )

    return "user succesfully subscribed"


def handle_unsubscribe(body: dict, mention: dict):
    chat_id = body["message"]["chat"]["id"]
    user_id = get_user_or_mention(body, mention)

    if not is_chat_registered(chat_id):
        return "chat not registered yet"
    
    if not is_user_subscribed(chat_id, user_id):
        return "user is not subscribed"

    database.delete_item(
        TableName=CHATS_TABLE_NAME,
        Key={
            "chat_id": {
                'N': chat_id
            },
            "user_id": {
                'N': user_id
            }
        }
    )

def handle_get(body: dict, mention: dict) -> str:
    chat_id = body["message"]["chat"]["id"]
    user_id = get_user_or_mention(body, mention)

    if not is_chat_registered(chat_id):
        return "chat not registered yet"
    
    if not is_user_subscribed(chat_id, user_id):
        return "user is not subscribed"
    
    response = database.query(
        KeyConditionExpression=Key("chat_id").eq(chat_id) & Key("user_id").eq(user_id)
    )

    table_entry = response["Items"]

    if table_entry != []:
        try:
            return f"{get_username(body, mention)}'s count: {table_entry["count"]}"
        except KeyError:
            return "could not retrieve user's count"
        
    return "cannot find user in the database"
