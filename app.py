from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import db as database

app = Flask(__name__)

with app.app_context():
    database.criar_tabelas()

@app.route('/')
def hello():
    return "<h1>Hello World!</h1>"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)

