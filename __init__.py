from app import app
import re

def Function_clean(text):
        # Eliminamos la @ y su mención
        text = re.sub(r"@[A-Za-z0-9]+", ' ', text)
        # Eliminamos los links de las URLs
        text = re.sub(r"https?://[A-Za-z0-9./]+", ' ', text)
        return text

from utils.load_model import ValuePredictor

app.run(host='0.0.0.0')
# app.run(port=8003)

