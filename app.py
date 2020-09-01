from flask import Flask
#importing libraries
import os
import numpy as np
import flask
import pickle
from flask import Flask, render_template, request
from joblib import dump, load
import re

# import tensorflow as tf

# from tensorflow.keras import layers
# import tensorflow_datasets as tfds

# from mlearner.nlp import Transformer
# from mlearner.nlp import Processor_data


# Constantes
MAX_LENGTH = 20
VOCAB_SIZE_EN = 8198
VOCAB_SIZE_ES = 8225

# Hiper Parámetros
D_MODEL = 128
NB_LAYERS = 4
FFN_UNITS = 512
NB_PROJ = 8
DROPOUT_RATE = 0.1

app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'Hello world!'

    
if __name__ == '__main__':
    app.run(host='0.0.0.0')