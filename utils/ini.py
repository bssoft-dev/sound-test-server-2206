import configparser, sys
import torch

config = configparser.ConfigParser()
config.read('/bssoft/config.ini')

sys.path.insert(1, config['dirs']['ml_path'])
from model.unet_wave import UNet_Wave

if config['ml']['device'] == 'gpu':
    unet_model = UNet_Wave().to('cuda')
    dict_model = torch.load(config['ml']['model'])
    unet_model.load_state_dict(dict_model['model'])    
    print('Unet model has been loaded with GPU!')
else:
    unet_model = UNet_Wave().to('cpu')
    dict_model = torch.load(config['ml']['model'], map_location='cpu')
    unet_model.load_state_dict(dict_model['model'])    
    print('Unet model has been loaded with CPU!')


from speechbrain.pretrained import SepformerSeparation as separator
from speechbrain.pretrained import SpectralMaskEnhancement as enhancer
sep_model = separator.from_hparams(source="speechbrain/sepformer-whamr", savedir='pretrained_models/separator', run_opts={"device":"cuda"})
enhance_model = enhancer.from_hparams(source="speechbrain/mtl-mimic-voicebank", savedir='pretrained_models/enhancer', run_opts={"device":"cuda"})