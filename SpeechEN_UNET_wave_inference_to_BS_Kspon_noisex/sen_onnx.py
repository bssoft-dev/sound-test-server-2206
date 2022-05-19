import numpy as np
import onnxruntime as ort
#%%
class WaveUnetEnhancer(object):
    def __init__(self, modelfile, cfg=None):

        """load onnx model"""
        self.ort = ort.InferenceSession(modelfile)
        self.dtype = np.float32
#%%
    def enhance(self, x):
        """Obtain the estimated filter"""
        onnx_inputs = {self.ort.get_inputs()[0].name: x.astype(self.dtype)}
        out = self.ort.run(None, onnx_inputs)[0][0]
        return out
#%%
    def __call__(self, sigIn):

        sigOut = self.enhance(sigIn)

        return sigOut
