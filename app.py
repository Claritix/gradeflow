import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, world"