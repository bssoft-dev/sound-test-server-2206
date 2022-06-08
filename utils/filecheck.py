import os
from datetime import datetime
from utils.ini import config

import soundfile as sf

BASE_DIR=config['dirs']['sound_path']

def get_duration(file):
    f = sf.SoundFile(file)
    return f'{int(f.frames/f.samplerate)}s'

def sort_fn(e):
    return e['recKey']

def getStatus():
    '''
    It makes json list.
    The keys are recKey, oriStatus, oriUrlBase, bssStatus, bssUrlBase, receivedTime, procTime, memo
    '''
    status = []
    for i in os.listdir(BASE_DIR):
        for recKey in os.listdir(os.path.join(BASE_DIR,i)):
            httpPrefix = f'http://sound.bs-soft.co.kr/download-single/{recKey}'
            nowDir = os.path.join(BASE_DIR,i,recKey)
            files = os.listdir(nowDir)
            if not os.path.exists(f'{nowDir}/uploaded.txt'):
                break
            filelist = {}
            upload_time = os.path.getmtime(f'{nowDir}/uploaded.txt')
            statusByDir = {}
            statusByDir['id'] = f'{recKey}'
            statusByDir['recKey'] = f'{recKey}'
            statusByDir['receivedTime'] = datetime.fromtimestamp(upload_time).strftime('%m-%d %H:%M:%S')
            types = ['ori', 'reduc', 'reduc2', 'sep']
            for type in types:
                filelist[type] = [f for f in files if (f.split('_')[0].endswith(type) and f.endswith('wav'))]
                statusByDir[f'{type}Status'] = 'Complete' if len(filelist[type]) > 0 else 'Ready'
                if type == 'ori':
                    statusByDir[f'{type}UrlBase'] = [f'{httpPrefix}-{type}_ch{i}.wav' for i in range(len(filelist[type]))]
                else:
                    statusByDir[f'{type}UrlBase'] = [f'{httpPrefix}-{type}_ch{i}.wav' for i in range(len(filelist[type]))]
                if statusByDir[f'{type}Status'] == 'Complete' and type != 'ori':
                    procTime = open(f'{nowDir}/{type}_time.txt', 'r').read()
                    statusByDir[f'{type}procTime'] = f'{float(procTime):0.3f}s'
                elif type != 'ori':
                    statusByDir[f'{type}procTime'] = ''
            statusByDir['duration'] = get_duration(f'{nowDir}/{filelist["ori"][0]}')
            statusByDir['memo'] = open(f'{nowDir}/uploaded.txt', 'r').read()
            status.append(statusByDir)
    status.sort(reverse=True, key=sort_fn)
    return status


if __name__ == '__main__':
    print(getStatus())