import urllib3
import boto3
import json

import handle
import logging
import util
import bot_token



def parse_event(event: dict) -> dict:
    """
    Parses principal objects and values from the main event dictionary
    """
    try:
        body: dict = json.loads(event["body"])
        message: dict = body["message"]
        chat_id: str = str(message["chat"]["id"])
        user_id: str = str(message["from"]["id"])
    except:
        return None, None, None
    
    return message, chat_id, user_id
    


def lambda_handler(event, context) -> None:
    """
    Main function, handler triggered by the Webhook
    """
    # setup
    root = logging.getLogger() # logger

    if root.handlers:   # remove useless aws default handlers
        for handler in root.handlers:
            root.removeHandler(handler)

    logging.basicConfig(    # setup logger formatting
        level=logging.INFO,
        format="[%(levelname)s] [%(asctime)s] [%(funcName)s] %(message)s",
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    http = urllib3.PoolManager() # http
    database = boto3.client("dynamodb") # allocate database object


    # parse event
    logging.info("event correctly received")
    message, chat_id, user_id = parse_event(event)

    if message == chat_id == user_id == None:   # in case something went wrong
        logging.error("could not load event properly")
        return { "statusCode": 400, "body": "could not load event properly" }   # ask newly for the event
    else:
        logging.info("event parsing completed successfully")
    

    # update user information in database
    handle.update_user_info(database, chat_id, user_id, util.get_username_or_firstname(message["from"]))


    # check whether the message is addressed to the bot
    if not util.contains_a_command(message):  # message does not containt a bot command
        logging.info("message is not a bot command, exiting")
        logging.info("event correctly handled")
        return { "statusCode": 200, "body": "event correctly handled"}


    # handle command and reply to user
    reply_text: str = handle.handle_message(database, message)
    
    if reply_text == None:  # should never happen, in case the handle_message function is called but there is no command for the bot
        logging.error("nothing to handle")
        return {
            "statusCode": 200,
            "body": "nothing to handle"
        }

    data = {    # data to reply to the user
        "chat_id": chat_id,
        "text": reply_text,
        "reply_to_message_id": str(message["message_id"])
    }

    http.request(
        "POST",
        f"https://api.telegram.org/bot{bot_token.TELEGRAM_BOT_TOKEN}/sendMessage",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=urllib3.request.urlencode(data)
    )
    
    # end
    logging.info("event correctly handled")
    return {
        "statusCode": 200,
        "body": "event correctly handled"
    }