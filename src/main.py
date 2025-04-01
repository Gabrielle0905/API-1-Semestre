from flask import Flask,render_template,url_for
import os
import time

app = Flask(__name__)
app.secret_key = '4657'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from views import *

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

if __name__ == '__main__' :
    app.run(debug=True)
