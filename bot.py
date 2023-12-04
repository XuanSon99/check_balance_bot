from telegram import *
from telegram.ext import *
import requests
import json
from types import SimpleNamespace
import math
import random
import time
from datetime import datetime, timedelta
import pytz
from dateutil import tz

domain = "https://api.chootc.com"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Tham giá @chootcvn để mua, bán USDT số lượng lớn.", parse_mode=constants.ParseMode.HTML)

async def messageHandler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    username = update.effective_user.username
    chat_id = update.effective_chat.id

    if update.message.chat.type == "private":
        return

    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    if "/sodu" in update.message.text:

        message_id = await context.bot.send_message(chat_id, text='<b>Loading 0%</b>', parse_mode=constants.ParseMode.HTML)

        text = "<b>DANH SÁCH SỐ DƯ\n</b>"

        for index, item in enumerate(data):
            text += f"{index+1}. {item['name']}: {get_balance(item['wallet'])} USDT\n"
            
            if index % 3 == 0:
                percent = f"<b>Loading {round((index+1)/len(data)*100)}%</b>"
                await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id.message_id, text=percent, parse_mode=constants.ParseMode.HTML)

        await context.bot.delete_message(message_id=message_id.message_id, chat_id=chat_id)
        await context.bot.send_message(chat_id, text, parse_mode=constants.ParseMode.HTML)

    if "/ds" in update.message.text:

        message_id = await context.bot.send_message(chat_id, text='<b>Loading 0%</b>', parse_mode=constants.ParseMode.HTML)

        date = update.message.text[4:]
        if date:
            text = f"<b>DOANH SỐ NGÀY {date}</b>\n"
            start_date = datetime.strptime(date,"%d/%m/%Y")
        else:
            text = f"<b>DOANH SỐ HÔM NAY</b>\n"
            today = datetime.now()
            start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)

        end_date = start_date + timedelta(days=1)

        min_timestamp = int(round(start_date.timestamp()))*1000
        max_timestamp = int(round(end_date.timestamp()))*1000

        for index, item in enumerate(data):
            res = requests.get(
                f"https://api.trongrid.io/v1/accounts/{item['wallet']}/transactions/trc20?limit=200&min_timestamp={min_timestamp}&max_timestamp={max_timestamp}&contract_address=TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
            )
            tx = res.json()["data"]
            total = 0
            for i in tx:
                value = round(float(i['value'])*pow(10, -6))
                if value > 10:
                    total += abs(value)

            text += f"{index+1}. {item['name']}: {round(float(total)):,}\n"

            if index % 3 == 0:
                percent = f"<b>Loading {round((index+1)/len(data)*100)}%</b>"
                await context.bot.edit_message_text(chat_id=chat_id, message_id=message_id.message_id, text=percent, parse_mode=constants.ParseMode.HTML)

        await context.bot.delete_message(message_id=message_id.message_id, chat_id=chat_id)
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=text,
            parse_mode=constants.ParseMode.HTML,
        )

def get_balance(address):
    url = "https://apilist.tronscan.org/api/account"
    payload = {
        "address": address,
    }
    res = requests.get(url, params=payload)
    trc20token_balances = json.loads(res.text)["trc20token_balances"]
    token_balance = next(
        (item for item in trc20token_balances if item["tokenId"] == 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'), None)
    if token_balance == None:
        return 0
    else:
        return f'{round(float(token_balance["balance"])*pow(10, -6)):,}'

app = ApplicationBuilder().token(
    "6605453961:AAEuAw1XyloVT0fmn53c48RFcw2cMQ3WCJw").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.ALL, messageHandler))

app.run_polling()
