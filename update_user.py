#! /usr/bin/python
# -*- coding: utf-8 -*-

# Поля, которые мы принимаем на входе:
# - идентификатор пользователя
# - время, который пользователь провел на сайте
# - число кликов, которое сделал пользователь
# - число сессий, которые пользователь провел на сайте
# - реферрер, по которому пользователь появился на сайте
# - длина новой сесси
# - число кликов, сделанных за сессию
# - реферрер сессии

# На выходе мы выдаем:
# - id пользователя
# - время, которое он провел на сайте
# - число сделанных им кликов
# - число сессий
# - реферрер пользователя

import sys


# Функция разбора строки в число, которая обрабатывает случай 
# что строка может быть пустой
def parse_int (string):
    if (string is not None):
        return int (string)
    else:
        return 0


# Класс информациии  о пользователи
# Создается из входных полей лога
# Его можно обновлять при помощи записей о новых сессиях
# Для выводной печати сериализуется в строку, разделенную табами
class User:
    def __init__ (self, user_and_session):
        self.user_id = user_and_session.user_id
        self.time_on_site = user_and_session.user_time_on_site
        self.clicks_count = user_and_session.user_clicks_count
        self.sessions_count = user_and_session.user_sessions_count
        self.referrer = user_and_session.user_referrer 
        self.update (user_and_session)
        
    # Метод обновления информации о пользователе
    def update (self, user_and_session):
        self.time_on_site += user_and_session.session_length
        self.clicks_count += user_and_session.session_clicks_count
        if (user_and_session.session_clicks_count != 0):
            self.sessions_count += 1

        if (self.referrer is None):
            self.referrer = user_and_session.session_referrer


    def __str__ (self):
        return "\t".join ((self.user_id, 
                           str (self.time_on_site), 
                           str (self.clicks_count), 
                           str (self.sessions_count), 
                           str (self.referrer)))



# Cджойненая информация о пользователях и сессиях
# Для разбора входных строк скрипта
class UserAndSession:
    def __init__ (self, line):
        # символ, которым hive отмечает пустые поля
        null_symbol = "\\N"             
        fields = line.rstrip ().split ("\t")
        
        # Поиск пустых полей во входной строке и замена их на символ None
        fields = map (lambda s: s if s!=null_symbol else None, fields); 

        # Раздача названий полям
        self.user_id = fields [0]
        self.user_time_on_site = parse_int (fields [1])
        self.user_clicks_count = parse_int (fields [2])
        self.user_sessions_count = parse_int (fields [3])
        self.user_referrer = fields [4]
        self.session_length = parse_int (fields [5])
        self.session_clicks_count = parse_int (fields [6])
        self.session_referrer = fields [7]



# Основное тело скрипта начинается здесь
current_user = None

# Вычитываем построчно стандарный ввод
for line in sys.stdin:
    user_and_session = UserAndSession (line)
    
    # Если текущий пользователь не определен - создаем его по входной строке
    if (current_user is None):
        current_user = User (user_and_session)

    # При смене пользователя печатаем информацию 
    # про старого пользователя и сохраняем нового
    elif (current_user.user_id != user_and_session.user_id):
        print current_user
        current_user = User (user_and_session)
    
    # Обновляем информацию о текущем пользователе
    else:
        current_user.update (user_and_session)
    
# После окончания цикла печатаем информацию о последнем найденном пользователе
if (current_user is not None):
    print current_user
