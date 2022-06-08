import soundfile as sf
import numpy as np
import os
import librosa
import argparse
import torch
from model.unet_wave import UNet_Wave
import time


def inference(inputs, model, fs, device):

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
        
        y_each = torch.FloatTensor(x_buffer.reshape(1, 1, -1)).to(device)
        y_each = model(y_each).squeeze(1).detach().cpu().numpy()
        
        y_out = y_each[:,y_each.shape[1]//2-hop_length:y_each.shape[1]//2] * win[:hop_length].reshape(1,-1) 
        y_out = y_out + y_buffer 
        y_buffer = y_each[:, y_each.shape[1]//2:y_each.shape[1]//2+hop_length ]* win[hop_length:].reshape(1,-1)
                
        y_out  = y_out.reshape(-1)   

        EnhndSpeech = np.concatenate((EnhndSpeech, y_out), axis=0)
        
        i = i + hop_length
        
        if i > len(inputs[0,:]) - hop_length:            
            break

    return EnhndSpeech
      
def noise_reduct(fs, model, InSample_PATH, OutSample_PATH, device):
    with torch.no_grad():  
        model.eval()          
        in_sample, fs_y = librosa.load(InSample_PATH, sr = fs)
        in_sample = in_sample.reshape(1,-1)
        start_time = time.time()
        EnhndSpeech    = inference(in_sample, model, fs, device)
        print('inferece time is {}s'.format(time.time()-start_time))
    sf.write(OutSample_PATH, EnhndSpeech, samplerate=fs, subtype='PCM_16')      

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fs',                default=16000,  type=int,    dest='fs')
    parser.add_argument('--MODEL_PATH',        default='./model/model-best.pth',  type=str,  dest='MODEL_PATH')    
    parser.add_argument('--InSample_PATH',     default = './in_samples/KsponSpeech_372061_babble2_snr3_tl-25_t60_0.09807.wav',  type=str,  dest='InSample_PATH')
    parser.add_argument('--OutSample_PATH',    default = './out_samples/out2.wav',  type=str,  dest='OutSample_PATH')

    args = parser.parse_args()
    
    noise_reduct(args)
    
    
