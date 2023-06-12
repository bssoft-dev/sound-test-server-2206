from datetime import datetime

try:
    from pytz import timezone    
    def date(format='%Y-%m-%d'):
        return datetime.now(timezone('Asia/Seoul')).strftime(format)
except ModuleNotFoundError:
    def date(format='%Y-%m-%d'):
        return datetime.now().strftime(format)
    pass

def stime(sformat='%Y-%m-%d %H:%M:%S'):
    return datetime.now(timezone('Asia/Seoul')).strftime(sformat)