import os
import telebot
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pytz
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

BOT_TOKEN = os.environ.get("BOT_TOKEN")
PETROL_URL = os.environ.get("PETROL_URL")

bot = telebot.TeleBot(BOT_TOKEN)


def retrieve_petrol_price():
    petrol_web = requests.get(PETROL_URL)
    soup = BeautifulSoup(petrol_web.content, 'html.parser')

    fuel_comparison_table = soup.find("table", {"class": "fuel_comparison_table"})
    fuel_table_list = fuel_comparison_table.find_all("tr", {"class": "text-center"})

    petrol_data = {}
    petrol_company = ["esso", "shell", "spc", "caltex", "sinopec"]
    petrol_grade_holder = None

    for fuel_table_row_tr in fuel_table_list:
        fuel_table_row_td = fuel_table_row_tr.find_all("td")
        for td in fuel_table_row_td:
            class_name = td.get("class")
            if class_name is not None:
                if "font-weight-bold" in class_name:
                    petrol_grade_holder = td.getText()
                    petrol_data[petrol_grade_holder] = {}

                if class_name[0] in petrol_company:
                    petrol_data[petrol_grade_holder][class_name[0]] = td.getText()
    return petrol_data


def build_html(data):
    sg_timezone = pytz.timezone('Asia/Singapore')
    html = f"Petrol Price for <b>{datetime.now(sg_timezone).strftime('%d-%m-%Y')}</b> \n\n"
    for grade, petrol_prices in data.items():
        html += f"<b>Grade : {grade}</b> \n"
        for company, price in petrol_prices.items():
            html += f"<code>{company} : {price} </code>\n"
        html += "\n\n"
    return html


def retrieve_esso_price():
    petrol_data = retrieve_petrol_price()
    return petrol_data


# keyboard = [[InlineKeyboardButton("Hackerearth", callback_data="test"),
#              InlineKeyboardButton("Hackerrank", callback_data='HRlist8')]]
# reply_markup = InlineKeyboardMarkup(keyboard)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "/price for petrol prices")

@bot.message_handler(commands=['price'])
def send_welcome(message):
    petrol_data = retrieve_petrol_price()
    petrol_html = build_html(petrol_data)

    bot.reply_to(message, petrol_html, parse_mode='HTML')
#    bot.reply_to(message, petrol_html, parse_mode='HTML', reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):  # <- passes a CallbackQuery type object to your function

    print(call.data)
    bot.send_message(call.message.chat.id,  '✅ Correct!')


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    bot.reply_to(message, "Try /price for petrol prices")


bot.infinity_polling()
