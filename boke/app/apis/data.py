from flask import Blueprint, jsonify, Response, url_for
from utils import sound
import numpy as np
from utils import model, preprocessor

data = Blueprint('data', __name__)

@data.route('/api/data', methods=['GET', 'OPTIONS', 'POST'])
def get_data():
    ''' send data from container'''
    y = sound.get_data()[::2]
    x = [_ for _ in range(len(y))]
    rv = jsonify(points=list(zip(x, y)))
    return rv

@data.route('/api/predict', methods=['GET', 'OPTIONS', 'POST'])
def predict():
    ''' get current sound data and predict '''
    y = sound.get_data()
    y1 = [0]
    _yy = [0, 0, 0, 0, 0, 0]
    if y:
        _y = list(y)
        y1 = model.predict(preprocessor(y)).tolist()[0]
        _yy = model.predict_proba(preprocessor(_y)).tolist()[0]

    # probas
    y2 = _yy[0]
    y3 = _yy[1]
    y4 = _yy[2]
    y5 = _yy[3]
    y6 = _yy[4]
    y7 = _yy[5]
    rv = jsonify(points=[y1, y2, y3, y4, y5, y6, y7])
    return rv
