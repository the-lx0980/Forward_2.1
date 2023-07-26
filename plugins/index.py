import pytz
from datetime import datetime
from pyrogram import Client, filters,
from pyrogram.enums import MessageMediaTyp
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import InviteHashExpired, UserAlreadyParticipant
from config import Config
import re
from bot import Bot
from asyncio.exceptions import TimeoutError
from database import save_data
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


skip_no=""
caption=""
channel_type=""
channel_id_=""
IST = pytz.timezone('Asia/Kolkata')
OWNER=int(Config.OWNER_ID)


@Client.on_message(filters.private & filters.command(["index"]))
async def run(bot, message):
    if message.from_user.id != OWNER:
        return await message.reply_text("Who the hell are you!!")
    while True:
        try:
            chat = await bot.ask(text = "To Index a channel you may send me the channel invite link, so that I can join channel and index the files.\n\nIt should be something like <code>https://t.me/xxxxxx</code> or <code>https://t.me/joinchat/xxxxxx</code>", chat_id = message.from_user.id, filters=filters.text, timeout=30)
            channel=chat.text
        except TimeoutError:
            return await bot.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")
        if "t.me/+" in chat.text:
            return await message.reply_text("Send Public Channel Link Not Private!")
        pattern=".*https://t.me/.*"
        result = re.match(pattern, channel, flags=re.IGNORECASE)
        if result:
            print(channel)
            break
        else:
            await chat.reply_text("Wrong URL")
            continue           
    # global channel_type
    channel_type="public"
    channel_id = re.search(r"t.me.(.*)", channel)
    # global channel_id_
    channel_id_=channel_id.group(1)

    while True:
        try:
            SKIP = await bot.ask(text = "Send me from where you want to start forwarding\nSend 0 for from beginning.", chat_id = message.from_user.id, filters=filters.text, timeout=30)
            print(SKIP.text)
        except TimeoutError:
            return await bot.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")
        try:
            global skip_no
            skip_no=int(SKIP.text)
            break
        except:
            await SKIP.reply_text("Thats an invalid ID, It should be an integer.")
            continue
    while True:
        try:
            LIMIT = await bot.ask(text = "Send me from Upto what extend(LIMIT) do you want to Index\nSend 0 for all messages.", chat_id = message.from_user.id, filters=filters.text, timeout=30)
            print(LIMIT.text)
        except TimeoutError:
            return await bot.send_message(message.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")
        try:
            global limit_no
            limit_no=int(LIMIT.text)
            break
        except:
            await LIMIT.reply_text("Thats an invalid ID, It should be an integer.")
            continue

    buttons=InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("All Messages", callback_data="all")
            ],
            [
                InlineKeyboardButton("Document", callback_data="docs"),
                InlineKeyboardButton("Photos", callback_data="photos")
            ],
            [
                InlineKeyboardButton("Videos", callback_data="videos"),
                InlineKeyboardButton("Audios", callback_data="audio")
            ]
        ]
        )
    await bot.send_message(
        chat_id=message.from_user.id,
        text=f"Ok,\nNow choose what type of messages you want to forward.",
        reply_markup=buttons
        )

@Client.on_callback_query()
async def cb_handler(bot: Client, query: CallbackQuery):
    filter=""
    if query.data == "docs":
        filter=MessageMediaTyp.DOCUMENT
    elif query.data == "all":
        filter="empty"
    elif query.data == "photos":
        filter=MessageMediaTyp.PHOTO
    elif query.data == "videos":
        filter=MessageMediaTyp.VIDEO
    elif query.data == "audio":
        filter=MessageMediaTyp.AUDIO
    caption=None
    await query.message.delete()
    while True:
        try:
            get_caption = await bot.ask(text = "Do you need a custom caption?\n\nIf yes , Send me caption \n\nif No send '0'", chat_id = query.from_user.id, filters=filters.text, timeout=30)
        except TimeoutError:
            await bot.send_message(query.from_user.id, "Error!!\n\nRequest timed out.\nRestart by using /index")
            return
        input=get_caption.text
        if input == "0":
            caption=None
        else:
            caption=input
        break

    m = await bot.send_message(
        text="Indexing Started",
        chat_id=query.from_user.id
    )
    msg_count = 0
    mcount = 0
    FROM=channel_id_
    try:
        async for MSG in bot.USER.search_messages(chat_id=FROM,offset=skip_no,limit=limit_no,filter=filter):
        async for message in bot.iter_messages(FROM, lst_msg_id, skip_no):
            if message.empty:
                continue                
            msg_caption=""
            if caption is not None:
                msg_caption=caption
            elif msg.caption:
                msg_caption=msg.caption 

            if filter in [MessageMediaTyp.DOCUMENT,
                          MessageMediaTyp.VIDEO,
                          MessageMediaTyp.AUDIO,
                          MessageMediaTyp.PHOTO]:
                for file_type in (MessageMediaTyp.DOCUMENT, MessageMediaTyp.VIDEO, MessageMediaTyp.AUDIO, MessageMediaTyp.PHOTO):
                    if msg.media:
                        media = getattr(msg, msg.media.value, None)
                        if media is not None:
                            file_type = file_type
                            id=media.file_id
                            break
            if filter == "empty":
                for file_type in [MessageMediaTyp.DOCUMENT,
                                  MessageMediaTyp.VIDEO,
                                  MessageMediaTyp.AUDIO,
                                  MessageMediaTyp.PHOTO]:
                    if msg.media:
                        media = getattr(msg, msg.media.value, None)
                        if media is not None:
                            file_type = file_type
                            id=media.file_id
                            break
                else:
                    id=f"{FROM}_{msg.id}"
                    file_type="others"
            
            message_id=msg.id
            try:
                await save_data(id, channel, message_id, methord, msg_caption, file_type)
            except Exception as e:
                print(e)
                await bot.send_message(OWNER, f"LOG-Error-{e}")
                pass
            msg_count += 1
            mcount += 1
            new_skip_no=str(skip_no+msg_count)
            print(f"Total Indexed : {msg_count} - Current SKIP_NO: {new_skip_no}")
            if mcount == 100:
                try:
                    datetime_ist = datetime.now(IST)
                    ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                    await m.edit(text=f"Total Indexed : <code>{msg_count}</code>\nCurrent skip_no:<code>{new_skip_no}</code>\nLast edited at {ISTIME}")
                    mcount -= 100
                except FloodWait as e:
                    print(f"Floodwait {e.value}")  
                    pass
                except Exception as e:
                    await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}")
                    print(e)
                    pass
        await m.edit(f"Succesfully Indexed <code>{msg_count}</code> messages.")
    except Exception as e:
        print(e)
        await m.edit(text=f"Error: {e}")
        pass
