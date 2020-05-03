from datetime import datetime


def log(s):
    log_string = format(datetime.now(), '%Y-%m-%d %H:%M:%S') + '||' + str(s)
    print(log_string)
    with open('logs.txt', 'a') as file:
        file.write(log_string + "\n")
