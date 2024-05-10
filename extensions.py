import xml.etree.ElementTree
import requests
import time
import xmltodict
import telebot
class APIException (Exception):
    def __str__(self):
        return 'Валюта отсутствует в справочнике ЦБ'
class MessageException(Exception):
    def __str__(self):
        return('Неверный формат сообщения')
class API_curr:
    path = 'http://www.cbr.ru/scripts/XML_daily.asp?date_req=' + time.strftime('%d', time.localtime()) + '/' + time.strftime('%m', time.localtime()) + '/' + time.strftime('%Y', time.localtime()) + '/'

    @staticmethod
    def get_price(base,quote,amount):
        response = requests.get(API_curr.path)
        data = xmltodict.parse(response.content)
        try:
            if base.upper() == 'RUB':
                quote_curr_value = API_curr.get_curr(data, quote)
                return float(amount)/quote_curr_value
            elif quote.upper() == 'RUB':
                base_curr_value = API_curr.get_curr(data, base)
                return float(amount)*base_curr_value
            else:
                base_curr_value = API_curr.get_curr(data,base)
                quote_curr_value = API_curr.get_curr(data,quote)
                return float(amount)*base_curr_value/quote_curr_value
        except APIException as e:
            raise e

    @staticmethod
    def get_curr(data,cur_name):
        for currs in data.get('ValCurs').get('Valute'):
            if cur_name.lower() == currs.get('CharCode').lower():
                return float(str.replace(currs.get('VunitRate'),',','.'))
        raise APIException()
    @staticmethod
    def get_currs():
        response = requests.get(API_curr.path)
        data = xmltodict.parse(response.content)
        ret_str = ''
        for currs in data.get('ValCurs').get('Valute'):
            ret_str += currs.get('Name')+' ('+currs.get('CharCode')+') '+currs.get('VunitRate')+'\n'
        return ret_str

#API_curr.get_currs()
class MyBot():
    def __init__(self):
        self.TOKEN = '7146595969:AAGMKDA71Qc6ujlTlUX22HpE-b8OOUNaktE'
        self.bot = telebot.TeleBot(self.TOKEN)
        self.help_mess = ('Приветствую. Я умею обрабатывать только текстовые сообщения\n'+
                'Для вызова данного сообщения введите /help или /start\n'+
                'Для перевода напишите сообщение в виде: <Код валюты, цену которой хотите узнать>\n'+
                '<Код валюты, в которой надо узнать цену первой валюты> <количество первой валюты>\n'+
                'Чтобы узнать список доступных валют введите /valuta')


        @self.bot.message_handler(commands=['start', 'help'])
        def handle_start_help(message: telebot.types.Message):
            self.bot.send_message(message.chat.id,  self.help_mess)

        @self.bot.message_handler(commands=['valuta'])
        def handle_start_help(message: telebot.types.Message):
            self.bot.send_message(message.chat.id, API_curr.get_currs())

        # Обрабатывается все документы и аудиозаписи
        @self.bot.message_handler(content_types=['text'])
        def handle_text(message: telebot.types.Message):
            if message.text == 'Hellow':
                self.bot.send_message(message.chat.id,
                                 'Hellow ' + message.from_user.first_name + ' ' + message.from_user.last_name)
            else:
                try:
                    MyBot.check_message(message.text)
                    text = message.text.split()
                    resp = API_curr.get_price(text[0],text[1],text[2])
                    ans_mes = text[2]+' '+text[0].upper()+' в '+text[1].upper()+' равняется '+resp.__str__()
                    self.bot.send_message(message.chat.id, ans_mes)
                except Exception as e:
                    self.bot.send_message(message.chat.id,'Ошибка: '+e.__str__())

        @self.bot.message_handler(
            content_types=['photo', 'audio ', 'voice ', 'video ', 'document ', 'location ', 'contact ', 'sticker '])
        def handle_photo(message: telebot.types.Message):
            self.bot.send_message(message.chat.id, 'Извините, я умею обрабатывать только текстовые поля \n Подсказка: /help',
                             reply_to_message_id=message.message_id)

        self.bot.polling(none_stop=True)

    @staticmethod
    def check_message(text):
        text = text.split()
        if len(text) != 3:
            raise MessageException
        try:
            num = float(text[2])
        except ValueError:
            raise MessageException

