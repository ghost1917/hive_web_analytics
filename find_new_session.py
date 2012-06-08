#! /usr/bin/python
# -*- coding: utf-8 -*-
#
# Метод обнаруживает начала новых сессии 
# и выдает статистики по сессиям на выход
#
# На воход, как ожидается, мы получаем
# - уникальный id пользователя
# - время его захода
# - реферер

# На выхд утилита выписывает
#  - id пользователя
#  - длительность сессии
#  - число кликов за сессию
#  - реферрер, с которого началась сессия
import sys

class Click:
    def __init__ (self, serialized_click):
        fields = serialized_click.rstrip ().split ("\t")
        self.user_id = fields [0]
        self.unixtime = int (fields [1])
        self.referrer = fields [2]

class Session:
    def __init__ (self, click):
        self.user_id = click.user_id
        self.begin_time = click.unixtime
        self.last_click_time = click.unixtime
        self.referrer = click.referrer
        self.clicks_count = 1

    def is_new_session (self, click):
        if (click.user_id != self.user_id):
            return True
        elif (click.unixtime - self.last_click_time > 30*60):
            return True
        return False

    def update (self, click):
        self.last_click_time = click.unixtime
        self.clicks_count += 1

    def __str__ (self):
        return "\t".join ((self.user_id, 
                           str (self.last_click_time - self.begin_time),
                           str (self.clicks_count),
                           self.referrer))
            
current_session = None

for line in sys.stdin:
    click = Click (line)
    if (current_session is None):
        current_session = Session (click)
    elif (current_session.is_new_session (click)):
        print current_session
        current_session = Session (click)
    else:
        current_session.update (click)

if (current_session is not None):
    print current_session
