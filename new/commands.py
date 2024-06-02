import boto3



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

def handle_subscribe(body: dict, mention: dict):
    chat_id = body["message"]["chat"]["id"]
    user_id = body["message"]["from"]["id"]

    if not is_chat_registered(chat_id):
        return "chat not registered yet"
    
    if is_user_subscribed(chat_id, user_id):
        return "user already subscribed"
    
    database.update_item(
        TableName=COUNTER_TABLE_NAME,
        Key={
            "chat_id": {
                'N': body["message"]["chat"]["id"]
            },
            "user_id": {
                'N': mention["text"] if mention != None else body["message"]["chat"]["id"]
            }
        }
    )