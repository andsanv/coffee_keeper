import json
import boto3
import urllib3

import handle
import commands
import logging
from bot_token import TELEGRAM_BOT_TOKEN

# Configurazione del logger
root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] [%(asctime)s] [%(funcName)s] %(message)s",
    datefmt='%Y-%m-%d %H:%M:%S'
)

database = boto3.client("dynamodb")
return_message: str = ""
return_status_code: int = 200

def lambda_handler(event, context):
    # Logging dell'evento ricevuto
    logging.info("event correctly received")
    
    
    # parse message
    try:
        body = json.loads(event["body"])
    except:
        logging.error("could not load event body properly")
        return { "statusCode": 400, "body": "could not load event body properly" }
    
    try:
        message = body["message"]
        chat = message["chat"]
    except:
        logging.error("the bot only supports chat messages")
        return { "statusCode": 200, "body": "the bot only supports chat messages" }
        
    try:
        text = message["text"]
    except:
        logging.error("the bot only supports text messages")
        return { "statusCode": 200, "body": "the bot only supports text messages" }
    
    try:
        chat_id = str(chat["id"])
    except:
        logging.error("could not retrieve \'chat_id\'")
        return { "statusCode": 200, "body": "could not retrieve \'chat_id\'" }
    
    try:
        user_id = str(message["from"]["id"])
    except:
        logging.error("could not retrieve \'user_id\'")
        return { "statusCode": 200, "body": "could not retrieve \'user_id\'" }
    

    handle.update_user_info(chat_id, user_id, message["from"]["username"])

    print(f"user subscribed: {commands.is_user_subscribed("572807840","572807840")}")

    logging.info(f"user_id = {user_id}, message text = {text}")

    return

    handle.handle_message(body)

    
    http = urllib3.PoolManager()
        
    message_params = {
        "chat_id": chat_id,
        "text": "test superato"
    }
    
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    
    response = http.request(
        "POST",
        url,
        body = json.dumps(message_params),
        headers = {'Content-Type': 'application/json'}
    )
        
    
    logging.info("event correctly handled")
    return { "statusCode": 200, "body": "event correctly handled" }

    try:
        count = text
    except:
        return {
            "statusCode": 400,
            "body": json.dumps(str(e))
        }
    
    try:
        response = database.update_item(
                TableName = table_name,
                Key = {
                    "group_id" : {'N' : group_id},
                    "user_id" : {'N' : user_id}
                },
                UpdateExpression = "SET #c = :c",
                ExpressionAttributeNames = {
                    "#c": "count"
                },
                ExpressionAttributeValues = {
                    ":c": {'N' : count}
                },
                ReturnValues = "UPDATED_NEW"
        )
        
        
        
        if response.status == 200:
            m = 'Messaggio inviato con successo'
        else:
            m = f'Errore nell\'invio del messaggio: {response.data}'
        
        return {
            'statusCode': 200,
            'body': json.dumps(f'update successful. {m}')
        }
    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps(str(e))
        }
