import logging, counter, messages

from bot_token import token

from telegram import Update, BotCommand
from telegram.ext import Application, CommandHandler, CallbackContext



counter = counter.Counter()


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

    await update.message.reply_text(str(counter.register_group(update.effective_chat)))


async def help_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return

    await update.message.reply_text(counter.handle_help())


async def subscribe_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return

    await update.message.reply_text(str(counter.subscribe_user(update.effective_chat, update.effective_sender.name)))


async def get_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return

    await update.message.reply_text(str(counter.get_count(update.effective_chat, update.effective_sender.name, context)))


async def get_all_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
    
    await update.message.reply_text(str(counter.get_counts(update.effective_chat)))


async def set_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
    
    await update.message.reply_text(str(counter.set_count(update.effective_chat, update.effective_sender.name, context)))


async def set_all_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
     
    await update.message.reply_text(str(counter.set_counts(update.effective_chat, context)))


async def reset_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
     
    await update.message.reply_text(str(counter.reset_count(update.effective_chat, update.effective_sender.name, context)))


async def reset_all_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
     
    await update.message.reply_text(str(counter.reset_counts(update.effective_chat)))

async def increment_command(update: Update, context: CallbackContext) -> None:
    if not await check_group_chat(update, context):
        return
    
    await update.message.reply_text(str(counter.increment_count(update.effective_chat, update.effective_sender.name, context)))


def main() -> None:
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