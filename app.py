#importing libraries
import flask
from flask import Flask, render_template, request

from utils.load_model import ValuePredictor

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

    app.run(host='0.0.0.0')


