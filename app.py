from fastapi import FastAPI, File, Body, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
import uvicorn

import zipfile
import shutil, os, sys
from pathlib import Path
from utils.network import cors
from utils.log_conf import app_log_conf
from utils.ini import (config, models, stt_processors, ref_voice_shcho, ref_voice_bsjang)
from utils.sys import date
from utils.soundprocessor import noise_reduce, stt, voice_seperation, voice_enhance, noise_reduce2, voice_recognition
from utils.filecheck import getStatus


app = FastAPI(
    title="BSsoft 1ch Sound Processing Test",
    description="BS소프트의 1채널 사운드처리 테스트 API 페이지입니다.",
    version="0.1.0"
)

cors(app)

BASE_DIR=config['dirs']['upload_path']


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
    background_tasks.add_task(noise_reduce, target_dir = target_dir, fs = 8000,
            model = models['unet_model'], InSample_PATH=soundfile, OutSample_PATH=targetfile)
    background_tasks.add_task(voice_seperation, target_dir=target_dir, filename=filename, model=models['sep_model'])
    background_tasks.add_task(voice_enhance, target_dir=target_dir, filename=filename, model=models['enhance_model'])
    background_tasks.add_task(noise_reduce2, target_dir=target_dir, filename=filename, model=models['enhance_model'])
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

@app.post("/analysis/whoyouare")
async def judge_who_you_are(file: UploadFile = File(...)):
    deviceid = file.filename.split('-')[0]
    if "wav" not in file.filename[-3:]:
        raise HTTPException(status_code=422, detail="File extension is not allowed")
    folder = os.path.join(BASE_DIR, deviceid)
    os.makedirs(folder, exist_ok=True)
    soundfile = os.path.join(folder,file.filename)
    with open(soundfile, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    res = voice_recognition(soundfile, ref_voices=[ref_voice_shcho, ref_voice_bsjang], model=models['voice_rec_model'])
    return {"file": file.filename, "result": res}

@app.post("/analysis/stt/{datatype}")
async def stt_anal(datatype, file: UploadFile = File(...)):
    deviceid = file.filename.split('-')[0]
    if "wav" not in file.filename[-3:]:
        raise HTTPException(status_code=422, detail="File extension is not allowed")
    folder = os.path.join(BASE_DIR, deviceid)
    os.makedirs(folder, exist_ok=True)
    soundfile = os.path.join(folder,file.filename)
    with open(soundfile, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    res = stt(soundfile, datatype, stt_processors, models['stt_model'])
    return {"file": file.filename, "result": res}

@app.post("/analysis/id-and-stt")
async def id_and_stt_anal(datatype = 'wavfile', file: UploadFile = File(...)):
    deviceid = file.filename.split('-')[0]
    if "wav" not in file.filename[-3:]:
        raise HTTPException(status_code=422, detail="File extension is not allowed")
    folder = os.path.join(BASE_DIR, deviceid)
    os.makedirs(folder, exist_ok=True)
    soundfile = os.path.join(folder,file.filename)
    with open(soundfile, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    speaker = voice_recognition(soundfile, ref_voices=[ref_voice_shcho, ref_voice_bsjang], model=models['voice_rec_model'])
    if speaker == 0:
        speaker = "성훈"
    elif speaker == -1:
        speaker = "??"
    res = stt(soundfile, datatype, stt_processors, models['stt_model'])
    return {"file": file.filename, "result": res, "speaker": speaker}

@app.get('/download/{wav_tag}')
async def download_wavfiles_for_specific_type(wav_tag):
    '''
    wav_tag : recKey-sep 
    '''
    [recKey, wav_type] = wav_tag.split('-')
    target_dir = f'{BASE_DIR}/{recKey[:-2]}/{recKey}'
    sfiles = os.listdir(target_dir)
    wavfiles = [ file for file in sfiles if ((file.split('_')[0].endswith(wav_type)) and (file.endswith('wav'))) ]
    if len(wavfiles) < 1:
        raise HTTPException(status_code=404, detail="No files found")
    # lastfiles = sorted(wavfiles)[-4:] # 가장 최신 4개만 뽑음
    lastfiles = wavfiles
    with zipfile.ZipFile(f"tmp/{wav_tag}.zip", 'w') as my_zip: #zip으로 묶음
        for i in lastfiles:
            my_zip.write(f'{target_dir}/{i}', i)
        my_zip.close()
    return FileResponse(path=f"tmp/{wav_tag}.zip", filename=f"wavfiles_{recKey}.zip", media_type='application/zip')

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
    uvicorn.run("app:app", host=config['host']['url'], port=int(config['host']['port']), reload=True, log_config=app_log_conf, log_level='info')
