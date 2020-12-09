import librosa
import numpy as np

SR = 44100
G={"G13":0,"G24":1,"G5":2,"G67":3,"G89":4,"G1011":5}
Gnames={value: key for key, value in G.items()}
GArray=["G13","G24","G5","G67","G89","G1011"]


def MFCCMIX(x,a,b,c):
   """Returns first a MFCC coefficients (Librosa Implementation)"""
   if a>0:
     mfccs = librosa.feature.mfcc(y=x, sr=SR, n_mfcc=a)
     if b>0:
       deltas = librosa.feature.delta(data=mfccs,width=b,order=1)
       if c>0:
         deltadeltas = librosa.feature.delta(data=mfccs,width=c,order=2)
         return np.mean(np.vstack((mfccs, deltas, deltadeltas)),axis=1)
       return np.mean(np.vstack((mfccs, deltas)),axis=1)
     return np.mean(np.vstack((mfccs)),axis=1)
   return np.array([])

def MFCC13(T): return MFCCMIX(T,13,0,0)

def load_model(model_path, *args, evalute=False, **kwargs):
    '''
    Load a model that have HDF5 standard or pickled
    *args and **kwargs should contain the inputs for model evaluation
    '''

    import os
    import pickle
    import joblib

    if not os.access(model_path, os.R_OK):
        raise PermissionError(f'Cannot open {model_path}')

    _, file_extension = os.path.splitext(model_path)

    if file_extension in ['.pck', '.pkl', '.pickle', '.model']:
        model_data = joblib.load(model_path)
        model, preprocessor = model_data['Model'], model_data['Preprocess Function']
        return  model, preprocessor

    if file_extension == '.hdf5':
        import tensorflow as tf
        model = tf.keras.models.load_model(model_path)

        if evalute:
            loss, acc = model.evaluate(*args, **kwargs)
            path, model_name = os.path.split(model_path)
            print(f'summary for {model_name}:')
            print('-' * 15)
            print(model.summary())
            print('-' * 15)
            print(f'Restored model acc: {acc * 100: 5.3f}%')

        return model


from scipy.interpolate import interp1d
ip = interp1d([-(2**15), 2**15-1], [-1, 1])
def process_data(data, preprocessor=None):
    '''
        This function takes the data coming from the sensors/mics
        and converts these to a given format (e.g. analog -> waw)
    '''
    import numpy as np
    data = ip(data)
    data = np.array(data)

    if preprocessor:
        return np.array(list(map(preprocessor, [data])))
    return data


