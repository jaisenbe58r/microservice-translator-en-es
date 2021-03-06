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

processor_en = load('model/processor_en.joblib')
processor_es = load('model/processor_es.joblib')

# Carga Modelo
loaded_model = Transformer(vocab_size_enc=VOCAB_SIZE_EN,
                                vocab_size_dec=VOCAB_SIZE_ES,
                                d_model=D_MODEL,
                                nb_layers=NB_LAYERS,
                                FFN_units=FFN_UNITS,
                                nb_proj=NB_PROJ,
                                dropout_rate=DROPOUT_RATE)

ckpt = tf.train.Checkpoint(Model=loaded_model)
ckpt_manager = tf.train.CheckpointManager(ckpt, "model/", max_to_keep=2)

if ckpt_manager.latest_checkpoint:
    ckpt.restore(ckpt_manager.latest_checkpoint)
    print("The last checkpoint has been restored")

# Funciones de predicción
def ValuePredictor(to_predict_list):
    to_predict = to_predict_list[0]
    result = translate(to_predict, loaded_model)
    return result

def evaluate(inp_sentence, model):
    inp_sentence = \
        [VOCAB_SIZE_EN-2] + processor_en.tokenizer.encode(inp_sentence) + [VOCAB_SIZE_EN-1]
    enc_input = tf.expand_dims(inp_sentence, axis=0)
    
    output = tf.expand_dims([VOCAB_SIZE_ES-2], axis=0)
    
    for _ in range(MAX_LENGTH):
        predictions = model(enc_input, output, False) #(1, seq_length, VOCAB_SIZE_ES)
        
        prediction = predictions[:, -1:, :]
        
        predicted_id = tf.cast(tf.argmax(prediction, axis=-1), tf.int32)
        
        if predicted_id == VOCAB_SIZE_ES-1:
            return tf.squeeze(output, axis=0)
        
        output = tf.concat([output, predicted_id], axis=-1)
        
    return tf.squeeze(output, axis=0)


def translate(sentence, model):
    output = evaluate(sentence, model).numpy()
    
    predicted_sentence = processor_es.tokenizer.decode(
        [i for i in output if i < VOCAB_SIZE_ES-2]
    )
    return predicted_sentence