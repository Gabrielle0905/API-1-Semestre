from flask import Flask,render_template,url_for
import os
import time
import json

app = Flask(__name__)
app.secret_key = '4657'
dir_base = os.path.dirname(os.path.abspath(__file__))

# App.Config para Upload de Atestados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config['uploads_atestados'] = os.path.join(BASE_DIR, 'uploads_atestados')


from views import *
UPLOAD_FOLDER = os.path.join(dir_base, 'uploads_atestados')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

USER_FOLDER = os.path.join(dir_base, 'usuarios')
app.config['USER_FOLDER'] = USER_FOLDER
os.makedirs(app.config['USER_FOLDER'], exist_ok=True)

caminho_atestados = os.path.join(UPLOAD_FOLDER, 'dados_atestados.json')
if not os.path.exists(caminho_atestados):
    with open(caminho_atestados, 'w') as u:
        json.dump({}, u)

caminho_usuarios = os.path.join(USER_FOLDER, 'usuarios.json')
if not os.path.exists(caminho_usuarios):
    with open(caminho_usuarios, 'w') as u:
        json.dump({}, u)

caminho_equipes = os.path.join(USER_FOLDER, 'equipes.json')
if not os.path.exists(caminho_equipes):
    with open(caminho_equipes, 'w') as u:
        json.dump({}, u)

if __name__ == '__main__' :
    app.run(debug=True)
