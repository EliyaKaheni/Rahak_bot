import os
import io
import ast
import time
import telebot
import datetime
import schedule
import threading
import pandas as pd
from telebot import types
import plotly.graph_objects as go
from persiantools.jdatetime import JalaliDate

BOT_ID = '7047772089:AAGHg_wXHy4hj5BnzTbe2z1Ei_PkcTjts5g'
bot = telebot.TeleBot(BOT_ID)

# Users temp database
cache = {}
users_cache = {}
goal = 100
admin_id = '168637741'

# Leagues
Leagues = ['موشک 🚀', 'چرخک ⚙️']

# Error handler
def error(message):
    bot.send_message(message.chat.id, "ببخشید فکر کنم یه اشتباهی پیش اومده 🤦\n لطفا ربات رو مجددا استارت کن و از اول مراحل رو طی کن. در صورت نیاز هم با ادمین تماس بگیر.")


""" BASIC FUNCTIONS """
def my_progress_baby(l_sh, l):
    try:
      if len(l) == 0:
          return 0

      l = sorted(l, reverse=True)

      i = 0
      days = []

      while len(l) > i:
          year, month, day = map(int, l[0].split('-'))
          d = JalaliDate(year, month, day)

          if l_sh - d >= datetime.timedelta(1):
              break

          days.append(l[i])
          i+=1

      return days

    except Exception as e:
        print(f'Erorr in my_progress_baby {e}')

def last_shanbe(last_shanbeh):
    try:
      while(JalaliDate.weekday(last_shanbeh) != 0):
          last_shanbeh -= datetime.timedelta(1)

      return last_shanbeh

    except Exception as e:
      print(f'Error in last_shanbe : {e}')

def days_read(id, users, last_shanbeh):
    try:
      days = []
      users_reading = users['Books'].loc[users['ID']==id]
      for reading in users_reading:
        reading = eval(reading)
        for name, reading_list in reading.items():
          for date, pages in reading_list.items():
              year, month, day = map(int, date.split('-'))
              d = JalaliDate(year, month, day)

              if (last_shanbeh - d < datetime.timedelta(1)) and (date not in days):
                  days.append(date)

      return len(days)

    except Exception as e:
        print(f'Error in days_read : {e}')
        error(id)

def pages_read(id, users):
  try:
    last_shanbeh = last_shanbe(JalaliDate.today())
    users_reading = users['Books'].loc[users['ID']==id]
    pages_read_by_person = 0
    for reading in users_reading:
      reading = eval(reading)
      for name, reading_list in reading.items():
        for date, pages in reading_list.items():
            year, month, day = map(int, date.split('-'))
            d = JalaliDate(year, month, day)

            if last_shanbeh - d >= datetime.timedelta(1):
                break

            pages_read_by_person += pages

    return pages_read_by_person

  except Exception as e:
    print(f'Error in pages_read : {e}')
    error(id)

def league_pie(total, read):
  try:
    trace = go.Pie(values=[total - read, read], labels=['خوانده نشده', 'خوانده شده'], marker={'colors': ['#A2C5DB', '#BBB19A']}, hole=0.5, textinfo='label')
    fig = go.FigureWidget(trace)

    image_bytes = fig.to_image(format='png')
    image_io = io.BytesIO(image_bytes)

    return image_io.getvalue()


  except Exception as e:
    print(f'Error in league_pie : {e}')

def leagues_situations(users, l):
  try:
    first = 0
    second = 0
    third = 0
    forth = 0

    for id in users['ID']:
      a = days_read(id, users, last_shanbe(JalaliDate.today()))
      if (a>=4 and l=='M') or (a>=1 and l=='C'):
        first += 1
      a = days_read(id, users, last_shanbe(JalaliDate.today()) - datetime.timedelta(7))
      if (a>=4 and l=='M') or (a>=1 and l=='C'):
        second += 1
      a = days_read(id, users, last_shanbe(JalaliDate.today()) - datetime.timedelta(14))
      if (a>=4 and l=='M') or (a>=1 and l=='C'):
        third += 1
      a = days_read(id, users, last_shanbe(JalaliDate.today()) - datetime.timedelta(21))
      if (a>=4 and l=='M') or (a>=1 and l=='C'):
        forth += 1

    return [(first), (second - first), (third - second), (forth - third)]

  except Exception as e:
    print(f'Error in leagues_situations : {e}')

def leagues_chart(charkhak, mooshak):
  try:
    df = pd.DataFrame({
        'Category': ['سه هفته قبل', 'دو هفته قبل', 'هفته قبل', 'هفته جاری'],
        'Charkhak': charkhak,
        'Mooshak': mooshak
    })

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=df['Category'],
        y=df['Charkhak'],
        name='لیگ چرخک',
        marker_color='#A2C5DB'
    ))

    fig.add_trace(go.Bar(
        x=df['Category'],
        y=df['Mooshak'],
        name='لیگ موشک',
        marker_color='#758281'
    ))

    fig.add_trace(go.Scatter(
        x=df['Category'],
        y=df['Charkhak'],
        mode='lines+markers',
        name='نمودار پیشرفت چرخکی ها',
        line=dict(color='darkblue')
    ))

    fig.add_trace(go.Scatter(
        x=df['Category'],
        y=df['Mooshak'],
        mode='lines+markers',
        name='نمودار پیشرفت موشکی ها',
        line=dict(color='darkgoldenrod')
    ))

    fig.update_layout(
        barmode='group',
        title='گزارش چهار هفته ی اخیر',
        yaxis_title='تعداد افراد پایبند به هدف'
    )

    image_bytes = fig.to_image(format='png')
    image_io = io.BytesIO(image_bytes)

    return image_io.getvalue()

  except Exception as e:
    print(f'Error in leagues_chart : {e}')

def total_reads_pie(people, days):
  try:
    trace = go.Pie(values=days, labels=people, marker={'colors': ['#A2C5DB', '#BBB19A']}, hole=0.5, textinfo='label')
    fig = go.FigureWidget(trace)
    fig.update_traces(textinfo='value+label')

    image_bytes = fig.to_image(format='png')
    image_io = io.BytesIO(image_bytes)

    return image_io.getvalue()

  except Exception as e:
    print(f'Error in league_pie : {e}')


""" DATABASE MANAGEMENT """
def Read_DataBase(myfile):
    try:
        return pd.read_csv(f'{myfile}.csv')

    except:
        print('Please check the database, reading problem')

def Write_DataBase(users, myfile):
    try:
        users.drop(users.columns[users.columns.str.contains(
        'unnamed', case=False)], axis=1, inplace=True)
        users.to_csv(f'{myfile}.csv')

    except:
        print('Please check the database, writing problem')

def add_user_to_database(users_cache, id):
    try:
        if users_cache[id]['League'] == 'چرخک ⚙️':
            users = Read_DataBase('Charkhak')
        else:
            users = Read_DataBase('Mooshak')

        new_user = {'ID':id, 'Name':users_cache[id]['Name'], 'Phone number':users_cache[id]['Phone number'],
        'Uni':users_cache[id]['Uni'], 'Field':users_cache[id]['Field'],
        'League':users_cache[id]['League'], 'Books':users_cache[id]['Book']}

        new_user_df = pd.DataFrame.from_dict(new_user)

        new_user_df.loc[0] = [id, users_cache[id]['Name'], users_cache[id]['Phone number'],
        users_cache[id]['Uni'], users_cache[id]['Field'],users_cache[id]['League'], users_cache[id]['Book']]

        users = pd.concat([users, new_user_df], ignore_index=True)
        users.reset_index()

        if users_cache[id]['League'] == 'چرخک ⚙️':
            Write_DataBase(users, 'Charkhak')
        else:
            Write_DataBase(users, 'Mooshak')

    except:
        print('Adding user failed.')

""" MENUS """

def start_menu(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item = types.KeyboardButton('بریم برای ثبت نام ✅')
        markup.add(item)
        bot.send_message(message.chat.id, 'بریم برای ثبت نام؟', reply_markup=markup)

    except Exception as e:
        print(f'Error in start_menu: {e}')
        error(message)

def leagues_menu(message):
    try:
        markup = types.InlineKeyboardMarkup()

        for league in Leagues:
            glass_button = types.InlineKeyboardButton(
                text=league, callback_data=league)

            markup.add(glass_button)

        bot.send_message(
            message.chat.id, 'لیگتون رو انتخاب کنین.', reply_markup=markup)

    except Exception as e:
        print(f'Error in leagues_menu: {e}')
        error(message)

def uni_menu(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('دانشگاه شریف')
        item2 = types.KeyboardButton('دانشگاه تهران')
        markup.add(item1, item2)
        bot.send_message(message.chat.id, 'مشغول به تحصیل در کدوم دانشگاهید؟', reply_markup=markup)

    except Exception as e:
        print(f'Error in uni_menu: {e}')
        error(message)

def date_menu(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for i in range(0, 5):
            day = JalaliDate.today() - datetime.timedelta(i)
            item = types.KeyboardButton(str(day))
            markup.add(item)
        item_cancel = types.KeyboardButton('بازگشت به منوی اصلی')
        markup.add(item_cancel)
        bot.send_message(message.chat.id, 'مایل به ثبت کتابخوانی در چه تاریخی هستید؟', reply_markup=markup)

    except Exception as e:
        print(f'Error in date_menu: {e}')
        error(message)

def main_menu(message):
    try:
        global admin_id
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item0 = types.KeyboardButton('هدف جمعی')
        item1 = types.KeyboardButton('ثبت مطالعه')
        item2 = types.KeyboardButton('مشاهده آمار')
        item3 = types.KeyboardButton('حذف کتاب')
        item4 = types.KeyboardButton('رهک چیست')
        markup.add(item0, item1, item2, item3, item4)

        if str(message.chat.id) == admin_id:
          item5 = types.KeyboardButton('تعیین هدف')
          item6 = types.KeyboardButton('آمار ثبت های ماهانه')
          item7 = types.KeyboardButton('آمار ثبت های هفتگی')
          item8 = types.KeyboardButton('دانلود دیتابیس')
          markup.add(item5, item6, item7, item8)

        bot.send_message(message.chat.id, 'شما در منوی اصلی قرار دارید', reply_markup=markup)
    except Exception as e:
        print(f'Error in main_menu: {e}')
        error(message)

def book_menu(message):
    try:
        users_charkhak = Read_DataBase('Charkhak')
        users_mooshak = Read_DataBase('Mooshak')

        users = None
        if message.chat.id in users_charkhak['ID'].values:
            users = users_charkhak
        elif message.chat.id in users_mooshak['ID'].values:
            users = users_mooshak
        else:
            bot.send_message(message.chat.id, "کاربر یافت نشد.")
            return

        if len(users.loc[users['ID'] == message.chat.id, 'Books'].values)!=0:
            user_books = eval(users.loc[users['ID'] == message.chat.id, 'Books'].values[0])
        else:
            user_books = {}

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

        for book in user_books.keys():
            item = types.KeyboardButton(book)
            markup.add(item)

        add_button = types.KeyboardButton('افزودن کتاب جدید')
        markup.add(add_button)

        item_cancel = types.KeyboardButton('بازگشت به منوی اصلی')
        markup.add(item_cancel)

        bot.send_message(message.chat.id, 'کتابی که مطالعه کردین رو انتخاب کنین.', reply_markup=markup)

    except Exception as e:
        print(f'Error in book_menu: {e}')
        error(message)

def delete_book_menu(message):
    try:
      users_charkhak = Read_DataBase('Charkhak')
      users_mooshak = Read_DataBase('Mooshak')

      users = None
      if message.chat.id in users_charkhak['ID'].values:
          users = users_charkhak
      elif message.chat.id in users_mooshak['ID'].values:
          users = users_mooshak
      else:
          bot.send_message(message.chat.id, "کاربر یافت نشد.")
          return

      user_books_str = users.loc[users['ID'] == message.chat.id, 'Books'].values[0]

      if user_books_str:
          user_books = ast.literal_eval(user_books_str)
      else:
          user_books = {}

      markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

      for book in user_books.keys():
          item = types.KeyboardButton(book)
          markup.add(item)

      cancel_button = types.KeyboardButton('لغو')
      markup.add(cancel_button)

      bot.send_message(message.chat.id, 'کتابی که می‌خواهید حذف کنید را انتخاب کنید.', reply_markup=markup)
      bot.register_next_step_handler(message, remove_book2)

    except Exception as e:
        print(f'Error in delete_book_menu: {e}')
        error(message)

def stats_menu(message):
    try:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        item1 = types.KeyboardButton('آمار پیشرفت خودم')
        item2 = types.KeyboardButton('آمار پیشرفت لیگ')
        item3 = types.KeyboardButton('هدف جمعی')
        item_cancel = types.KeyboardButton('بازگشت به منوی اصلی')
        markup.add(item1, item2, item3, item_cancel)

        bot.send_message(message.chat.id, 'در منوی مشاهده آمار قرار دارید.', reply_markup=markup)
    except Exception as e:
        print(f'Error in stats_menu: {e}')
        error(message)

"""Sign-up Section"""
# Start handler
@bot.message_handler(commands=['start'])
def handle_start(message):
    try:
        global users_cache
        users_cache[message.chat.id] = {}

        bot.send_message(message.chat.id, 'سلام :) \nبه رهک خوش اومدین. لطفا مراحل ثبت نام رو طی کنین.')

        start_menu(message)

    except Exception as e:
      print(f'Error in start: {e}')
      error(message)


# Sign-up section
@bot.message_handler(func=lambda message: message.text=='بریم برای ثبت نام ✅')
def signup_1(message):
    try:
        bot.send_message(message.chat.id, 'لطفا نام و نام خانوادگی تون رو وارد کنید')
        bot.register_next_step_handler(message, signup_2)

    except Exception as e:
      print(f'Error in signup_1: {e}')
      error(message)

def signup_2(message):
    try:
        global users_cache
        name = message.text
        users_cache[message.chat.id]['Name'] = name

        bot.register_next_step_handler(message, signup_3)
        bot.send_message(message.chat.id, 'لطفا شماره موبایل یا آیدی لگرام خود را وارد کنید')

    except Exception as e:
      print(f'Error in signup_2: {e}')
      error(message)

def signup_3(message):
    try:
        global users_cache
        phone_number = message.text
        users_cache[message.chat.id]['Phone number'] = phone_number


        uni_menu(message)
        bot.register_next_step_handler(message, signup_4)

    except Exception as e:
      print(f'Error in signup_3: {e}')
      error(message)

def signup_4(message):
    try:
        global users_cache
        university = message.text
        users_cache[message.chat.id]['Uni'] = university

        bot.send_message(message.chat.id, 'رشته تحصیلیتون رو بنویسید')
        bot.register_next_step_handler(message, signup_5)

    except Exception as e:
      print(f'Error in signup_4: {e}')
      error(message)


def signup_5(message):
    try:
        global users_cache
        field = message.text
        users_cache[message.chat.id]['Field'] = field

        bot.send_message(message.chat.id, 'گروه کتابخوانی رهک دوتا لیگ داره که با هم در پایبند بودن به کتابخوانی رقابت میکنن. لیگ موشک و لیگ چرخک.\nموشکی ها انتخاب میکنن که در هفته چهار الی هفت روز مطالعه داشته باشن و چرخکی ها تصمیم دارن در هفته یک الی سه روز مطالعه کنند.')
        leagues_menu(message)

    except Exception as e:
      print(f'Error in signup_5: {e}')
      error(message)

@bot.callback_query_handler(func=lambda call: True)
def signup_6(call):
    try:
        global users_cache

        if call.data in Leagues:
            bot.answer_callback_query(
                call.id, f'{call.data} :انتخاب شد')
            leagues = call.data
            users_cache[call.message.chat.id]['League'] = leagues

        bot.send_message(call.message.chat.id, 'تبریک میگم شما دیگه عضوی از رهک هستید. به یاد داشته باشید که در صورتی که پونزده روز بدون ثبت هیچ مطالعه ای در گروه عضو باشید، عضویت شما لغو میشه.')
        users_cache[call.message.chat.id]['Book'] = {}

        add_user_to_database(users_cache, call.message.chat.id)

        main_menu(call.message)

    except Exception as e:
      print(f'Error in signup_6: {e}')
      error(call.message)


"""Reading Section"""
@bot.message_handler(func=lambda message: message.text=='ثبت مطالعه')
def date_set(message):
    try:
        date_menu(message)
        bot.register_next_step_handler(message, book_set)

    except Exception as e:
      print(f'Error in date_set: {e}')
      error(message)

def book_set(message):
    try:
      if message.text == 'بازگشت به منوی اصلی':
        main_menu(message)
        return
      global cache
      cache[message.chat.id] = []
      date = message.text
      cache[message.chat.id].append(date)

      book_menu(message)

      bot.register_next_step_handler(message, page_set)

    except Exception as e:
      print(f'Error in book_set: {e}')
      error(message)

def page_set(message):
    try:
        if message.text == 'بازگشت به منوی اصلی':
          main_menu(message)
          return

        global cache
        book_name = message.text
        if book_name != 'افزودن کتاب جدید':
            cache[message.chat.id].append(book_name)

            bot.send_message(message.chat.id, 'چند صفحه مطالعه کرده اید؟')
            bot.register_next_step_handler(message, note_data)
        else:
            bot.send_message(message.chat.id, 'نام کتابی که قصد مطالعه آنرا دارید را بنویسید')
            bot.register_next_step_handler(message, add_book1)

    except Exception as e:
      print(f'Error in page_set: {e}')
      error(message)

@bot.message_handler(func=lambda message: message.text=='رهک چیست')
def description(message):
    try:
        letter = """"سلام به "رَهَک" خوش اومدی.🌱
 رهک اون راه کوچکیه که ما برای جا دادن عادت کتاب خوانی در زندگیمون بهش وارد شدیم.🛣

رهک یک هدف جمعی داره. اونم کتاب خوندن و با هم بیشتر آشنا شدن. اینجا ما مطالعه‌هامون رو ثبت  میکنیم و برای دور هم بودن بهانه می‌سازیم. 

ابزار های رهک بهتون کمک میکنه هدف گذاری مناسب خودتون بکنید و هدفتون رو از یاد نبرید. 👓

رهک دو تیم داره:✌️🏻

🛞 چرخک: 
اگه تازه شروع کردی به مطالعه یا در طول هفته سرت خیلی شلوغه این لیگ برای توعه.
در چرخک ما به خودمون قول میدیم در هفته ۲ الی ۳ روز کتاب بخونیم

🚀 موشک: اگه یک کتاب‌خون حرفه ای هستی راهو درست اومدی. 
در موشک ما به خودمون قول میدیم ۴ الی ۷ روز در هفته کتاب بخونیم.


📌 بعد از اینکه تیمت رو انتخاب کردی، باید هر روزی که به قولت عمل کردی، تعداد صفحه های مطالعتو رو در ربات تلگرامی رهک ثبت کنی. 
اگر ثبت مطالعه رو فراموش کردی، رهک بهت یادآوری میکنه."""
        bot.send_message(message.chat.id, letter)
    
    except Exception as e:
      print(f'Error in description: {e}')
      error(message)

def add_book1(message):
    try:
        global cache
        book_name = message.text
        cache[message.chat.id].append(book_name)
        bot.send_message(message.chat.id, f'کتاب {book_name} با موفقیت به لیست کتابهای شما اضافه شد. لطفا تعداد صفحه ای از آن را که مطالعه کرده اید، را ارسال کنید.')
        bot.register_next_step_handler(message, note_data)

    except Exception as e:
      print(f'Error in add_book_1: {e}')
      error(message)

def note_data(message):
    try:
        global cache
        id = int(message.chat.id)

        users_charkhak = Read_DataBase('Charkhak')
        users_mooshak = Read_DataBase('Mooshak')

        users = None
        if id in users_charkhak['ID'].values:
            League = 'C'
            users = users_charkhak
        elif id in users_mooshak['ID'].values:
            League = 'M'
            users = users_mooshak
        else:
            bot.send_message(message.chat.id, "کاربر یافت نشد.")
            return


        user_books_str = users.loc[users['ID'] == id, 'Books'].values[0]

        if user_books_str:
            user_books = ast.literal_eval(user_books_str)
        else:
            user_books = {}

        book_name = cache[id][1]
        pages_read = int(message.text)
        date_read = cache[id][0]

        if book_name not in user_books:
            user_books[book_name] = {}
            user_books[book_name][date_read] = pages_read
        else:
            if date_read in user_books[book_name].keys():
                user_books[book_name][date_read] += pages_read
            else:
                user_books[book_name][date_read] = pages_read

        users.loc[users['ID'] == id, 'Books'] = str(user_books)

        if League == 'C':
            Write_DataBase(users, 'Charkhak')
        else:
            Write_DataBase(users, 'Mooshak')

        del cache[id]
        main_menu(message)

    except Exception as e:
        print(f'Error in note_data: {e}')
        error(message)

@bot.message_handler(func=lambda message: message.text=='مشاهده آمار')
def statistics(message):
  stats_menu(message)


@bot.message_handler(func=lambda message: message.text=='آمار پیشرفت خودم')
def indivisual_progress(message):
    try:
      users_charkhak = Read_DataBase('Charkhak')
      users_mooshak = Read_DataBase('Mooshak')

      users = None
      if message.chat.id in users_charkhak['ID'].values:
          users = users_charkhak
      elif message.chat.id in users_mooshak['ID'].values:
          users = users_mooshak
      else:
          bot.send_message(message.chat.id, "کاربر یافت نشد.")
          return
      days = days_read(message.chat.id, users, last_shanbe(JalaliDate.today()))
      bot.send_message(message.chat.id, f'شما در هفته تا کنون {days} روز مطالعه کرده اید.')

    except Exception as e:
      print(f'Error in indivisual_progress: {e}')
      error(message)

@bot.message_handler(func=lambda message: message.text=='آمار پیشرفت لیگ')
def league_progress(message):
  try:
      users_charkhak = Read_DataBase('Charkhak')
      users_mooshak = Read_DataBase('Mooshak')

      charkhak_goods, mooshak_goods = leagues_situations(users_charkhak, 'C'), leagues_situations(users_mooshak, 'M')

      bot.send_message(message.chat.id, 'در حال پردازش آمار هستیم، لطفا چند لحظه صبر کنید ...')

      bot.send_photo(message.chat.id, leagues_chart(charkhak_goods[::-1], mooshak_goods[::-1]))


  except Exception as e:
      print(f'Error in league_progress: {e}')
      error(message)

@bot.message_handler(func=lambda message: message.text=='بازگشت به منوی اصلی')
def back_to_main_menu(message):
  try:
    main_menu(message)
  except Exception as e:
    print(f'Error in back_to_main_menu function: {e}')
    error(message)

@bot.message_handler(func=lambda message: message.text=='حذف کتاب')
def remove_book1(message):
    delete_book_menu(message)

def remove_book2(message):
    try:
        book_to_delete = message.text
        if book_to_delete == 'لغو':
            main_menu(message)
            return

        users_charkhak = Read_DataBase('Charkhak')
        users_mooshak = Read_DataBase('Mooshak')

        users = None
        if message.chat.id in users_charkhak['ID'].values:
            League = 'C'
            users = users_charkhak
        elif message.chat.id in users_mooshak['ID'].values:
            League = 'M'
            users = users_mooshak
        else:
            bot.send_message(message.chat.id, "کاربر یافت نشد.")
            return

        user_books_str = users.loc[users['ID'] == message.chat.id, 'Books'].values[0]

        if user_books_str:
            user_books = ast.literal_eval(user_books_str)
        else:
            bot.send_message(message.chat.id, "کتابی برای حذف یافت نشد.")
            main_menu(message)
            return

        if book_to_delete in user_books:
            del user_books[book_to_delete]
            users.loc[users['ID'] == message.chat.id, 'Books'] = str(user_books)

            if League == 'C':
                Write_DataBase(users, 'Charkhak')
            else:
                Write_DataBase(users, 'Mooshak')

            bot.send_message(message.chat.id, f'کتاب {book_to_delete} با موفقیت حذف شد.')
        else:
            bot.send_message(message.chat.id, 'کتاب در لیست شما یافت نشد.')

        main_menu(message)

    except Exception as e:
        print(f'Error in delete_book: {e}')
        error(message)

@bot.message_handler(func= lambda message: message.text=='دانلود دیتابیس' and str(message.chat.id) == admin_id)
def database_download(message):
  try:
    users_charkhak = Read_DataBase('Charkhak')
    users_mooshak = Read_DataBase('Mooshak')

    users_charkhak.to_excel('Charkhak.xlsx')
    users_mooshak.to_excel('Mooshak.xlsx')
    with open('Charkhak.xlsx', 'rb') as file:
      bot.send_document(message.chat.id, file)
    with open('Mooshak.xlsx', 'rb') as file:
      bot.send_document(message.chat.id, file)

    os.remove('Mooshak.xlsx')
    os.remove('Charkhak.xlsx')

  except Exception as e:
        print(f'Error in database_download : {e}')
        error(message)

@bot.message_handler(func= lambda message: (message.text=='آمار ثبت های ماهانه' and str(message.chat.id) == admin_id))
def monthly_reads(message):
  try:
    users_charkhak = Read_DataBase('Charkhak')
    users_mooshak = Read_DataBase('Mooshak')

    charkhak_days = []
    mooshak_days = []
    charkhak_people = []
    mooshak_people = []

    for id, name in zip(users_charkhak['ID'], users_charkhak['Name']):
      charkhak_days.append(days_read(id, users_charkhak, last_shanbe(JalaliDate.today()-datetime.timedelta(21))))
      charkhak_people.append(name)
    for id, name in zip(users_mooshak['ID'], users_mooshak['Name']):
      mooshak_days.append(days_read(id, users_mooshak, last_shanbe(JalaliDate.today()-datetime.timedelta(21))))
      mooshak_people.append(name)

    bot.send_message(message.chat.id, 'چارت ماهانه لیگ چرخک')
    bot.send_photo(message.chat.id, total_reads_pie(charkhak_people, charkhak_days[::-1]))
    bot.send_message(message.chat.id, 'چارت ماهانه موشک')
    bot.send_photo(message.chat.id, total_reads_pie(mooshak_people, mooshak_days[::-1]))


  except Exception as e:
        print(f'Error in monthly_reads: {e}')

@bot.message_handler(func= lambda message: (message.text=='آمار ثبت های هفتگی' and str(message.chat.id) == admin_id))
def weekly_reads(message):
  try:
    users_charkhak = Read_DataBase('Charkhak')
    users_mooshak = Read_DataBase('Mooshak')

    charkhak_days = []
    mooshak_days = []
    charkhak_people = []
    mooshak_people = []

    for id, name in zip(users_charkhak['ID'], users_charkhak['Name']):
      charkhak_days.append(days_read(id, users_charkhak, last_shanbe(JalaliDate.today())))
      charkhak_people.append(name)
    for id, name in zip(users_mooshak['ID'], users_mooshak['Name']):
      mooshak_days.append(days_read(id, users_mooshak, last_shanbe(JalaliDate.today())))
      mooshak_people.append(name)

    bot.send_message(message.chat.id, 'چارت هفتگی لیگ چرخک')
    bot.send_photo(message.chat.id, total_reads_pie(charkhak_people, charkhak_days[::-1]))
    bot.send_message(message.chat.id, 'چارت هفتگی موشک')
    bot.send_photo(message.chat.id, total_reads_pie(mooshak_people, mooshak_days[::-1]))


  except Exception as e:
        print(f'Error in weekly_reads: {e}')


@bot.message_handler(func= lambda message: (message.text=='تعیین هدف' and str(message.chat.id) == admin_id))
def goal_set_1(message):
  try:
    bot.send_message(message.chat.id, 'هدف را وارد کنید')
    bot.register_next_step_handler(message, goal_set_2)

  except Exception as e:
        print(f'Error in goal_set_1: {e}')
        error(message)

def goal_set_2(message):
  try:
    global goal
    goal = int(message.text)
    bot.send_message(message.chat.id, f'هدف تعیین شد: {goal}')

  except Exception as e:
        print(f'Error in goal_set_2: {e}')
        error(message)


@bot.message_handler(func=lambda message: message.text=='هدف جمعی')
def league_goal_situation(message):
  try:
    global goal

    users_charkhak = Read_DataBase('Charkhak')
    users_mooshak = Read_DataBase('Mooshak')

    users = None
    if message.chat.id in users_charkhak['ID'].values:
        League = 'C'
        users = users_charkhak
    elif message.chat.id in users_mooshak['ID'].values:
        League = 'M'
        users = users_mooshak
    else:
        bot.send_message(message.chat.id, "کاربر یافت نشد.")
        return

    all_group_progress = 0
    for id in users['ID']:
        all_group_progress += pages_read(id, users_charkhak)
    for id in users['ID']:
        all_group_progress += pages_read(id, users_mooshak)

    bot.send_message(message.chat.id, f'{all_group_progress} صفحه از {goal} صفحه مطالعه شده است. ')
    bot.send_photo(message.chat.id, league_pie(goal, all_group_progress))
    


  except Exception as e:
    print(f'Error in group_goal_situation: {e}')
    error(message)

"""Reminder section"""
def check_last_submission(user_books, n):
    last_submission = max(date for book in user_books.values() for date in book.keys())
    year, month, day = map(int, last_submission.split('-'))
    d = JalaliDate(year, month, day)
    if (JalaliDate.today() - d).days >= n:
        return True
    return False

def check_submissions(message):
    users_charkhak = Read_DataBase('Charkhak')
    users_mooshak = Read_DataBase('Mooshak')

    for id in users_charkhak['ID']:
      user_books = eval(users_charkhak.loc[users_charkhak['ID'] == id, 'Books'].values[0])
      if check_last_submission(user_books, 4):
        bot.send_message(id, 'سلام دوست عزیز شما بیش از 4 روز است که هیچ ثبتی نداشته اید')

    for id in users_mooshak['ID']:
      user_books = eval(users_mooshak.loc[users_mooshak['ID'] == id, 'Books'].values[0])
      if check_last_submission(user_books, 2):
        bot.send_message(id, 'سلام دوست عزیز شما بیش از 2 روز است که هیچ ثبتی نداشته اید')
    
schedule.every().day.at("10:30").do(check_submissions)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.start()

    
    
bot.polling()
