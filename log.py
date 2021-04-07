
from datetime import datetime

def log(level,message):
    print("[%s][%s] %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), level, message))