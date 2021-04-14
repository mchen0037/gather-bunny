from datetime import datetime
import time

import requests

import pyrebase
import os


config = {
  "apiKey": os.environ['GATHER_FB_API_KEY'],
  "authDomain": os.environ['GATHER_FB_AUTH_DOMAIN'],
  "databaseURL": os.environ['GATHER_FB_DATABASE_URL'],
  "storageBucket": os.environ['GATHER_FB_STORAGE_BUCKET']
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

SPRITE_URLS = {
    'NORMAL_URL' : "https://raw.githubusercontent.com/mchen0037/gather-bunny/master/static/stand/stand0_0.png",
    'HUNGRY_URL' : "https://raw.githubusercontent.com/mchen0037/gather-bunny/master/static/hunger/hungry_0.png",
    'HAPPY_URL' : "https://raw.githubusercontent.com/mchen0037/gather-bunny/master/static/love/love_2.png",
    'HAPPY_URL_HIGHLIGHT': "https://raw.githubusercontent.com/mchen0037/gather-bunny/master/static/love/love_3.png",
    'SLEEPING_URL' : "https://raw.githubusercontent.com/mchen0037/gather-bunny/master/static/sleep/sleep_3.png",
    'SAD_URL' : "https://raw.githubusercontent.com/mchen0037/gather-bunny/master/static/hunger/hungry_0.png",
}

class Cat:
    def __init__(self):
        self.update_state()

    def reset_cat(self):
        cat = {
            "name": "Lily",
            "hunger": 100,
            "happiness": 50,
            "is_sleeping": False,
            "current_sprite_url" : SPRITE_URLS['NORMAL_URL'],
            "level" : 1,
            "exp" : 0
        }

        db.child("cats").child("Lily").set(cat)

        self.update_state()


    def update_state(self):
        """
        Update state variables of Cat
        """
        # Determines if it is night time or not and returns True or False
        # Night time is determined as 10:00pm PST - 8am PST
        current_time = datetime.now()
        new_state = self.get_state()

        # self.set_sleep()

        if current_time.hour >= 22 or current_time.hour <= 8:
            # self.is_sleeping = True
            new_state['is_sleeping'] = True
        else:
            new_state['is_sleeping'] = False

        # Reduce 1 hunger every 6 minutes--
        # 10 hunger every hour
        # 80 hunger every 8 hours
        if current_time.minute % 6 == 0:
            if new_state['is_sleeping']:
                new_state['hunger'] = max(new_state['hunger'] - 0.5, 0)
            else:
                new_state['hunger'] = max(new_state['hunger'] - 1, 0)

        if current_time.minute % 20 == 0:
            if not new_state['is_sleeping']:
                new_state['happiness'] = new_state['happiness'] - 1

        new_state = self.update_sprite(new_state)

        db.child("cats").child("Lily").set(new_state)

    def update_sprite(self, new_state):
        """
        Based on changing values of state, we need to update the sprite
        """
        new_map_state = self.get_gather_map_state()

        if new_state['is_sleeping']:
            new_state['current_sprite_url'] = SPRITE_URLS['SLEEPING_URL']
            new_map_state['objects'][-1]['normal'] = SPRITE_URLS['SLEEPING_URL']
            new_map_state['objects'][-1]['highlighted'] = SPRITE_URLS['SLEEPING_URL']
        elif new_state['hunger'] < 30:
            new_state['current_sprite_url'] = SPRITE_URLS['HUNGRY_URL']
            new_map_state['objects'][-1]['normal'] = SPRITE_URLS['HUNGRY_URL']
            new_map_state['objects'][-1]['highlighted'] = SPRITE_URLS['HUNGRY_URL']
        elif new_state['happiness'] < 30:
            new_state['current_sprite_url'] = SPRITE_URLS['SAD_URL']
            new_map_state['objects'][-1]['normal'] = SPRITE_URLS['SAD_URL']
            new_map_state['objects'][-1]['highlighted'] = SPRITE_URLS['SAD_URL']
        elif new_state['happiness'] > 75:
            new_state['current_sprite_url'] = SPRITE_URLS['HAPPY_URL']
            new_map_state['objects'][-1]['normal'] = SPRITE_URLS['HAPPY_URL']
            new_map_state['objects'][-1]['highlighted'] = SPRITE_URLS['HAPPY_URL_HIGHLIGHT']
        else:
            new_state['current_sprite_url'] = SPRITE_URLS['NORMAL_URL']
            new_map_state['objects'][-1]['normal'] = SPRITE_URLS['NORMAL_URL']
            new_map_state['objects'][-1]['highlighted'] = SPRITE_URLS['HAPPY_URL_HIGHLIGHT']

        print(self.set_gather_map_state(new_map_state))
        return new_state


    def play(self):
        """
        Grab the state from the Firebase DB and then update happiness
        """

        new_state = self.get_state()
        delta = min(new_state['happiness'] + 20, 100) - new_state['happiness']
        new_state['happiness'] = new_state['happiness'] + delta
        new_state['exp'] = new_state['exp'] + (1 / new_state['level'] * delta)

        if new_state['exp'] >= 100:
            new_state['exp'] = new_state['exp'] - 100
            new_state['level'] = new_state['level'] + 1

        # Need to update the sprite if necessary
        new_state = self.update_sprite(new_state)
        db.child("cats").child("Lily").set(new_state)

    def feed(self):
        """
        Grab the state from the Firebase DB and then update hunger
        """

        new_state = self.get_state()
        delta = min(new_state['hunger'] + 20, 100) - new_state['hunger']
        new_state['hunger'] = new_state['hunger'] + delta
        new_state['exp'] = new_state['exp'] + (1 / new_state['level'] * delta)

        if new_state['exp'] >= 100:
            new_state['exp'] = new_state['exp'] - 100
            new_state['level'] = new_state['level'] + 1

        # Need to update the sprite if necessary
        new_state = self.update_sprite(new_state)
        db.child("cats").child("Lily").set(new_state)

    def gather_move_up(self):
        map_state = self.get_gather_map_state()
        map_state["objects"][-1]["y"] = map_state["objects"][-1]["y"] - 1
        # print out the status code from the API
        print(self.set_gather_map_state(map_state))
        return

    def gather_move_down(self):
        map_state = self.get_gather_map_state()
        map_state["objects"][-1]["y"] = map_state["objects"][-1]["y"] + 1
        # print out the status code from the API
        print(self.set_gather_map_state(map_state))
        return

    def gather_move_left(self):
        map_state = self.get_gather_map_state()
        map_state["objects"][-1]["x"] = map_state["objects"][-1]["x"] - 1
        # print out the status code from the API
        print(self.set_gather_map_state(map_state))
        return

    def gather_move_right(self):
        map_state = self.get_gather_map_state()
        map_state["objects"][-1]["x"] = map_state["objects"][-1]["x"] + 1
        # print out the status code from the API
        print(self.set_gather_map_state(map_state))
        return

    # def gather_change_sprite(self):
    #     map_state = self.get_gather_map_state()

    def test(self):
        """
        Lower exp, happiness, and hunger to test the cat
        """
        db.child("cats").child("Lily").child("happiness").set(29)
        db.child("cats").child("Lily").child("hunger").set(29)
        # db.child("cats").child("Lily").child("is_sleeping").set(True)

    def get_state(self):
        return db.child("cats").child("Lily").get().val()

    def get_gather_map_state(self):
        map_state = requests.get("https://gather.town/api/getMap",
            params={
                "apiKey": os.environ["GATHER_API_KEY"],
                "spaceId": "Uu7dRIJ7BdzD44NS\\party",
                "mapId": "homeroom"
            }
        )
        return map_state.json()

    def set_gather_map_state(self, new_map):
        req = requests.post("https://gather.town/api/setMap",
            json={
                "apiKey": os.environ["GATHER_API_KEY"],
                "spaceId": "Uu7dRIJ7BdzD44NS\\party",
                "mapId": "homeroom",
                "mapContent": new_map
            }
        )
        return req.status_code
