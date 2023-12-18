from fastapi import APIRouter, File, Body, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import ValidationError
from database import SoundData, SoundModel
from utils.filecheck import get_duration, getStatus
from utils.sys import date
import os, shutil, zipfile
from pydub import AudioSegment
from pathlib import Path
from utils.ini import config, models
import postgres

from utils.soundprocessor import noise_reduce, voice_seperation, voice_enhance, noise_reduce2

BASE_DIR=config['dirs']['upload_path']

router = APIRouter(tags=['Onestop Analysis'])

@router.get('/status')
async def status():
    # status = getStatus()
    status = SoundData().read_all()
    return status

@router.post("/analysis/uploadFile")
async def upload_and_analysis_wavfile(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):
    soundData = SoundModel(duration=get_duration(file.file))
    SoundData().insert(soundData)
    recKey = date(format='%y%m%d%H%M%S')
    target_dir = f'{BASE_DIR}/{recKey[:-2]}/{recKey}'
    os.makedirs(target_dir, exist_ok=True)
    if not(file.filename.endswith('.wav')):
        raise HTTPException(status_code=400, detail="Only WAV files are allowed")
    filename = f'{recKey}-ori_ch0.wav'
    # targetfilename = f'{recKey}-reduc_ch0.wav'
    soundfile = os.path.join(target_dir,filename)
    # targetfile = os.path.join(target_dir,targetfilename)
    with open(soundfile, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    # Path(f'{target_dir}/uploaded.txt').touch() # make file for status checking
    # background_tasks.add_task(noise_reduce, target_dir = target_dir, fs = 8000,
            # model = models['unet_model'], InSample_PATH=soundfile, OutSample_PATH=targetfile)
    background_tasks.add_task(voice_seperation, target_dir=target_dir, filename=filename, model=models['sep_model'])
    # background_tasks.add_task(voice_enhance, target_dir=target_dir, filename=filename, model=models['enhance_model'])
    # background_tasks.add_task(noise_reduce2, target_dir=target_dir, filename=filename, model=models['enhance_model'])
    return {"res": "ok"}

@router.post("/analysis/uploadBlob")
async def upload_and_analysis_blob(file: UploadFile = File(...), background_tasks: BackgroundTasks = BackgroundTasks()):

    recKey = date(format='%y%m%d%H%M%S')
    target_dir = f'{BASE_DIR}/{recKey[:-2]}/{recKey}'
    os.makedirs(target_dir, exist_ok=True)
    blobfile = f'{recKey}-blob_ch0.wav'
    filename = f'{recKey}-ori_ch0.wav'
    targetfilename = f'{recKey}-reduc_ch0.wav'
    soundfile = os.path.join(target_dir,filename)
    blobpath = os.path.join(target_dir,blobfile)
    targetfile = os.path.join(target_dir,targetfilename)
    with open(blobpath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    wav_file = AudioSegment.from_file(file = blobpath)
    wav_file.export(out_f = soundfile, format = "wav")
    Path(f'{target_dir}/uploaded.txt').touch() # make file for status checking
    background_tasks.add_task(noise_reduce, target_dir = target_dir, fs = 8000,
            model = models['unet_model'], InSample_PATH=soundfile, OutSample_PATH=targetfile)
    background_tasks.add_task(voice_seperation, target_dir=target_dir, filename=filename, model=models['sep_model'])
    background_tasks.add_task(voice_enhance, target_dir=target_dir, filename=filename, model=models['enhance_model'])
    background_tasks.add_task(noise_reduce2, target_dir=target_dir, filename=filename, model=models['enhance_model'])
    return {"res": "ok"}


@router.get('/download-single/{wav_file}')
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

@router.get('/download/{wav_tag}')
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

@router.post('/data/memo')
async def update_memo(recKey: str = Body(...), content: str = Body(...)):
    try:
        SoundData().update(recKey= recKey, data= SoundModel(memo=content))
        return content
    except Exception as e:
        return HTTPException(status_code=400, content=e.errors())