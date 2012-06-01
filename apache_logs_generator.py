#! /usr/bin/python
# -*- coding: utf-8 -*-
# Герератор логов апача
# Моделирует работу апач сервера
# и пишет его логи.
# число пользователей и диапазоны дат настраиваются
#
# Мезенцев Павел 2012
# pavel@mezentsev.org

from optparse import OptionParser
import sys
import random
import datetime
import os


# Пользователь. У пользователя есть свой ip адрес, "агент пользователя"
class User (object):
    def __init__ (self, ip, useragent):
        self.ip = ip
        self.useragent = useragent
        pass

    # Активация - это заход пользователя на сайт.
    # момент активации мы утанавливаем, с какого ресурса пришел пользователь
    # его траекторию по сайту
    # число кликов, которые он следает на ресурсе
    def activate (self, web_path, session_referrer, current_time, clicks_count):
        self.web_path = web_path
        self.session_referrer = session_referrer
        self.url = session_referrer
        self.next_time = current_time 
        self.clicks_count = clicks_count
        

    # Определяет, что должно произойти во время клика пользователя
    # и возвращает иформацию о клике, сериализованную в строчку
    def make_click (self):
        self.prev_url = self.url
        self.web_path = random.choice (self.web_path.get_links ())
        self.url = str (self.web_path)
        self.click_time = self.next_time
        self.next_time += random.randint (1, 180);
        self.clicks_count -= 1
        return "%s - - [%s] \"GET %s HTTP 1.0\" 200 %d %s %s" % (self.ip,
               datetime.datetime.fromtimestamp(self.click_time).strftime('%d/%b/%Y:%H:%M:%S +0400'),
               self.url,
               random.randint (1000, 20000), 
               self.prev_url,
               self.useragent)


# Пишет лог в файл
# каждые 3 часа он открывает новый файл для записи лога
# каждые сутки - создает новую папку с логами
class LogsWriter (object):
    def __init__ (self, start_time, delta_time):
        self.start_time = start_time
        self.delta_time = delta_time
        self.log_number = 0
        log_date = datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%m')
        try: os.mkdir (log_date) 
        except: pass
        self.log_file = open ("%s/%08d" % (log_date, self.log_number), "w");

    def print_to_log (self, click, time):
        if (self.start_time + self.delta_time < time):
            self.start_time += self.delta_time
            self.log_number += 1
            log_date = datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d')
            try: os.mkdir (log_date) 
            except: pass
            self.log_file.close ()
            log_file_name = "%s/%08d" % (log_date, self.log_number)
            self.log_file = open (log_file_name, "w")
            print "log file", log_file_name, "created"
        print >>self.log_file, click
        


# Класс элемент пути
# Служит для задания графа путей, 
# по которым может ходить пользователь
class PathElement (object):
    def __init__ (self, uri, links = None, is_loop=False):
        self.uri = uri
        self.links = []
        if (links is not None):
            self.links.extend (links)
        self.is_loop = is_loop

    def add_loop (self):
        self.is_loop = True
    
    def add_link (self, new_url):
        self.links.append (new_url)

    def __str__ (self):
        return self.uri

    def __repr__ (self):
        return str(self)

    def get_links (self):
        if (self.is_loop):
            links = list (self.links)
            links.append (self)
            return links
        return self.links

        


# Это специальная версия элемента пути,
# в которой суффикс генерируется случайным образом
class PathElementWithRandomPage (PathElement):
    def __init__ (self, uri, links = None, is_loop = False):
        super(PathElementWithRandomPage, self).__init__ (uri, links, is_loop)

    def __str__ (self):
        return self.uri + str (random.randint (10000, 99999)) + ".html"


# Выводит help на экран
def print_usage ():
    print """
    Generates apache web logs for web statistics researches.    

    Usage:
       ./apache_logs_generator.py -b unixtime -e unixtime -u number

    Where 
        -b unixtime    start time
        -e unixtime    end time
        -u number      number of users
""";    



# Разбор аргументов командной строки
def parse_arguments ():
    parser = OptionParser()
    parser.add_option("-b", dest="begin",       type="int", default=1293829200)
    parser.add_option("-e", dest="end",         type="int", default=1296507600)
    parser.add_option("-u", dest="users_count", type="int", default=100)

    (options, args) = parser.parse_args()

    if (options.begin is None or
        options.end is None or
        options.users_count is None):
        print_usage ()
        sys.exit (0)

    return options


# Моделируем просмотр новостей на news.rambler.ru
rambler_news =  PathElementWithRandomPage ("http://news.rambler.ru/", is_loop=True);
rambler_news_main = PathElement ("http://news.rambler.ru/", links = [rambler_news], is_loop=True);
web_paths = (rambler_news, rambler_news_main)

# Список рефереров сессий
session_referrers = ["http://nova.rambler.ru/search?btnG=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8!&query=rambler.+news",
                     "http://yandex.ru/yandsearch?text=rambler+news&lr=213",
                     "https://www.google.com/search?q=rambler+news&ie=utf-8&oe=utf-8&client=ubuntu&channel=fs",
                     "-", "-", "-"]
# Список возможных юзерагентов
useragents = ["Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
              "Mozilla/5.0 (Windows; I; Windows NT 5.1; ru; rv:1.9.2.13) Gecko/20100101 Firefox/4.0",
              "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"]



if __name__ == "__main__":
    options = parse_arguments ()

    # Сначала создаем множество пользователей, которые сейчас не посещают сайт
    # Пользователи имеют случайный ip и случайный useragent
    inactive_users = set ()
    for i in xrange (options.users_count):
        ip = "%d.%d.%d.%d" % (random.randint (0,255), random.randint (0,255), random.randint (0,255), random.randint (0,255))
        inactive_users.add (User (ip, random.choice (useragents)))

    # Это вероятность, что пользователь активизируется - решит зайти на сайт
    activate_user_probability = 0.01

    # Множество активных пользователей сайта. Сейчас пустое
    active_users = set ()

    # Создаем писатель лога, указав начальное время записи лога и период ротации логов
    log_writer = LogsWriter (options.begin, 10800)
    
    # Проходим посекундно выбранный диапазон времени
    for current_time in xrange (options.begin, options.end):
        # Проверяем наступление ситуации "на сайт пришел еще один визитер"
        if (len (inactive_users) != 0 and random.random () <= activate_user_probability):
            activated_user = inactive_users.pop ()
            activated_user.activate (random.choice (web_paths), 
                                     random.choice (session_referrers), 
                                     current_time,
                                     random.randint (2, 100))
            active_users.add (activated_user)
        
        # Делаем клики активными пользователями тех,
        # кто отстрелялся - переводим в неактивные
        is_inactivated_users = False
        for user in active_users:
            if user.next_time <= current_time:
                log_writer.print_to_log (user.make_click (), current_time)
                if user.clicks_count <= 0:
                    inactive_users.add (user)
                    is_inactivated_users = True
        if is_inactivated_users: active_users.difference_update (inactive_users)
        

