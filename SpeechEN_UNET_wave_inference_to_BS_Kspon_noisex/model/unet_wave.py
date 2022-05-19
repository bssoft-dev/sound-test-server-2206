import torch
import torch.nn as nn
import torch.nn.functional as F
from torchsummary import summary

#%%
class DownSamplingLayer(nn.Module):
    def __init__(self, channel_in, channel_out, dilation=1, kernel_size=15, stride=1, padding=7):
        super(DownSamplingLayer, self).__init__()
        self.main = nn.Sequential(
            nn.Conv1d(channel_in, channel_out, kernel_size=kernel_size,
                      stride=stride, padding=padding, dilation=dilation),
            nn.BatchNorm1d(channel_out),
            nn.LeakyReLU(negative_slope=0.1)
        )

    def forward(self, ipt):
        return self.main(ipt)
#%%
class UpSamplingLayer(nn.Module):
    def __init__(self, channel_in, channel_out, kernel_size=5, stride=1, padding=2):
        super(UpSamplingLayer, self).__init__()
        self.main = nn.Sequential(
            nn.Conv1d(channel_in, channel_out, kernel_size=kernel_size,
                      stride=stride, padding=padding),
            nn.BatchNorm1d(channel_out),
            nn.LeakyReLU(negative_slope=0.1, inplace=True),
        )

    def forward(self, ipt):
        return self.main(ipt)
    
#%%
class MiddleLayer(nn.Module):
    def __init__(self,channel_in, channel_out, kernel_size=15, stride=1, padding=7):
        super(MiddleLayer, self).__init__()
        self.main = nn.Sequential(
            nn.Conv1d(channel_in, channel_out, kernel_size=kernel_size, stride=stride, padding=padding),
            nn.BatchNorm1d(channel_out),
            nn.LeakyReLU(negative_slope=0.1, inplace=True)
    )
    def forward(self, ipt):
        return self.main(ipt)
    
#%%
class UNet_Wave(nn.Module):
    def __init__(self, n_layers=12, channels_interval=24):
        super(UNet_Wave, self).__init__()

        self.n_layers = n_layers
        self.channels_interval = channels_interval
        encoder_in_channels_list = [1] + [i * self.channels_interval for i in range(1, self.n_layers)]
        encoder_out_channels_list = [i * self.channels_interval for i in range(1, self.n_layers + 1)]

        #          1    => 2    => 3    => 4    => 5    => 6   => 7   => 8   => 9  => 10 => 11 =>12
        # 16384 => 8192 => 4096 => 2048 => 1024 => 512 => 256 => 128 => 64 => 32 => 16 =>  8 => 4

        self.DownSamplingLayer_0  = DownSamplingLayer(channel_in=encoder_in_channels_list[0],  channel_out=encoder_out_channels_list[0])
        self.DownSamplingLayer_1  = DownSamplingLayer(channel_in=encoder_in_channels_list[1],  channel_out=encoder_out_channels_list[1])
        self.DownSamplingLayer_2  = DownSamplingLayer(channel_in=encoder_in_channels_list[2],  channel_out=encoder_out_channels_list[2])
        self.DownSamplingLayer_3  = DownSamplingLayer(channel_in=encoder_in_channels_list[3],  channel_out=encoder_out_channels_list[3])
        self.DownSamplingLayer_4  = DownSamplingLayer(channel_in=encoder_in_channels_list[4],  channel_out=encoder_out_channels_list[4]) 
        self.DownSamplingLayer_5  = DownSamplingLayer(channel_in=encoder_in_channels_list[5],  channel_out=encoder_out_channels_list[5]) 
        self.DownSamplingLayer_6  = DownSamplingLayer(channel_in=encoder_in_channels_list[6],  channel_out=encoder_out_channels_list[6])
        self.DownSamplingLayer_7  = DownSamplingLayer(channel_in=encoder_in_channels_list[7],  channel_out=encoder_out_channels_list[7])
        self.DownSamplingLayer_8  = DownSamplingLayer(channel_in=encoder_in_channels_list[8],  channel_out=encoder_out_channels_list[8])
        self.DownSamplingLayer_9  = DownSamplingLayer(channel_in=encoder_in_channels_list[9],  channel_out=encoder_out_channels_list[9])
        self.DownSamplingLayer_10 = DownSamplingLayer(channel_in=encoder_in_channels_list[10], channel_out=encoder_out_channels_list[10])  
        self.DownSamplingLayer_11 = DownSamplingLayer(channel_in=encoder_in_channels_list[11], channel_out=encoder_out_channels_list[11])  
        
        
        self.middle=MiddleLayer(channel_in=self.n_layers * self.channels_interval, channel_out=self.n_layers * self.channels_interval)

        decoder_in_channels_list = [(2 * i + 1) * self.channels_interval for i in range(1, self.n_layers)] + [
            2 * self.n_layers * self.channels_interval]
        decoder_in_channels_list = decoder_in_channels_list[::-1]
        decoder_out_channels_list = encoder_out_channels_list[::-1]


        self.UpSamplingLayer_0  = UpSamplingLayer(channel_in=decoder_in_channels_list[0],  channel_out=decoder_out_channels_list[0])
        self.UpSamplingLayer_1  = UpSamplingLayer(channel_in=decoder_in_channels_list[1],  channel_out=decoder_out_channels_list[1])
        self.UpSamplingLayer_2  = UpSamplingLayer(channel_in=decoder_in_channels_list[2],  channel_out=decoder_out_channels_list[2])
        self.UpSamplingLayer_3  = UpSamplingLayer(channel_in=decoder_in_channels_list[3],  channel_out=decoder_out_channels_list[3])
        self.UpSamplingLayer_4  = UpSamplingLayer(channel_in=decoder_in_channels_list[4],  channel_out=decoder_out_channels_list[4])
        self.UpSamplingLayer_5  = UpSamplingLayer(channel_in=decoder_in_channels_list[5],  channel_out=decoder_out_channels_list[5])
        self.UpSamplingLayer_6  = UpSamplingLayer(channel_in=decoder_in_channels_list[6],  channel_out=decoder_out_channels_list[6])
        self.UpSamplingLayer_7  = UpSamplingLayer(channel_in=decoder_in_channels_list[7],  channel_out=decoder_out_channels_list[7])
        self.UpSamplingLayer_8  = UpSamplingLayer(channel_in=decoder_in_channels_list[8],  channel_out=decoder_out_channels_list[8])
        self.UpSamplingLayer_9  = UpSamplingLayer(channel_in=decoder_in_channels_list[9],  channel_out=decoder_out_channels_list[9])
        self.UpSamplingLayer_10 = UpSamplingLayer(channel_in=decoder_in_channels_list[10], channel_out=decoder_out_channels_list[10])
        self.UpSamplingLayer_11 = UpSamplingLayer(channel_in=decoder_in_channels_list[11], channel_out=decoder_out_channels_list[11])


        self.out = nn.Sequential(
            nn.Conv1d(1 + self.channels_interval, 1, kernel_size=1, stride=1),
            nn.Tanh()
        )
#%%
    def forward(self, input):
        tmp = []
        o = input
        
        o = self.DownSamplingLayer_0(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_1(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_2(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_3(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_4(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_5(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_6(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_7(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_8(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_9(o) ;           tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_10(o) ;          tmp.append(o)
        o = o[:, :, ::2]
        o = self.DownSamplingLayer_11(o) ;          tmp.append(o)
        o = o[:, :, ::2]

        o = self.middle(o)

        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 0 - 1]], dim=1)
        o = self.UpSamplingLayer_0(o) ;           

        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 1 - 1]], dim=1)
        o = self.UpSamplingLayer_1(o) ;   
        
        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 2 - 1]], dim=1)
        o = self.UpSamplingLayer_2(o) ;   

        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 3 - 1]], dim=1)
        o = self.UpSamplingLayer_3(o) ;           

        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 4 - 1]], dim=1)
        o = self.UpSamplingLayer_4(o) ;   
        
        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 5 - 1]], dim=1)
        o = self.UpSamplingLayer_5(o) ;   

        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 6 - 1]], dim=1)
        o = self.UpSamplingLayer_6(o) ;           

        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 7 - 1]], dim=1)
        o = self.UpSamplingLayer_7(o) ;   
        
        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 8 - 1]], dim=1)
        o = self.UpSamplingLayer_8(o) ;   

        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 9 - 1]], dim=1)
        o = self.UpSamplingLayer_9(o) ;           

        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 10 - 1]], dim=1)
        o = self.UpSamplingLayer_10(o) ;   
        
        o = F.interpolate(o, scale_factor=2, mode="linear", align_corners=True)
        o = torch.cat([o, tmp[self.n_layers - 11 - 1]], dim=1)
        o = self.UpSamplingLayer_11(o) ;   


        o = torch.cat([o, input], dim=1)
        o = self.out(o)

        return o
    #%%
if __name__ == '__main__':
    USE_CUDA = torch.cuda.is_available()
    DEVICE = torch.device('cuda:0' if USE_CUDA else 'cpu')
    batch_size  = 4
    img_size    = 16384
    in_channel  = 1
    out_channel = 1
    num_filters = 16
    
    sample_input = torch.ones(size=(batch_size, in_channel, img_size)).to(DEVICE)
    #%%
    model  = UNet_Wave().to(DEVICE)
    output = model(sample_input)
    summary(model,(in_channel, img_size) )   
    
    # check parameter of model
    print("------------------------------------------------------------")
    total_params = sum(p.numel() for p in model.parameters())
    print("num of parameter : ", total_params)
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print("num of trainable_ parameter :", trainable_params)
    print("------------------------------------------------------------")

