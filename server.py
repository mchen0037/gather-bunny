from flask import Flask
from flask import request
from flask import jsonify
from flask import render_template
from flask_sslify import SSLify
from flask_cors import CORS

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

    return render_template(
        'index.html',
        title="Hello",
        pet_sprite="https://www.spriters-resource.com/resources/sheet_icons/20/21897.png",
        pet_name=c.name,
        pet_hunger=int(c.hunger),
        pet_happiness=int(c.happiness),
        pet_is_sleeping=c.is_sleeping

    )
