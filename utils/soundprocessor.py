from time import time
from utils.ini import config
import os

import torchaudio
import soundfile as sf
from inference import noise_reduct
import noisereduce as nr


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
    with open(f'{target_dir}/sep_time.txt', 'w') as f:
        f.write(f'{ftime-stime}')
    os.remove(filename) # 왜 현재위치에 ori 파일이 생성되는지 모르겠지만 일단 생성된 것 삭제

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

