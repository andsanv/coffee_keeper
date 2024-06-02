import json
import boto3
import urllib3

from handle import handle_message

import logging

# Configurazione del logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

table_name = "coffee_counts"
database = boto3.client("dynamodb")
return_message: str = ""
return_status_code: int = 200

def lambda_handler(event, context):
    # Logging dell'evento ricevuto
    logger.info("event correctly received")
    
    
    # parse message
    try:
        body = json.loads(event["body"])
    except:
        logger.error("could not load event body properly")
        return { "statusCode": 400, "body": "could not load event body properly" }
    
    try:
        message = body["message"]
        chat = message["chat"]
    except:
        logger.error("the bot only supports chat messages")
        return { "statusCode": 200, "body": "the bot only supports chat messages" }
        
    try:
        text = message["text"]
    except:
        logger.error("the bot only supports text messages")
        return { "statusCode": 200, "body": "the bot only supports text messages" }
    
    try:
        chat_id = str(chat["id"])
    except:
        logger.error("could not retrieve \'chat_id\'")
        return { "statusCode": 200, "body": "could not retrieve \'chat_id\'" }
    
    try:
        user_id = str(message["from"]["id"])
    except:
        logger.error("could not retrieve \'user_id\'")
        return { "statusCode": 200, "body": "could not retrieve \'user_id\'" }
    

    handle_message(body)

    
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
        
    
    logger.info("event correctly handled")
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
