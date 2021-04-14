from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask_sslify import SSLify
from flask_cors import CORS
from flask import redirect

import os

import time
import threading
import jsonify

import pyrebase

from Cat import Cat

app = Flask(__name__)
CORS(app)
if 'DYNO' in os.environ:
    sslify = SSLify(app)

c = Cat()

config = {
  "apiKey": os.environ['GATHER_FB_API_KEY'],
  "authDomain": os.environ['GATHER_FB_AUTH_DOMAIN'],
  "databaseURL": os.environ['GATHER_FB_DATABASE_URL'],
  "storageBucket": os.environ['GATHER_FB_STORAGE_BUCKET']
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()


@app.before_first_request
def light_thread():
    def run():
        while True:
            c.update_state()
            time.sleep(60)
    thread = threading.Thread(target=run)
    thread.start()


@app.route("/")
def cat():
    state = c.get_state()
    return render_template(
        'index.html',
        title="Hello",
        pet_sprite=state['current_sprite_url'],
        pet_name=state['name'],
        pet_hunger=int(state['hunger']),
        pet_happiness=int(state['happiness']),
        pet_is_sleeping=state['is_sleeping'],
        pet_level=int(state['level']),
        pet_exp=int(state['exp'])
    )

@app.route("/feed")
def feed():
    lock_variables = True
    c.feed()
    lock_variables = False
    time.sleep(1)
    return redirect(f"/")

@app.route("/play")
def play():
    lock_variables = True
    c.play()
    lock_variables = False
    time.sleep(1)
    return redirect(f"/")

@app.route("/test")
def test():
    c.hunger = 20
    c.happiness = 30
    c.exp = 0
    c.update_state()
    return redirect(f"/")
