#importing libraries
import os
import numpy as np
import flask
import pickle
from flask import Flask, render_template, request

import re
from joblib import dump, load

import tensorflow as tf

from tensorflow.keras import layers
import tensorflow_datasets as tfds

from mlearner.nlp import Transformer
from mlearner.nlp import Processor_data


def Function_clean(text):
        # Eliminamos la @ y su mención
        text = re.sub(r"@[A-Za-z0-9]+", ' ', text)
        # Eliminamos los links de las URLs
        text = re.sub(r"https?://[A-Za-z0-9./]+", ' ', text)
        return text

# from utils.load_model import ValuePredictor
e=2

#creating instance of the class
app = Flask(__name__)

# to tell flask what url shoud trigger the function index()
@app.route('/')
@app.route('/index')
def index():
    return flask.render_template('index.html')

@app.route('/result', methods = ['POST'])
def result():
    if request.method == 'POST':
        to_predict_list = request.form.to_dict()
        to_predict_list = list(to_predict_list.values())
        try:
            to_predict_list = list(map(str, to_predict_list))
            result = ValuePredictor(to_predict_list)
            prediction=f'es: {result}'
        except ValueError:
            prediction='Error en el formato de los datos'

        sentence=f'en: {to_predict_list[0]}'
        return render_template("result.html", sentence=sentence, prediction=prediction)


if __name__ == '__main__': 

    processor_en = load('model/processor_en.joblib')
    processor_es = load('model/processor_es.joblib')

    from utils.load_model import ValuePredictor
    print(ValuePredictor)
    e = 1
    app.run(host='0.0.0.0')
#     # app.run(port=8003)



