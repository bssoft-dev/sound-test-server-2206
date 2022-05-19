import argparse
import torch
from model.unet_wave import UNet_Wave
import torch.onnx
#%%
DEVICE = 'cpu'
#%%
def main(args):   
    model      = UNet_Wave().to(DEVICE)
    dict_model = torch.load(args.MODEL_PATH, map_location=DEVICE)
    model.load_state_dict(dict_model['model'])    
    print('DNN model has been loaded!')
    model.eval()       
    dummy_data = torch.empty(1,1,16384, dtype=torch.float32).to(DEVICE)
    torch.onnx.export(
                        model, 
                        dummy_data, 
                        args.onnx_MODEL_PATH,
                        export_params=True, 
                        opset_version=11, 
                        do_constant_folding=True,
                        keep_initializers_as_inputs=None,
                        enable_onnx_checker=True,
                        use_external_data_format=False,
                        input_names = ['input'], 
                        output_names = ['output'], 
                        dynamic_axes={'input'  : {0 : 'batch_size'}, 
                                      'output' : {0 : 'batch_size'}}
                    )
#%%    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--MODEL_PATH',        default='./model/model-best.pth',  type=str,  dest='MODEL_PATH')    
    parser.add_argument('--onnx_MODEL_PATH',        default='./model/model-best.onnx',  type=str,  dest='onnx_MODEL_PATH')   
    args = parser.parse_args()
    
    main(args)
    
    