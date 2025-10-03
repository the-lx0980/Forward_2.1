import re
import pytz
import logging
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.enums import MessageMediaType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import FloodWait
from config import Config
from bot import Bot
from asyncio.exceptions import TimeoutError
from database import save_data

logger = logging.getLogger(__name__)

CHANNEL = {}
SKIN_NO = {}
END_MSG_ID = {}
IST = pytz.timezone('Asia/Kolkata')
OWNER = Config.OWNER_ID

@Client.on_message(filters.private & filters.command(["index"]))
async def run(bot, message):
    if message.from_user.id not in OWNER:
        await message.reply_text("Who the hell are you!!")
        return
    while True:
        try:
            chat = await bot.ask(text = "To Index a channel send me public channel link like <code>https://t.me/xxxxx</code>", chat_id = message.from_user.id, filters=filters.text, timeout=30)
            channel=chat.text
        except TimeoutError:
            await bot.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")
            return

        pattern=".*https://t.me/.*"
        result = re.match(pattern, channel, flags=re.IGNORECASE)
        if result:
            print(channel)
            break
        else:
            await chat.reply_text("Wrong URL")
            continue


    channel_id = re.search(r"t.me.(.*)", channel)
    chat_usr = channel_id.group(1)
    try:
        chat = await bot.get_chat(chat_usr)
    except Exception as e:
        logger.exception(e)
        return await message.reply(f"{e}")
    CHANNEL[message.from_user.id] = chat.username 
    

    while True:
        try:
            SKIP = await bot.ask(
                text="Send me from where you want to start forwarding\nSend 0 for from the beginning.",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=30
            )
            logger.info(SKIP.text)
        except TimeoutError:
            return await bot.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")

        try:
            SKIN_NO[message.from_user.id] = int(SKIP.text)
            break
        except ValueError:
            await SKIP.reply_text("That's an invalid ID. It should be an integer.")
            continue

    while True:
        try:
            end_id = await bot.ask(
                text="Send me forward ending msg id",
                chat_id=message.from_user.id,
                filters=filters.text,
                timeout=30
            )
            logger.info(end_id.text)
        except TimeoutError:
            return await bot.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")

        try:
            END_MSG_ID[message.from_user.id] = int(end_id.text)
            break
        except ValueError:
            await end_id.reply_text("That's an invalid ID. It should be an integer.")
            continue

    buttons = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("Index Media", callback_data="index")
        ],[
            InlineKeyboardButton("Cancel", callback_data="cancel"),  
        ]]
    )

    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"Ok,\nNow choose what type of messages you want to forward.",
        reply_markup=buttons
    )

@Client.on_callback_query()
async def cb_handler(bot: Client, query: CallbackQuery):
    filter = ""
    if query.data == "index":
        filter = "media"
    elif query.data == "cancel":
        return await query.message.delete()
        
    await query.message.delete()

    m = await bot.send_message(
        text="Indexing Started",
        chat_id=query.from_user.id
    )
    user_id = query.from_user.id
    msg_count = 0
    mcount = 0
    deleted = 0
    unsupported = 0
    lst_msg_id=END_MSG_ID.get(user_id)
    chat=CHANNEL.get(user_id)
    CURRENT=SKIN_NO.get(user_id) if SKIN_NO.get(user_id) else 0
    try:
        async for msg in bot.iter_messages(chat, lst_msg_id, CURRENT):
            if msg.empty:
                deleted += 1
                continue
            if not msg.media:
                unsupported += 1
                continue
            if msg.video:
                file_name = msg.video.file_name
            elif msg.document:
                file_name = msg.document.file_name
            elif msg.audio:
                file_name = msg.audio.file_name 
            else:
                file_name = None                
            if msg.caption:
                m_caption = msg.caption
            else:
                m_caption = file_name
            if not m_caption:
                m_caption = "No Caption"
            caption = m_caption
            if filter == "media":
                if msg.media:
                    if msg.media in [MessageMediaType.DOCUMENT, MessageMediaType.VIDEO, MessageMediaType.AUDIO, MessageMediaType.PHOTO]: 
                        media = getattr(msg, msg.media.value, None)
                        id=media.file_id
            try:
                await save_data(id, caption)
            except Exception as e:
                logger.exception(e)
                await bot.send_message(OWNER, f"LOG-Error-{e}")
                pass

            msg_count += 1
            mcount += 1
            new_skip_no = str(CURRENT + msg_count)
            logger.info(f"Total Indexed: {msg_count} - Current SKIP_NO: {new_skip_no}")

            if mcount == 100:
                try:
                    datetime_ist = datetime.now(IST)
                    ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                    await m.edit(text=f"Total Indexed: <code>{msg_count}</code>\nCurrent skip_no: <code>{new_skip_no}</code>\nDeleted Msg skip: {deleted}\nLast edited at {ISTIME}")
                    mcount -= 100
                except FloodWait as e:
                    logger.info(f"Floodwait {e.value}")  
                    pass
                except Exception as e:
                    await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}")
                    logger.exception(e)
                    pass

        await m.edit(f"Succesfully Indexed <code>{msg_count}</code> messages.\n\nNon Media Files: {unsupported}\nDeleted Message: {deleted}")

    except Exception as e:
        logger.exception(e)
        await m.edit(text=f"Error: {e}")
        pass
