
# -*- coding: utf-8 -*-
import soundfile as sf
import numpy as np
import os
import librosa
import argparse
import torch
from model.unet_wave import UNet_Wave
import time

#%%
""" os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="0"
USE_CUDA = torch.cuda.is_available() """
DEVICE = 'cpu'
# DEVICE = 'cuda'

#%%
"""
import warnings
warnings.filterwarnings('ignore')

import keras
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
  try:
    tf.config.experimental.set_memory_growth(gpus[0], True)
  except RuntimeError as e:
    # 프로그램 시작시에 메모리 증가가 설정되어야만 합니다
    print(e)
"""

def inference(inputs, model, fs):

    sample_length = 16384
    hop_length = sample_length//2
    
    x_buffer= np.zeros([1,sample_length], dtype=np.float32)   
    y_buffer= np.zeros([1,hop_length], dtype=np.float32)   
    win = np.hamming(hop_length*2)
    EnhndSpeech = []
    i = 0
    while 1:
        x_in = inputs[:,i:i+hop_length]
        x_buffer[:,0:sample_length-hop_length] =x_buffer[:,-sample_length+hop_length:]
        x_buffer[:,-hop_length:] =x_in
        
#--------------------------------------------------------------------------------------
        y_each = torch.FloatTensor(x_buffer.reshape(1, 1, -1)).to(DEVICE)
        y_each = model(y_each).squeeze(1).detach().cpu().numpy()
        
        y_out = y_each[:,y_each.shape[1]//2-hop_length:y_each.shape[1]//2] * win[:hop_length].reshape(1,-1) 
        y_out = y_out + y_buffer 
        y_buffer = y_each[:, y_each.shape[1]//2:y_each.shape[1]//2+hop_length ]* win[hop_length:].reshape(1,-1)
                
        y_out  = y_out.reshape(-1)   
#--------------------------------------------------------------------------------------

        EnhndSpeech = np.concatenate((EnhndSpeech, y_out), axis=0)
        
        i = i + hop_length
        
        if i > len(inputs[0,:]) - hop_length:            
            break

    return EnhndSpeech
# #%%
# def voice_enhance(args): 
#     model      = UNet_Wave().to(DEVICE)
#     # dict_model = torch.load(args.MODEL_PATH)
#     dict_model = torch.load(args.MODEL_PATH, map_location='cpu')
#     model.load_state_dict(dict_model['model'])    
#     print('DNN model has been loaded!')
# #%%  
#     with torch.no_grad():  
#         model.eval()          
#         in_sample, fs_y = librosa.load(args.InSample_PATH, sr = args.fs)
#         in_sample = in_sample.reshape(1,-1)
#         start_time = time.time()
#         EnhndSpeech    = inference(in_sample, model, args.fs)
#         print('inferece time is {}s'.format(time.time()-start_time))
#     sf.write(args.OutSample_PATH, EnhndSpeech, samplerate=args.fs, subtype='PCM_16')      
# #%%
      
def voice_enhance(fs, MODEL_PATH, InSample_PATH, OutSample_PATH):   
    model      = UNet_Wave().to(DEVICE)
    # dict_model = torch.load(MODEL_PATH)
    dict_model = torch.load(MODEL_PATH, map_location='cpu')
    model.load_state_dict(dict_model['model'])    
    print('DNN model has been loaded!')
#%%  
    with torch.no_grad():  
        model.eval()          
        in_sample, fs_y = librosa.load(InSample_PATH, sr = fs)
        in_sample = in_sample.reshape(1,-1)
        start_time = time.time()
        EnhndSpeech    = inference(in_sample, model, fs)
        print('inferece time is {}s'.format(time.time()-start_time))
    sf.write(OutSample_PATH, EnhndSpeech, samplerate=fs, subtype='PCM_16')      
#%%
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fs',                default=16000,  type=int,    dest='fs')
    parser.add_argument('--MODEL_PATH',        default='./model/model-best.pth',  type=str,  dest='MODEL_PATH')    
    parser.add_argument('--InSample_PATH',     default = './in_samples/KsponSpeech_372061_babble2_snr3_tl-25_t60_0.09807.wav',  type=str,  dest='InSample_PATH')
    parser.add_argument('--OutSample_PATH',    default = './out_samples/out2.wav',  type=str,  dest='OutSample_PATH')

    args = parser.parse_args()
    
    voice_enhance(args)
    
    
