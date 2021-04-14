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

from Cat import Cat

app = Flask(__name__)
CORS(app)
if 'DYNO' in os.environ:
    sslify = SSLify(app)

c = Cat()
c.name = "Lily"

lock_variables = False

@app.before_first_request
def light_thread():
    def run():
        while True:
            lock_variables = True
            c.update_state()
            lock_variables = False
            time.sleep(65)
    thread = threading.Thread(target=run)
    thread.start()


@app.route("/")
def cat():
    print("hunger", c.hunger)
    print("happiness", c.happiness)
    return render_template(
        'index.html',
        title="Hello",
        pet_sprite=c.current_sprite_url,
        pet_name=c.name,
        pet_hunger=int(c.hunger),
        pet_happiness=int(c.happiness),
        pet_is_sleeping=c.is_sleeping,
        pet_level=int(c.level),
        pet_exp=int(c.exp)
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
