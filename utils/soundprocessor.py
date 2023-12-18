from time import time
from database import SoundData, SoundModel
from utils.ini import config
import os

import torch, torchaudio, librosa
import soundfile as sf
from inference import noise_reduct
import noisereduce as nr
from typing import List

httpPrefix = 'http://sound.bs-soft.co.kr/download-single/'
def noise_reduce(target_dir: str, fs: int, model, InSample_PATH: str, OutSample_PATH: str):
    stime = time()
    if config['ml']['device'] == 'gpu':
        noise_reduct(fs, model, InSample_PATH, OutSample_PATH, 'cuda')
    else:
        noise_reduct(fs, model, InSample_PATH, OutSample_PATH, 'cpu')
    
    ftime = time()
    with open(f'{target_dir}/reduc_time.txt', 'w') as f:
        f.write(f'{ftime-stime}')

def voice_seperation(target_dir : str, filename: str, model, num_sep=2):
    inFile = os.path.join(target_dir, filename)
    stime = time()
    est_sources = model.separate_file(inFile)
    for i in range(num_sep):
        outFile = os.path.join(target_dir, f'{filename.split("-")[0]}-sep_ch{i}.wav')
        torchaudio.save(outFile, est_sources[:, :, i].detach().cpu(), 8000)
    ftime = time()
    SoundData().update(recKey=f'{filename.split("-")[0]}',data=SoundModel(sepStatus='Complete',
                                                                          sepprocTime=f'{float(ftime-stime):0.3f}s',
                                                                          sepUrlBase=[f'{httpPrefix}'f'{filename.split("-")[0]}-sep_ch{i}.wav']))
    # with open(f'{target_dir}/sep_time.txt', 'w') as f:
        # f.write(f'{ftime-stime}')
    os.remove(filename) # 왜 현재위치에 ori 파일이 생성되는지 모르겠지만 일단 생성된 것 삭제
    #업데이트 필요set

def voice_enhance(target_dir : str, filename: str, model, num_sep=2):
    inFile = os.path.join(target_dir, filename)
    stime = time()
    noisy, fs = torchaudio.load(inFile)
    enhanced = model.enhance_batch(noisy)
    outFile = os.path.join(target_dir, f'{filename.split("-")[0]}-enhance_ch0.wav')
    torchaudio.save(outFile, enhanced.detach().cpu(), 8000)
    ftime = time()
    with open(f'{target_dir}/enhance_time.txt', 'w') as f:
        f.write(f'{ftime-stime}')

def noise_reduce2(target_dir : str, filename: str, model):
    inFile = os.path.join(target_dir, filename)
    stime = time()
    
    outFile = os.path.join(target_dir, f'{filename.split("-")[0]}-reduc2_ch0.wav')
    noisy, fs = sf.read(inFile)
    reduc = nr.reduce_noise(y=noisy, sr=fs)
    sf.write(outFile, reduc, samplerate=fs, subtype='PCM_16')
    ftime = time()
    with open(f'{target_dir}/reduc2_time.txt', 'w') as f:
        f.write(f'{ftime-stime}')
        
def voice_recognition(filepath: str, ref_voices: List, model, thres = 0.3):
    now_voice = torchaudio.load(filepath)[0].to('cuda')
    prediction = {"max_score": 0, "speaker": -1}
    for i, ref_voice in enumerate(ref_voices):
        score_tensor, _ = model.verify_batch(ref_voice, now_voice)
        score = score_tensor.tolist()[0][0]
        if score > thres and prediction["max_score"] < score:
            prediction["max_score"] = score
            prediction["speaker"] = i
    if prediction["speaker"] != -1:
        print(f"score, prediction : {prediction['max_score']}, {prediction['speaker']}")
    else:
        print("No speaker detected")
    return prediction['speaker']

def stt(filepath: str, processors: dict, model, thres = 0.3, sr = 16000):
    wav_data = librosa.load(filepath, sr=sr)[0]
    tmp = processors['processor'](wav_data, sampling_rate = sr, return_tensors='pt')
    input_values = tmp.input_features.to('cuda')
    with torch.no_grad():
        generated_ids = model.generate(input_values, forced_decoder_ids=processors['forced_decoder_ids'])
    pred = processors['processor'].batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(pred)
    return pred