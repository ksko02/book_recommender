import telebot
from telebot import types
import hybrid_model
from telebot.types import InputMediaPhoto
import csv
import json

users_ratings = {}
users_results = {}



datafile = open('data/interim/books_information.csv', 'r', encoding='utf-8')
books_rows = csv.reader(datafile)

books = []
# book_id,authors,original_publication_year,title,average_rating,image_url

for row in books_rows:
    if row[2] == 'original_publication_year':
        continue
    books.append({'book_id': row[0], 
                  'authors': row[1], 
                  'original_publication_year' : row[2], 
                  'title' : row[3],
                  'average_rating' : row[4],
                  'image_url' : row[5] 
                  })

print("Amount of books:",len(books))

key = open("bot_key.key", 'r').readline()
print(key)
bot = telebot.TeleBot(token=key)




@bot.message_handler(commands=['start'])
def startFunction(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item_1 = types.KeyboardButton('End rating books')
    item_2 = types.KeyboardButton('Reset rates')
    markup.add(item_1, item_2)
    print(message)
    users_ratings[message.chat.id] = []
    bot.send_message(message.chat.id, "This bot helps you to find new books! Write me author or book's name and rate books. \n Based on your ratings, I offer you book. Choose from 3 to 15 b`ooks", reply_markup=markup)

@bot.message_handler(func=(lambda message : message.text == 'End rating books'))
def endRating(message):
    result = []
    if len(users_ratings[message.chat.id]) >= 3 and len(users_ratings[message.chat.id]) <= 15:
        bot.send_message(message.chat.id,"Generating recommendation...")
        # book_id,authors,original_publication_year,title,average_rating,image_url
        #   0       1                  2              3        4            5
        result = hybrid_model.get_recommendation(users_ratings[message.chat.id])
        print(result[0][1])
        result_books = ""
        media = []
        for i in range(len(result)):
            result_books += f"{result[i][3]}\n{result[i][1]} ({int(float(result[i][2]))})\n⭐{result[i][4]}\n\n"
            media.append(InputMediaPhoto(result[i][5]))
        result_string = f"""Here's you recommendations! \n\n {result_books}"""
        bot.send_media_group(message.chat.id,media)
        bot.send_message(message.chat.id, result_string)
        users_ratings[message.chat.id] = []
    else:
        bot.send_message(message.chat.id,"You choose too much or not enough books! Choose books again")
        users_ratings[message.chat.id] = []

@bot.message_handler(func=lambda message : message.text == 'Reset rates')
def howManyBooks(message):
    users_ratings[message.chat.id] = []
    bot.reply_to(message,f"Done! Rate books again")

@bot.message_handler(func=lambda message : True)
def findTheBook(message):
    request_text = message.text
    result_books = list(filter(
        lambda book : 
            request_text.lower() in book['title'].lower() or
            request_text.lower() in book['authors'].lower(),
            books))
    # print(result_books)
    result_string = "Search results:\n\n"
    for i, offered_book in enumerate(result_books):
        result_string += f"Book #{i + 1}\n{offered_book['title']}\n{offered_book['authors']} ({int(float(offered_book['original_publication_year']))})\n⭐{offered_book['average_rating']}\n\n"
    result_string += "Choose number of book that you search"

    remove_markup = types.ReplyKeyboardRemove()

    if len(result_string) > 4096:
        bot.send_message(message.chat.id, 'Do request search more concrete')
        bot.register_next_step_handler_by_chat_id(message.chat.id,findTheBook)
    else:
        if len(result_books) == 0:
            bot.send_message(message.chat.id, "Could not search book. Try another book.")
        else:
            bot.send_message(message.chat.id, result_string, reply_markup=remove_markup)
            bot.register_next_step_handler_by_chat_id(message.chat.id, rateTheBook, result_books)

def rateTheBook(message, result_books):
    try:

        if int(message.text) > len(result_books) or int(message.text) <= 0 :
            raise Exception("Invaild input")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item_1 = types.KeyboardButton('1')
        item_2 = types.KeyboardButton('2')
        item_3 = types.KeyboardButton('3')
        item_4 = types.KeyboardButton('4')
        item_5 = types.KeyboardButton('5')

        markup.add(item_1,item_2, item_3, item_4, item_5)
        bot.send_message(message.chat.id,"Rate this book by number from 1 to 5", reply_markup=markup)
        bot.register_next_step_handler_by_chat_id(message.chat.id,finalChoice, result_books[int(message.text) - 1])

    except Exception as err:
        print(err)
        bot.send_message(message.chat.id,"Choose book and type order number. First book looks kind of interesting...")
        bot.register_next_step_handler_by_chat_id(message.chat.id, rateTheBook, result_books)

    
def finalChoice(message, result_book):
    try:
        if int(message.text) > 5 or int(message.text) <= 0:
            raise Exception("Invaild input")
        if message.chat.id in users_ratings:
            users_ratings[message.chat.id].append((result_book['book_id'], int(message.text)))# [(<id>, <rating>),(2343,3)] 
        else:
            users_ratings[message.chat.id] = [(result_book['book_id'], int(message.text))]
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        item_1 = types.KeyboardButton('End rating books')
        item_2 = types.KeyboardButton('Reset rates')
        markup.add(item_1, item_2)
        bot.send_message(message.chat.id, f"Now you rate {len(users_ratings[message.chat.id])} books!",reply_markup=markup)
        print(users_ratings[message.chat.id])
    except Exception as err:
        print(err)
        bot.send_message(message.chat.id,"Enter number from 1 to 5. May be 5 of 5?")
        bot.register_next_step_handler_by_chat_id(message.chat.id,finalChoice, result_book)

    
    


bot.infinity_polling()