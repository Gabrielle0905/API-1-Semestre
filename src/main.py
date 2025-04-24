from flask import Flask,render_template,url_for
import os
import time
import json

app = Flask(__name__)
app.secret_key = '4657'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from views import *

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
dir_base = os.path.dirname(os.path.abspath(__file__))
caminho_usuarios = os.path.join(dir_base, 'usuarios.json')

if not os.path.exists(caminho_usuarios):
    with open(caminho_usuarios, 'w') as u:
        json.dump({}, u)

if __name__ == '__main__' :
    app.run(debug=True)
