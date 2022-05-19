from fastapi import FastAPI, File, Body, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

import shutil, os
from pathlib import Path
from utils.network import cors
from utils.ini import config
from utils.sys import date
from utils.soundprocessor import noise_reduce
from utils.filecheck import getStatus

app = FastAPI()
cors(app)

BASE_DIR=config['dirs']['sound_path']


@app.on_event("startup")
async def startup():
    os.makedirs(BASE_DIR, exist_ok=True)

    
@app.get('/status')
async def status():
    status = getStatus()
    return status

@app.post("/analysis/uploadFile")
async def upload_and_analysis_wavfile(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):

    today = date(format='%m%d')
    recKey = f"{today}{date(format='%H%M%S')}"
    target_dir = f'{BASE_DIR}/{recKey[:-2]}/{recKey}'
    os.makedirs(target_dir, exist_ok=True)
    if not(file.filename.endswith('.wav')):
        raise HTTPException(status_code=400, detail="Only WAV files are allowed")
    filename = f'{recKey}-ori_ch0.wav'
    targetfilename = f'{recKey}-reduc_ch0.wav'
    soundfile = os.path.join(target_dir,filename)
    targetfile = os.path.join(target_dir,targetfilename)
    with open(soundfile, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    Path(f'{target_dir}/uploaded.txt').touch() # make file for status checking
    background_tasks.add_task(noise_reduce, dir = target_dir, fs = 8000,
            MODEL_PATH = config['ml']['model'], InSample_PATH=soundfile, OutSample_PATH=targetfile)
    return {"res": "ok"}



@app.get('/download-single/{wav_file}')
async def download_single_wavfile_for_specific_type(wav_file):
    '''
    wav_file : recKey-ori_ch1.wav, recKey-bss_ch1.wav
    '''
    recKey = wav_file.split('-')[0]
    target_dir = f'{BASE_DIR}/{recKey[:-2]}/{recKey}'
    target_file = f'{target_dir}/{wav_file}'
    if not os.path.exists(target_file):
        raise HTTPException(status_code=404, detail="No files found")
    return FileResponse(path=target_file, filename=wav_file, media_type='audio/wav')


@app.post('/data/memo')
async def update_memo(recKey: str = Body(...), content: str = Body(...)):
    memofile = f'{BASE_DIR}/{recKey[:-2]}/{recKey}/uploaded.txt'
    try:
        mtime = os.path.getmtime(memofile)
        f = open(memofile, 'w')
        f.write(content)
        f.close()
        os.utime(memofile,(mtime, mtime)) # change modification time to origin value
        return content
    except Exception as e:
        raise HTTPException(500, detail=e)


@app.get("/")
async def main():
    content = """
    <body>
    <form action="/upload/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
    """
    return HTMLResponse(content=content)


if __name__ == '__main__':
    uvicorn.run("app:app", host=config['host']['url'], port=int(config['host']['port']), reload=True, log_level='info')
