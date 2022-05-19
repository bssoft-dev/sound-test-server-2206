import sys
from time import time
from utils.ini import config

sys.path.insert(1, config['dirs']['ml_path'])
if config['ml']['device'] == 'cpu':
    from Step4_enhance_use_cpu import DEVICE, noise_reduct
else:
    from Step4_enhance_use_gpu import DEVICE, noise_reduct


def noise_reduce(dir: str, fs: int, MODEL_PATH: str, InSample_PATH: str, OutSample_PATH: str):
    stime = time()
    noise_reduct(fs, MODEL_PATH, InSample_PATH, OutSample_PATH)
    ftime = time()
    with open(f'{dir}/reduc_time.txt', 'w') as f:
        f.write(f'{ftime-stime}')


