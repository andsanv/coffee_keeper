import logging, counter, messages, util

from bot_token import token

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackContext


count = None


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def check_group_chat(update: Update, context: CallbackContext) -> bool:
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text(str(messages.Errors.ONLY_GROUP_CHATS))
        return False

    return True


async def start(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return

    await update.message.reply_text(str(count.register_group(update.effective_chat.id)))
    util.write_data(count.counter)


async def help_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return

    await update.message.reply_text(count.handle_help())


async def subscribe_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return

    await update.message.reply_text(str(count.subscribe_user(update.effective_chat.id, update.effective_sender.name)))
    util.write_data(count.counter)


async def get_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return

    await update.message.reply_text(str(count.get_count(update.effective_chat.id, update.effective_sender.name, context)))


async def get_all_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
    
    await update.message.reply_text(str(count.get_counts(update.effective_chat.id)))


async def set_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
    
    await update.message.reply_text(str(count.set_count(update.effective_chat.id, update.effective_sender.name, context)))
    util.write_data(count.counter)


async def set_all_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
     
    await update.message.reply_text(str(count.set_counts(update.effective_chat.id, context)))
    util.write_data(count.counter)


async def reset_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
     
    await update.message.reply_text(str(count.reset_count(update.effective_chat.id, update.effective_sender.name, context)))
    util.write_data(count.counter)


async def reset_all_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
     
    await update.message.reply_text(str(count.reset_counts(update.effective_chat.id)))
    util.write_data(count.counter)

async def increment_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
    
    await update.message.reply_text(str(count.increment_count(update.effective_chat.id, update.effective_sender.name, context)))
    util.write_data(count.counter)


def main() -> None:
    global count
    count = counter.Counter(util.read_data())

    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe_command))
    
    application.add_handler(CommandHandler("get", get_command))
    application.add_handler(CommandHandler("getall", get_all_command))

    application.add_handler(CommandHandler("set", set_command))
    application.add_handler(CommandHandler("setall", set_all_command))

    application.add_handler(CommandHandler("reset", reset_command))
    application.add_handler(CommandHandler("resetall", reset_all_command))

    application.add_handler(CommandHandler("increment", increment_command))

    application.run_polling()


if __name__ == "__main__":
    main()