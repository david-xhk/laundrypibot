#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import telegram
from telegram.ext import Updater, ConversationHandler, MessageHandler, CommandHandler, Filters
import laundrypidb
import logging


logging.basicConfig(format='[%(asctime)s] %(name)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

BOT_TOKEN = "811400967:AAFhHBH7CI264VsmWPh5JMnbT0Ivyntv-TE"

updater = Updater(BOT_TOKEN)

dispatcher = updater.dispatcher


def send_washer_notification(chat_id, washer_id):
    text = "Hello, this is to notify you that washer {} has stopped running.".format(washer_id)
    send_message(chat_id, text)


def send_kivy_notification(chat_id, washer_id):
    text = "Hello, this is to notify you that your phone number was used in the Kivy App. You will be notified when washer {} has stopped running.".format(washer_id)
    send_message(chat_id, text)


def send_message(chat_id, text):
    dispatcher.bot.send_message(chat_id=chat_id, text=text)


def start_callback(bot, update):
    chat_id = update.message.chat_id
    
    text1 = 'Hello {}'.format(update.message.from_user.first_name)
    bot.send_message(chat_id=chat_id, text=text1)
    
    text2 = "Welcome to LaundryPiBot, where you can get live information and notifications about your laundry in SUTD!"
    bot.send_message(chat_id=chat_id, text=text2)
    
    contact_btn = telegram.KeyboardButton(text="Send my contact", request_contact=True)
    reply_markup = telegram.ReplyKeyboardMarkup([[contact_btn], ["No thanks"]])
    
    text3 = "We have a Kivy App at the laundry room just in case you forget your mobile phone. Do you want to share your contact for use in the Kivy App?\n\n_By sharing your contact, you acknowledge and consent to the collection, use and disclosure of your phone number by LaundryPiBot according to the Personal Data Protection Act (PDPA) for the purpose of: 'Getting Telegram chat id from phone number for use in Kivy App'._"
    bot.send_message(chat_id=chat_id, text=text3, reply_markup=reply_markup, parse_mode=telegram.ParseMode.MARKDOWN)
    
    return 1


def start_reply_callback(bot, update):
    if update.message.text == "No thanks":
        text = "You have chosen not to share your contact. Please note that the Kivy App in the laundry room will not be able to accept your phone number until you have registered it. If you would like to do so, please /start LaundryPiBot again.\n\n"
    
    elif update.message.contact:
        text = "Thank you, your contact details have been saved. You can now use the Kivy App in the laundry room!\n\n"
        laundrypidb.set_chat_id(update.message.contact["phone_number"], update.message.chat_id)
    
    else:
        text = ""
    
    text += "To start using LaundryPiBot, you can type in one of the following commands:\n1.  /washers\nSee the status of all washers\n\n2.  /notify [washer_id]\nGet notified when a specific washer or the next available washer has stopped running (if/if not provided with a washer_id).\n\n3.  /report washer_id\nPlease use this command when a washer is faulty."
    
    reply_markup = telegram.ReplyKeyboardRemove()
    bot.send_message(chat_id=update.message.chat_id, text=text, reply_markup=reply_markup)
    
    return -1

dispatcher.add_handler(ConversationHandler(
    entry_points=[CommandHandler("start", start_callback)],
    
    states={1:[MessageHandler(Filters.contact, start_reply_callback),
               MessageHandler(Filters.text, start_reply_callback)]},
    
    fallbacks=[MessageHandler(Filters.text, start_reply_callback)]))


def notify_callback(bot, update):
    chat_id = update.message.chat_id
    washer_id = update.message.text.replace("/notify", "").strip()  
    
    if not washer_id or laundrypidb.is_valid_washer(washer_id):
        reply = laundrypidb.update_waitlist(washer_id, chat_id)
    
    else:
        reply = "Invalid washer id! Usage: /notify [washer_id]"
    
    update.message.reply_text(reply)

dispatcher.add_handler(CommandHandler("notify", notify_callback))


def washers_callback(bot, update):
    update.message.reply_text(laundrypidb.check_washers())

dispatcher.add_handler(CommandHandler("washers", washers_callback))


def report_callback(bot, update):
    washer_id = update.message.text.replace("/report", "").strip()
        
    if laundrypidb.is_valid_washer(washer_id):
        laundrypidb.set_washer_state(washer_id, "faulty")
        reply = "Thank you for reporting. Washer {} has been reported as faulty.".format(washer_id)
    
    else:
        reply = "Invalid washer id! Usage: /report washer_id"
    
    update.message.reply_text(reply)

dispatcher.add_handler(CommandHandler("report", report_callback))


def echo_callback(bot, update):
    update.message.reply_text(update.message.text)

dispatcher.add_handler(MessageHandler(Filters.text, echo_callback))


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', bot, error)

dispatcher.add_error_handler(error_handler)


def main():
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

