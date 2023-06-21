import configparser, sys
import torch, torchaudio

from transformers import pipeline
from transformers import WhisperProcessor, WhisperForConditionalGeneration

config = configparser.ConfigParser()
config.read('/bssoft/config.ini')

sys.path.insert(1, config['dirs']['ml_path'])
from model.unet_wave import UNet_Wave

stt_model_path = "openai/whisper-medium"

if config['ml']['device'] == 'gpu':
    device = 'cuda'
else :
    device = 'cpu'

models = {}

models['unet_model'] = UNet_Wave().to(device)
dict_model = torch.load(config['ml']['model'], map_location=device)
models['unet_model'].load_state_dict(dict_model['model'])    
print(f"Unet model has been loaded with {config['ml']['device']}!")


from speechbrain.pretrained import SepformerSeparation as separator
from speechbrain.pretrained import SpectralMaskEnhancement as enhancer
from speechbrain.pretrained import SpeakerRecognition
models['sep_model'] = separator.from_hparams(source="speechbrain/sepformer-whamr", savedir='pretrained_models/separator', run_opts={"device":device})
models['enhance_model'] = enhancer.from_hparams(source="speechbrain/mtl-mimic-voicebank", savedir='pretrained_models/enhancer', run_opts={"device":device})
models['voice_rec_model'] = SpeakerRecognition.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb", savedir='pretrained_models/voice_recognition', run_opts={"device":device})
ref_voice_shcho = torchaudio.load(f"{config['dirs']['sound_path']}/cho.wav")[0].to(device)
ref_voice_bsjang = torchaudio.load(f"{config['dirs']['sound_path']}/jang.wav")[0].to(device)
# stt_model = WhisperForConditionalGeneration.from_pretrained(stt_model_path)
stt_processors = {}
stt_processors['processor'] = WhisperProcessor.from_pretrained(stt_model_path)
stt_processors['forced_decoder_ids'] = stt_processors['processor'].get_decoder_prompt_ids(language="korean", task="transcribe")
models['stt_model'] = WhisperForConditionalGeneration.from_pretrained("openai/whisper-medium").to(device)