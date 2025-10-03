import logging, pytz, random, asyncio
from config import Config
from pyrogram import Client, filters, enums
from database import get_search_results, Data
from pyrogram.errors import FloodWait
from datetime import datetime

logger = logging.getLogger(__name__)

IST = pytz.timezone('Asia/Kolkata')
MessageCount = 0
BOT_STATUS = "0"
status = set(int(x) for x in BOT_STATUS.split())
OWNER = Config.OWNER_ID

@Client.on_message(filters.command("status"))
async def count(bot, m):
    if 1 in status:
        await m.reply_text("Currently Bot is forwarding messages.")
    if 1 not in status and 2 not in status:
        await m.reply_text("Bot is Idle now, You can start a task.")

@Client.on_message(filters.command('total'))
async def total(bot, message):
    if message.from_user.id not in OWNER:
        return await message.reply_text("Who the hell are you!!")
    msg = await message.reply("Counting total messages in DB...", quote=True)
    try:
        total = await Data.count_documents()
        await msg.edit(f'Total Messages: {total}')
    except Exception as e:
        await msg.edit(f'Error: {e}')

@Client.on_message(filters.command('cleardb'))
async def clrdb(bot, message):
    if message.from_user.id not in OWNER:
        return await message.reply_text("Who the hell are you!!")
    msg = await message.reply("Clearing files from DB...", quote=True)
    try:
        await Data.collection.drop()
        await msg.edit(f'Cleared DB')
    except Exception as e:
        await msg.edit(f'Error: {e}')

@Client.on_message(filters.command("forward"))
async def forward(bot, message):
    global MessageCount
    if message.from_user.id not in OWNER:
        return await message.reply_text("Who the hell are you!!")
    if 1 in status:
        await message.reply_text("A task is already running.")
        return

    m = await bot.send_message(chat_id=message.from_user.id, text="Started Forwarding....")

    while await Data.count_documents() != 0:
        data = await get_search_results()
        for msg in data:
            to_chat=Config.TO_CHANNEL 
            file_id=msg.id
            caption=msg.caption
            try:
                try:
                    await bot.send_cached_media(
                        chat_id=to_chat,
                        file_id=file_id,
                        caption=caption
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    await bot.send_cached_media(
                        chat_id=to_chat,
                        file_id=file_id,
                        caption=caption
                    )               
                await asyncio.sleep(1)
                try:
                    status.add(1)
                except:
                    pass
            except Exception as e:
                logger.exception(e)
                pass

            await Data.collection.delete_one({
                'use': 'forward'
                })

            MessageCount += 1
            
            try:
                datetime_ist = datetime.now(IST)
                ISTIME = datetime_ist.strftime("%I:%M:%S %p - %d %B %Y")
                await m.edit(text=f"Total Forwarded: <code>{MessageCount}</code>\nForwarded Using: Bot\nSleeping for {1} Seconds\nLast Forwarded at {ISTIME}")
            except Exception as e:
                logger.exception(e)
                await bot.send_message(chat_id=OWNER, text=f"LOG-Error: {e}")
                pass

    logger.info("Finished")

    try:
        await m.edit(text=f'Successfully Forwarded {MessageCount} messages')
    except Exception as e:
        await bot.send_message(OWNER, e)
        logger.exception(e)
        pass

    try:
        status.remove(1)
    except:
        pass

    MessageCount = 0
