from flask import Flask, render_template, url_for, flash, redirect
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

bcrypt = Bcrypt()


app = Flask(__name__)
app.config['SECRET_KEY'] = '611d9950d57b916a8a8e4b620b1ef04c'
login_manager = LoginManager(app)

import Routes


