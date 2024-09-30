TELEGRAM_BOT_NAME: str = "coffee_keeper_bot"

CHATS_TABLE_NAME: str = "chats"     # name of the DynamoDB table which contains a list of registered chats
COUNTER_TABLE_NAME: str = "coffee_counts"   # name of the DynamoDB table that maps chat_id, user_id to its count

COUNTER_TABLE_PARTITION_KEY_NAME: str = "chat_id"
COUNTER_TABLE_SORT_KEY_NAME: str = "user_id"

MAX_VALUE: int = 1024   # max count value