#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Автор: Роман Коптев <forest_software@mail.ru>
"""Модуль реализует поиск "особых" групп пользователя социальной сети
ВКонтакте (https://vk.com), в которые не входят его друзья, или в которые
входит ограниченное количество его друзей по данным этой социальной сети.

Модуль может использоваться для импорта функций и как отдельное приложение

Самый простой пример использования модуля:
    
    from unshared_vk.spy import find_unshared_groups
    find_unshared_groups('a_medvedev_01')
    
Здесь a_medvedev_01 - идентификатор одного из пользователей ВКонтакте (ВК),
  который выбран потому, что количество друзей у него приближается к верхнему
  ограничению ВК (около 10000).
  
Тот же пользователь может быть адресован в вызове find_unshared_groups как:
    
    find_unshared_groups('a_medvedev_01')
    find_unshared_groups('id169845376')
    find_unshared_groups('169845376')
    find_unshared_groups(169845376)
    
В функцию find_unshared_groups может быть передано большое число
дополнительных параметров. Например, можно указать минимальное количество
друзей, которое может быть в группе, чтобы она считалась "особой":
    
    find_unshared_groups('a_medvedev_01', members_threshold=5)

Если вызвать функцию таким образом, то особыми будут сочтены группы, в которых
есть до пяти друзей пользователя a_medvedev_01. По умолчанию установлен порог
0. Т.е. особыми считаются группы, в которых совсем нет друзей пользователя.

Можно указать, например, язык, на котором нужно выводить информацию:
    
    find_unshared_groups('a_medvedev_01', lang='ru')
    
По умолчанию данные выводятся на русском языке.

Основные выходные данные - это файл в формате json со списком осбых групп вида:
    
    [
        {
            "name": "Название группы", 
            "gid": "идентификатор группы", 
            "members_count": количество_участников_собщества
        },
        {
        …
        }
    ]

По умолчанию это файл groups.json в рабочем каталоге, но можно указать
использовать другое имя и расположение файла:
    
    find_unshared_groups('a_medvedev_01', json_file='myfile.json')
    
Данные файла всегда сохраняются в кодировке utf-8

Кроме того, можно указать не использовать выходной файл, передав None в
качестве значения параметра json_file

Та же самая выходная информация возвращается функцией как json объект
и может быть использована в программе:
    
    special_groups = find_unshared_groups('a_medvedev_01')
    
Кроме того, в процессе выполнения функция может выводить дополнительную
более подробную информацию на экран, что можно отключить, использовав
параметр silent=True:
    
    find_unshared_groups('a_medvedev_01', silent=True)
    
Такая дополнительная информация выводится только если стандартный поток
вывода направлен на терминал/эмулятор терминала, в частности на ipython.

Также по умолчанию будет осуществляться попытка вывода дополнительных
данных на любое tty устройство (например, /dev/null), что не всегда
желательно.

В процессе работы рисуется простой прогресс бар, но можно задать свою
функцию для фиксирования/отрисовки прогресса. Например, если нужно сделать
прогресс бар с помощью ipwidgets в jupyter notebook:
    
    find_unshared_groups('a_medvedev_01', progress=myfunc)
    
Функция myfunc будет периодически вызываться с параметром status,
который представляет собой число с плавающей точкой в интервале от 0 до 100.
Это число примерно указывает процент завершенности получения и анализа
данных.

Среди других доступных опций:
    * Возможность указать, генерировать ли исключительную ситуацию, если
      запрошенного пользователя не существует, или просто выдать
      сообщение об ошибке в stderr и вернуть пустой списко специальных
      групп (параметр raise_nouser)
    * Можно изменить token, с которым идет обращение к API ВК (token)
    * Можно задать задержки таймаутов при соединении и получении данных,
      задержки при повторах в случае ответов сервера с ошибкой и количество
      повторов (параметры request_delay, request_repeat, request_timeout)
    * Можно также изменить ряд настроек запросов к API ВК, но не рекомендуется
      этого делать, т.к. в таком случае с большой вероятностью будут
      происходить разные ошибки, связанные с ограничениями сети ВК и API ВК.
      
Реализация использованных алгоритмов проверялась в среде Anaconda bash/ipython
на Windows 10. Работоспособность проверена на пользователях ВК с большим
количеством друзей/сообществ. Учтены многие ограничения ВК и возможные ошибки
передачи данных. Алгоритмы расчитаны на работу при следующих основных
ограничениях:
    
    Максимальное количество друзей пользователя: 10 000
    Максимальное количество сообществ: 5 000
    Метод friends.get позволяет получать данные не более чем о 5 000
       пользователей за обращение
    Метод groups.get позволяет получать данные не более чем о 1 000
       групп за одно обращение
    Метод groups.isMember позволяет проверять вступили ли в группу
       пользователи, но не более чем для 500 пользователей за обращение
    Метод execute позволяет выполнять сразу несколько запросов к API (но
       не более 25) и выполнять вычисления и обработку данных на стороне
       серверов ВК (но есть ограничения на количество операций)
    Существуют ограничения на объемы передаваемых данных, накладываемые API
       ВК и протоколами передачи данных (5 Мб).
    Для ключа доступа пользователя возможно обращаться к API ВК не более
       3 раз в секунду.
    При передаче данных наиболее возможны ошибки таймаута соединения/чтения
       и сбой DNS lookup
       
Обработка данных по возможности вынесена на сторону серверов ВК, для чего
использованы запросы к методу execute API и скрипты на VKScript. Используются
только post запросы, потому что с их помощью можно передавать большие объемы
данных, чем при использовании get запросов.

Более подробные данные по API ВК приведены по ссылке:
    https://vk.com/dev/manuals

Модуль можно использовать из командной строки. Получить информацию по
опциям командной строки и о версии приложения можно стандартным способом:
    
    ./spy.py -h
    ./spy.py --help
    
    ./spy.py -v
    ./spy.py--version
    
Позиционным параметром можно указать идентификатор пользователя в любом
из упомянутых виде. Остальные параметры:
    
-------------------------------------------------------------------------------
Использование: spy.py [-v] [-h] [-t [TOKEN]]
                      [--request-repeat [REQUEST_REPEAT]]
                      [--request-delay [REQUEST_DELAY]]
                      [--request-timeout1 [REQUEST_TIMEOUT1]]
                      [--request-timeout2 [REQUEST_TIMEOUT2]]
                      [--output-json-file [OUTPUT_JSON_FILE]]
                      [--group-step [GROUP_STEP]]
                      [--friend-step [FRIEND_STEP]]
                      [--friend-load-step [FRIEND_LOAD_STEP]]
                      [--friend-is-member-step [FRIEND_IS_MEMBER_STEP]]
                      [--members-threshold [MEMBERS_THRESHOLD]]
                      [-i [INTERACTIVE]] [--silent [SILENT]]
                      [user_id]

Поиск особых групп пользователя ВК

Позиционные аргументы:
  user_id               id пользователя ВК (По умолч.: None)

Опциональные аргументы:
  -v, --version         Показать версию программы и выйти.
  -h, --help            Показать данное справочное сообщение и выйти.
  -t [TOKEN], --token [TOKEN]
                        ВК token (По умолч.: 7b23e40ad10e08d3b7a8ec0956f2c5791
                        0c455e886b480b7d9fb59859870658c4a0b8fdc4dd494db19099)
  --request-repeat [REQUEST_REPEAT]
                        число повторений запросов (По умолч.: 10)
  --request-delay [REQUEST_DELAY]
                        задержка между запросами при ошибках (По умолч.: 0.5)
  --request-timeout1 [REQUEST_TIMEOUT1]
                        connection timeout (По умолч.: 7)
  --request-timeout2 [REQUEST_TIMEOUT2]
                        read timeout (По умолч.: 7)
  --output-json-file [OUTPUT_JSON_FILE]
                        выходной json файл (По умолч.: groups.json)
  --group-step [GROUP_STEP]
                        количество групп в одном запросе (рек. 1000) (По
                        умолч.: 1000)
  --friend-step [FRIEND_STEP]
                        количество друзей в одном запросепри запросе основной
                        информации пользователя(рек. 5000) (По умолч.: 5000)
  --friend-load-step [FRIEND_LOAD_STEP]
                        количество друзей в одном запросепри запросе друзей
                        для анализа специфичности группы(рек. 5000) (По
                        умолч.: 5000)
  --friend-is-member-step [FRIEND_IS_MEMBER_STEP]
                        количество друзей в одном запросепри запросе друзей
                        для метода ismember(рек. 500) (По умолч.: 500)
  --members-threshold [MEMBERS_THRESHOLD]
                        порог специфичности (По умолч.: 0)
  -i [INTERACTIVE], --interactive [INTERACTIVE]
                        Интерактивный ввод данных (По умолч.: False)
  --silent [SILENT]     Интерактивный ввод данных (По умолч.: False)
-------------------------------------------------------------------------------

Можно указать использовать интерактивный ввод данных с помощью опции -i:
    
    .spy.py -i
    .spy.py --interactive
    
Тогда со стандартного потока ввода будет предложено ввести идентификатор
пользователя и порог специфичности (members-threshold). Остальные параметры
нельзя ввести интерактивно.
Параметры, введенные интерактивно, перекроют параметры, указанные в
командной строке.

Если не задан интерактивный ввод данных, не указан идентификатор пользователя
в командной строке, не указаны специальные опции, приводящие к завершению
работы приложения, такие как --help и --version, будет запущена тестовая
обработка одного из пользователей.

"""

__version__ = '1.0'
__all__ = [
    'find_unshared_groups',
    'do_execute_request',
    'simple_progress'
]

import colorama
from colorama import Fore, Style
import json
import requests
import sys
from time import sleep

##########################
# Значения по умолчанию:
##########################

TOKEN = '7b23e40ad10e08d3b7a8ec0956f2c57910c455e886b480b7d9fb59859870658c4'\
        'a0b8fdc4dd494db19099'
        # Ключ доступа API ВК, см. https://vk.com/dev/access_token
        
API_VERSION = '5.80' # Изменение данного параметра может потребовать изменения
                     # кода модуля
                     
MAX_REPEAT_REQUESTS = 10 # Количество повторов запросов при сбоях и ошибках
                         # по умолчанию
                         
REQUEST_DELAY = 0.5      # Задержка после ошибок

REQUEST_TIMEOUT = (7, 7) # None, integer или tuple of integer
                         # Задержки timeout
                         # None - ждать неограниченно
                         # Одно число - одинаковая задержка соединения/чтения
                         # Кортеж двух чисел - задержка соединения и чтения
                         # Рекомендуется задать не менее 3

REQUEST_BASE_PATH = 'https://api.vk.com/method'
REQUEST_EXECUTE_PATH = f'{REQUEST_BASE_PATH}/execute' # Адреса запросов API ВК

DEFAULT_OUTPUT_JSON_FILE = 'groups.json' # Путь к выходному файлу по умолчанию

GROUP_STEP = 1000   # Сколько групп читать в запросе groups.get
FRIEND_STEP = 5000  # Число друзей в запросе friends.get при получении общих
                    #   данных о пользователе
                    
FRIEND_LOAD_STEP = 5000 # Число друзей в запросе friends.get при получении
                        # данных по группе
                        
FRIEND_IS_MEMBER_STEP = 500 # Число друзей в запросе groups.isMember

MEMBERS_THRESHOLD = 0 # Порог друзей, когда группа еще считается "особой"

DEFAULT_LANG = 'ru' # Язык интерфейса

SILENT = False # "Молчаливый" режим: не выводить дополнительных данных
               # в стандартный поток вывода

##########################################
# Шаблоны VKScript для запросов execute:
##########################################

# VKScript запроса на получение общих данных о пользователе
GET_MAIN_USER_INFO_REQUEST_CODE = """
    var user_id = "{user_id}";
    var group_step = {group_step};
    var friend_step = {friend_step};
    
    var user = API.users.get({{user_ids: user_id}});
    var uid = user[0].id;
    
    var groups = API.groups.get({{user_id: uid, count: group_step}});
    
    var i = group_step;
    var count = groups.count;
    
    while(i < count)
    {{
      groups.items = groups.items
        + API.groups.get({{user_id:uid, count: group_step, offset: i}})
          .items;
      i = i + group_step;
    }}
    
    var friends = API.friends.get({{user_id:uid, count: friend_step}});
    
    i = friend_step;
    count = friends.count;
    
    while(i < count)
    {{
      friends.items = friends.items
        + API.friends.get({{user_id:uid, count: friend_step, offset: i}})
          .items;
      i = i + friend_step;
    }}
    
    return {{user: user, groups: groups, friends: friends}};
"""

# VKScript запроса на проверку особенности группы:
CHECK_SPECIAL_GROUP_REQUEST_CODE = """
    var user_id = "{user_id}";
    var group_id = "{group_id}";
    var members_threshold = {members_threshold};
    var friend_load_step = {friend_load_step};
    var friend_is_member_step = {friend_is_member_step};
    
    var user = API.users.get({{user_ids: user_id}});
    var uid = user[0].id;
    
    var friends = API.friends.get({{user_id:uid, count: friend_load_step}});
    
    var i = friend_load_step;
    var count = friends.count;
    
    while(i < count)
    {{
      friends.items = friends.items
        + API.friends.get({{user_id:uid, count: friend_load_step, offset: i}})
          .items;
      i = i + friend_load_step;
    }}
    
    var sum = 0;
    var slice = 0;
    count = friends.length;
    
    while(slice < count)
    {{
      var member_flags =
        API.groups.isMember({{group_id: group_id,
                             user_ids:
                                 friends.items.slice(slice,
                                   slice + friend_is_member_step)
                             }}
                           )@.member;
    
      sum = sum + ((member_flags+"").split(0)+"").split(1).length-1;
      
      slice = slice + friend_is_member_step;
    }}
    
    
    return {{user: user,
             special_group: (sum <= members_threshold),
             friends_in_group: sum,
             group: API.groups.getById({{group_id: group_id,
               fields: ["members_count"]}})
             }};
"""

###################################
# Объявления функций
###################################

def is_in_ipython():
    """Проверка, что ввод/вывод происходит в среде IPython"""
    try:
        __IPYTHON__
        return True
    except NameError:
        return False

    
def is_a_tty():
    """Проверка, что вывод осуществляется на устройство tty"""
    return sys.stdout.isatty()


def simple_progress(status):
    """Простая процедура отображения прогресса в текстовом терминале.
    Входные параметры:
        status: число с плавающей точкой в диапазоне от 0 до 100,
          характеризующее степень завершенности процесса
          
    Выход: None
    
    """
    
    def write(str):
        print(str, end='', flush=True)
    
    if is_in_ipython() or is_a_tty():
        if status < 0: status = 0
        if status > 100: status = 100
        
        toolbar_width = 40

        initial_string = f'[{" " * toolbar_width}] {round(status):>3}%'
        count = int(status * toolbar_width / 100)
        
        write('\r')
        write(initial_string)
        write('\r[')       
        write('\u25A0' * count)
        if status == 100:
            write('\n\n')


def do_execute_request(code, lang=DEFAULT_LANG, *,
                       token=TOKEN,
                       request_delay=REQUEST_DELAY,
                       request_repeat=MAX_REPEAT_REQUESTS,
                       request_timeout=REQUEST_TIMEOUT,
                       **kwarg):
    """Выполнить запрос к методу execute API ВК
    
    Входные параметры:
        code:   Текст VKScript для выполнения
        lang:   Язык, на котором выдавать выходную информацию
        token:  Ключ доступа API ВК
        request_delay:  Задержка между запросами при ошибках и сбоях
        request_repeat: Число повторений запросов при ошибках и сбоях
        request_timeout: Задержки timeout
                         None - ждать неограниченно
                         Одно число - одинаковая задержка соединения/чтения
                         Кортеж двух чисел - задержка соединения и чтения
                         Рекомендуется задать не менее 3
                         
    Выход:
        Часть ответа request внутри секции response
        
    В случае ошибок могут генерироваться исключительные ситуации
    requests.RequestException
    
    """
    response = None
    for i in range(request_repeat):
        try:
            response = requests.post(
                REQUEST_EXECUTE_PATH,
                data=dict(
                        access_token=token,
                        v=API_VERSION,
                        lang=lang,
                        code=code
                        ),
                timeout=request_timeout
                )
#        except requests.exceptions.ReadTimeout as e:
#            print('Произошел таймаут при чтении', file=sys.stderr)
#            response = e
#        except requests.exceptions.ConnectTimeout as e:
#            print('Произошел таймаут при соединении', file=sys.stderr)
#            response = e
#        except requests.exceptions.ConnectionError as e:
#            print('Произошла ошибка DNS lookup', file=sys.stderr)
#            response = e
        except requests.RequestException as e:
            print(f'{type(e).__name__}: {e}', file=sys.stderr)
            response = e
        if not isinstance(response, Exception) \
           and not 'error' in response.json():
               break
        sleep(request_delay)
        
    if isinstance(response, Exception):
        raise response
    if 'error' in response.json():
        raise requests.RequestException(
                f'VK request error: {response.json()["error"]["error_code"]}. '
                f'Message: {response.json()["error"]["error_msg"]}'
                )
    
    return response.json()['response']


def find_unshared_groups(user_id, *,                        
                         members_threshold=MEMBERS_THRESHOLD,
                         json_file=DEFAULT_OUTPUT_JSON_FILE,
                         lang=DEFAULT_LANG,
                         token=TOKEN,
                         silent=SILENT,
                         raise_nouser=True,
                         progress=simple_progress,                         
                         group_step=GROUP_STEP,
                         friend_step=FRIEND_STEP,
                         friend_load_step=FRIEND_LOAD_STEP,
                         friend_is_member_step=FRIEND_IS_MEMBER_STEP,
                         request_delay=REQUEST_DELAY,
                         request_repeat=MAX_REPEAT_REQUESTS,
                         request_timeout=REQUEST_TIMEOUT,
                         **kwarg):
    """Поиск "особых" групп указанного пользователя. Групп,
    в которых состоит ограниченное количество его друзей.
    
    Входные параметры:
        user_id:           идентификатор пользователя в виде строки/числа
                           Например: 'eshmargunov', 'id171691064',
                                     '171691064', 171691064
        members_threshold: Максимально число пользователей, для которого группа
                           еще считается особой
        json_file:         файл для сохранения списка данных об особых группах
                           Формат json, кодировка utf-8
                           Если указано значение None выходной файл не
                           формируется
        lang:              язык вывода выходных данных
                           (см. https://vk.com/dev/api_requests)
        token:             ключ доступа API ВК
        silent:            "молчаливый" режим - True означает не выводить
                           дополнительную информацию в стандартный поток вывода
        raise_nouser:      при значении True, если пользователя с указанным
                           идентификатором не существует, будет сгенерирована
                           исключительная ситуация ValueError. При значении
                           False будет выведено сообщение об ошибке в
                           стандартный поток ошибок и функция вернет пустой
                           список групп. В выходной файл также будет сохранен
                           пустой списко групп.
        request_delay:     задержка между запросами при ошибках и сбоях
        request_repeat:    максимальное число повторений запросов при
                           ошибках и сбоях
        request_timeout:   задержки timeout
                           None - ждать неограниченно
                           Одно число - одинаковая задержка соединения/чтения
                           Кортеж двух чисел - задержка соединения и чтения
                           Рекомендуется задать не менее 3
                         
            Следующие параметры не рекомендуется изменять:
        group_step:       число групп читать в запросе groups.get
        friend_step:      число друзей в запросе friends.get при получении
                          общих данных о пользователе
        friend_load_step: число друзей в запросе friends.get при получении
                          данных по группе
        friend_is_member_step: число друзей в запросе groups.isMember
        
    Возвращаемое значение:
        
        Объект json со списком особых групп в кодировке utf-8:
            
            [
                {
                    "name": "Название группы", 
                    "gid": "идентификатор группы", 
                    "members_count": количество_участников_собщества
                },
                {
                …
                }
            ]
            
        Файл такого же формата может сохраняться на носитель информации в
        соответствии с установкой параметра json_file
        
    Функция может генерировать исключительные ситуации:
        - При отсутсвии пользователя с указанным идентификатором и
          соответсвующей установке параметра raise_nouser (ValueError)
        - Исключительные ситуации Request при повторах ошибочных ответов
          серверов ВК или сбоях передачи данных, ошибках DNS lookup.
        
    """
    
    if not(is_in_ipython() or is_a_tty()): silent = True
    
    progress(0)
    
    code = GET_MAIN_USER_INFO_REQUEST_CODE.format(
                user_id=user_id,
                group_step=group_step,
                friend_step=friend_step
                )
    user_info = do_execute_request(code, lang, token=token,
                                   request_delay=request_delay,
                                   request_repeat=request_repeat,
                                   request_timeout=request_timeout)
    
    special_groups = []
    
    if not user_info['user']:
        progress(100)
        if(raise_nouser):
            raise ValueError(f'Пользователя {user_id} не существует')
        else:
            print(f'Пользователя {user_id} не существует', file=sys.stderr) 
    elif 'deactivated' in user_info['user'][0]:
        progress(100)
        if(raise_nouser):
            raise ValueError(f'Пользователь {user_id} деактивирован '
                             f'({user_info["user"][0]["deactivated"]})')
        else:
            print(f'Пользователь {user_id} деактивирован '
                  f'({user_info["user"][0]["deactivated"]})',
                  file=sys.stderr) 
    else:
        
        progress_status = (user_info['groups']['count'] + 1) / 100
        progress_step = 1 / progress_status
        progress(progress_status)

        if not silent:
            print(f'\n{Fore.RED}Пользователь {user_id}:{Style.RESET_ALL}\n'
                  f'\t{user_info["user"][0]["last_name"]}, '
                  f'{user_info["user"][0]["first_name"]}\n'
                  f'\t(id: {user_info["user"][0]["id"]})\n'
                  f'Состоит в {user_info["groups"]["count"]} группах, '
                  f'{user_info["friends"]["count"]} друзей\n',
                  flush=True)
        
        for group in user_info['groups']['items']:
            code = CHECK_SPECIAL_GROUP_REQUEST_CODE.format(
                        user_id=user_id,
                        group_id=group,
                        members_threshold=members_threshold,
                        friend_load_step=friend_load_step,
                        friend_is_member_step=friend_is_member_step
                        )
            group_info = do_execute_request(code, lang,
                                            token=token,
                                            request_delay=request_delay,
                                            request_repeat=request_repeat,
                                            request_timeout=request_timeout)
            
            progress_status += progress_step
            progress(progress_status)
            
            if(group_info['special_group']):
                special_groups.append(dict(
                        name = group_info['group'][0]['name'],
                        gid = group_info['group'][0]['id'],
                        members_count = group_info['group'][0]['members_count']
                        ))
                if not silent:
                    print(f'\n{Fore.CYAN}Группа:{Style.RESET_ALL}\n'
                          f'{Fore.GREEN}'
                          f'\t{group_info["group"][0]["name"]}\n'
                          f'{Fore.YELLOW}'
                          f'\t{group_info["group"][0]["screen_name"]} '
                          f'{Fore.RED}'
                          f'(id: {group_info["group"][0]["id"]})\n'
                          f'{Style.RESET_ALL}'
                          f'\t{group_info["group"][0]["members_count"]}'
                          f' членов\n'
                          f'\t{group_info["friends_in_group"]} друзей\n',
                          flush=True)
                    
        progress(100)
                
        if not silent:
            print(f'{Fore.RED}Всего групп: '
                  f'{user_info["groups"]["count"]}{Style.RESET_ALL}')
            print(f'{Fore.RED}Из них особых групп: '
                  f'{len(special_groups)}{Style.RESET_ALL}')
            
    if json_file:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(special_groups, f,
                      indent=4, ensure_ascii=False)
    
    return json.dumps(special_groups, indent=4, ensure_ascii=False)

# Инициализация colorama, которая используется 
# для управления выводом эскейп последоваетльностей управления терминалом
# и перенаправлением их в Windows Api вызовы. Чтобы не заниматься этим вручну.
# Используется для цветного вывода
if is_in_ipython():
    colorama.init(convert=False, strip=False)
else:
    colorama.init()


if __name__ == '__main__':
    
    # Разбор командной строки
    
    import argparse
    
    def str2bool(value):
        """Форматирование булевых значений командной строки"""
        if value.lower() in \
            ('yes', 'true', 't', 'y', '1', 'д', 'да', 'истина'):
            return True
        elif value.lower() in \
            ('no', 'false', 'f', 'n', '0', 'н', 'нет', 'ложь'):
            return False
        else:
            raise argparse.ArgumentTypeError('Ожидалось логическое значение')
            
    def str2timeout(value):
        """Форматирование задания timeout в командной строке"""
        if value.strip() == 'None':
            return 'None'
        elif value.strip().replace('.','').isnumeric():
            return value
        else:
            raise argparse.ArgumentTypeError(
                    'Ожидалось None или число с плавающей точкой')
            
    class MyArgumentDefaultsHelpFormatter(argparse.HelpFormatter):
        """Это копия стандартного argparse.ArgumentDefaultsHelpFormatter,
        измененного в целях русификации вывода
        
        """
        def _get_help_string(self, action):
            help = action.help
            if '%(default)' not in action.help:
                if action.default is not argparse.SUPPRESS:
                    defaulting_nargs = [argparse.OPTIONAL,
                                        argparse.ZERO_OR_MORE]
                    if action.option_strings or action.nargs \
                          in defaulting_nargs:
                        help += ' (По умолч.: %(default)s)'
            return help
        
        
            
    class MyUsageHelpFormatter(MyArgumentDefaultsHelpFormatter):
        """Дополнительный класс для русификации сообщения usage
        при выводе справки по опциям командной строки
        
        """
        def add_usage(self, usage, actions, groups, prefix=None):
            if prefix is None:
                prefix = 'Использование: '
            return super(MyUsageHelpFormatter, self) \
                .add_usage(usage, actions, groups, prefix)

    
    parser = argparse.ArgumentParser(
            description='Поиск особых групп пользователя ВК',
            add_help=False,
            formatter_class=MyUsageHelpFormatter)
    
    parser._positionals.title = 'Позиционные аргументы'
    parser._optionals.title = 'Опциональные аргументы'
    
    parser.add_argument('-v', '--version', action='version',
            version=f'%(prog)s __version__',
            help="Показать версию программы и выйти.")
    parser.add_argument('-h', '--help', action='help',
                        default=argparse.SUPPRESS,
                        help='Показать данное справочное сообщение и выйти.')
    
    parser.add_argument('user_id', metavar='user_id', type=str, nargs='?',
                    help='id пользователя ВК')
    parser.add_argument('-t', '--token', nargs='?', type=str,
                        const=TOKEN, default=TOKEN,
                        help='ВК token')
    parser.add_argument('--request-repeat', nargs='?', type=int,
                        const=MAX_REPEAT_REQUESTS, default=MAX_REPEAT_REQUESTS,
                        help='число повторений запросов')
    parser.add_argument('--request-delay', nargs='?', type=float,
                        const=REQUEST_DELAY, default=REQUEST_DELAY,
                        help='задержка между запросами при ошибках')
    if REQUEST_TIMEOUT is None:
        parser.add_argument('--request-timeout1', nargs='?', type=str2timeout,
                            const='None', default='None',
                            help='connection timeout')
        parser.add_argument('--request-timeout2', nargs='?', type=str2timeout,
                            const='None', default='None',
                            help='read timeout')
    elif isinstance(REQUEST_TIMEOUT, tuple):
        parser.add_argument('--request-timeout1', nargs='?', type=str2timeout,
                            const=REQUEST_TIMEOUT[0],
                            default=REQUEST_TIMEOUT[0],
                            help='connection timeout')
        parser.add_argument('--request-timeout2', nargs='?', type=str2timeout,
                            const=REQUEST_TIMEOUT[1],
                            default=REQUEST_TIMEOUT[1],
                            help='read timeout')
    else:
        parser.add_argument('--request-timeout1', nargs='?', type=str2timeout,
                            const=REQUEST_TIMEOUT, default=REQUEST_TIMEOUT,
                            help='connection timeout')
        parser.add_argument('--request-timeout2', nargs='?', type=str2timeout,
                            const=REQUEST_TIMEOUT, default=REQUEST_TIMEOUT,
                            help='read timeout')
    parser.add_argument('--output-json-file', nargs='?', type=str,
                        const=DEFAULT_OUTPUT_JSON_FILE,
                        default=DEFAULT_OUTPUT_JSON_FILE,
                        help='выходной json файл')
    parser.add_argument('--group-step', nargs='?', type=int,
                        const=GROUP_STEP,
                        default=GROUP_STEP,
                        help='количество групп в одном запросе (рек. 1000)')
    parser.add_argument('--friend-step', nargs='?', type=int,
                        const=FRIEND_STEP,
                        default=FRIEND_STEP,
                        help='количество друзей в одном запросе' \
                             'при запросе основной информации пользователя'\
                             '(рек. 5000)')
    parser.add_argument('--friend-load-step', nargs='?', type=int,
                        const=FRIEND_LOAD_STEP,
                        default=FRIEND_LOAD_STEP,
                        help='количество друзей в одном запросе' \
                             'при запросе друзей для анализа '\
                             'специфичности группы'\
                             '(рек. 5000)')
    parser.add_argument('--friend-is-member-step', nargs='?', type=int,
                        const=FRIEND_IS_MEMBER_STEP,
                        default=FRIEND_IS_MEMBER_STEP,
                        help='количество друзей в одном запросе' \
                             'при запросе друзей для метода ismember'\
                             '(рек. 500)')
    parser.add_argument('--members-threshold', nargs='?', type=int,
                        const=MEMBERS_THRESHOLD,
                        default=MEMBERS_THRESHOLD,
                        help='порог специфичности')
    parser.add_argument('-i', '--interactive', type=str2bool, nargs='?',
                        const=True, default=False,
                        help="интерактивный ввод данных")
    parser.add_argument('--silent', type=str2bool, nargs='?',
                        const=True, default=SILENT,
                        help="не выводить дополнительные данные в stdout")
            
    args = vars(parser.parse_args())
    
    if args['user_id'] is None:
        user_id = None
    else:
        user_id = args['user_id']
    
    members_threshold = args['members_threshold']
    
    params = {}
    
    if args['output_json_file'].strip() == 'None':
        params['json_file'] = None
    else:
        params['json_file'] = args['output_json_file']
        
    for item in ('group_step', 'friend_step', 'friend_load_step',
                 'friend_is_member_step', 'silent', 'token',
                 'request_delay', 'request_repeat'):
        params[item] = args[item]
    
    if args['request_timeout1'] == 'None' \
       and args['request_timeout2'] == 'None':
        params['request_timeout'] = None
    elif args['request_timeout1'] == 'None':
        params['request_timeout'] = float(args['request_timeout2'])
    elif args['request_timeout2'] == 'None':
        params['request_timeout'] = float(args['request_timeout1'])           
    else:
        params['request_timeout'] = (float(args['request_timeout1']),
                                     float(args['request_timeout2']))
    
    if args['interactive']:
        
        # Ввод в режиме интерактивного ввода
        
        print(f'{Fore.GREEN}Введите данные для работы программы:'
              f'{Style.RESET_ALL}')
        
        while True:
            user_id = input('Введите id пользователя (например, '
                        'a_medvedev_01, id169845376 или 169845376):').strip()
            if user_id != '': break
            print('Неверный ввод')
        
        while True:
            members_threshold = input(
                f'Введите порог специфичности ({MEMBERS_THRESHOLD}):').strip()
            if members_threshold == '':
                members_threshold = MEMBERS_THRESHOLD
                break
            if members_threshold.isnumber():
                members_threshold = int(members_threshold)
                break
            print('Неверный ввод')

        find_unshared_groups(user_id,
                             members_threshold=members_threshold,
                             **params)
    elif not user_id is None:
        
        # Вызов функции для пользователя, указанного в командной строке
        
        find_unshared_groups(user_id,
                             members_threshold=members_threshold,
                             **params)
    else:
        
        # Тестовые вызовы, если не задан пользователь в командной строке
        # и не используется интерактивный режим
        
        if not params['silent'] and (is_in_ipython() or is_a_tty()):
            print(f'{Fore.GREEN}Пользователь для примера{Style.RESET_ALL}')
            
        #find_unshared_groups('romikforest')
        #find_unshared_groups('id180784333', members_threshold=10)
        #find_unshared_groups(180784333)
        
        #find_unshared_groups('eshmargunov')
        #find_unshared_groups('id171691064')
        #find_unshared_groups(171691064)
        
        # > 9000 друзей:
        find_unshared_groups('a_medvedev_01',
                             members_threshold=members_threshold,
                             **params)
        #find_unshared_groups('id169845376')
        #find_unshared_groups(169845376)
