from flask import Flask, render_template, url_for, flash, redirect
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


app = Flask(__name__)
app.config['SECRET_KEY'] = '611d9950d57b916a8a8e4b620b1ef04c'


from Systems import Routes


