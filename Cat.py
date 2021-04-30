import datetime as dt
import time

import requests

import pyrebase
import os

import random

from GatherTownBase64HexArray import GatherTownBase64HexArray
PST = dt.timezone(dt.timedelta(hours=-8))

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
        current_time = dt.datetime.now(PST)
        new_state = self.get_state()

        if current_time.hour >= 22 or current_time.hour <= 8:
            # self.is_sleeping = True
            new_state['is_sleeping'] = True
            if current_time.minute == 1:
                self.update_cafe_board()
        else:
            new_state['is_sleeping'] = False

        if current_time.minute % 8 == 0:
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
        new_map_state = self.get_gather_map_state(new_state['current_map'])

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

        print("update_sprite", self.set_gather_map_state(new_map_state, new_state['current_map']))
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


    def move_random_walk(self):
        """
        Calculate collisions based on our current position, make a random step.
        After calculating the step that we will take, determine if we are on
        any portals. If we are on a portal, we will teleport to that new map.
        """
        dir = random.randint(0,3)
        lily_state = self.get_state()
        lily_current_map = lily_state['current_map']
        map_state = self.get_gather_map_state(lily_current_map)

        # Grab current xycor of cat so we can check for collisions.
        current_xcor = map_state["objects"][-1]["x"]
        current_ycor = map_state["objects"][-1]["y"]

        # [up, down, left, right]
        collision_neighbors = self.check_possible_directions(
            map_state, current_xcor, current_ycor
        )

        possible_direction_procedures = []
        if not collision_neighbors[0]: possible_direction_procedures.append(
            self.gather_move_up
        )
        if not collision_neighbors[1]: possible_direction_procedures.append(
            self.gather_move_down
        )
        if not collision_neighbors[2]: possible_direction_procedures.append(
            self.gather_move_left
        )
        if not collision_neighbors[3]: possible_direction_procedures.append(
            self.gather_move_right
        )

        if len(possible_direction_procedures) > 0:
            map_state = random.choice(possible_direction_procedures)(lily_current_map)

        new_current_xcor = map_state["objects"][-1]["x"]
        new_current_ycor = map_state["objects"][-1]["y"]

        # Before sending the request to setMap, we should calculate if
        # Lily is standing on any portals.

        portals = map_state['portals']
        portal_standing_on = self.check_for_portals(
            portals, new_current_xcor, new_current_ycor
        )

        if portal_standing_on is not None:
            # 1. Grab the Target Coordinates
            target_map_name = portal_standing_on['targetMap']
            target_x = portal_standing_on['targetX']
            target_y = portal_standing_on['targetY']

            # 2. Delete Lily from current map (oh god)
            lily = map_state["objects"].pop()
            lily['x'] = target_x
            lily['y'] = target_y

            # 3. Redirect the map that Lily needs to go.
            target_map_state = self.get_gather_map_state(target_map_name)
            target_map_state['objects'].append(lily)
            db.child("cats").child("Lily").child("current_map").set(target_map_name)

            # 4. Update database map that lily is in.
            self.set_gather_map_state(target_map_state, target_map_name)

        print("move_random_walk", self.set_gather_map_state(map_state, lily_current_map))
        return

    def check_possible_directions(self, map_state, current_xcor, current_ycor):
    # def check_possible_directions(self, map_state):
        """
        Checks for collisions based on current x, y cooridnate
        Returns list of [0, 0, 0, 0] where 1 is a collision and 0 is not.
        """
        collision_array = GatherTownBase64HexArray(
            map_state['collisions'],
            map_state['dimensions']
        )

        return collision_array.get_collision_neighbors(current_xcor, current_ycor)

    def check_for_portals(self, portals, new_current_xcor, new_current_ycor):
        for portal in portals:
            if ( portal['x'] == new_current_xcor and
                portal['y'] == new_current_ycor
                ):
                return portal
        return None


    def gather_move_up(self, map_name):
        print("move_up")
        map_state = self.get_gather_map_state(map_name)
        map_state["objects"][-1]["y"] = map_state["objects"][-1]["y"] - 1
        return map_state

    def gather_move_down(self, map_name):
        print("move_down")
        map_state = self.get_gather_map_state(map_name)
        map_state["objects"][-1]["y"] = map_state["objects"][-1]["y"] + 1
        return map_state

    def gather_move_left(self, map_name):
        print("move_left")
        map_state = self.get_gather_map_state(map_name)
        map_state["objects"][-1]["x"] = map_state["objects"][-1]["x"] - 1
        return map_state

    def gather_move_right(self, map_name):
        print("move_right")
        map_state = self.get_gather_map_state(map_name)
        map_state["objects"][-1]["x"] = map_state["objects"][-1]["x"] + 1
        return map_state

    def update_cafe_board(self):
        """
        Update the cafe board with a new random qod
        """
        board_id = '1wM0xV12VmiM3ObLIFJ4-_1402fde1-22ff-46a9-b4c3-7c91abdea15d'
        map_name = "coffee"
        map_state = self.get_gather_map_state(map_name)
        cafe_board_index = self.get_gather_object_index_by_id(map_state, board_id)
        cafe_board = map_state['objects'][cafe_board_index]

        # Call API to get quote of the day
        data = requests.get(
            "https://quotes.rest/qod?language=en"
        )

        res = data.json()
        if res is None:
            quote = "You look beautiful today"
            auth = "Mighty Chen"
        else:
            quote = res['contents']['quotes'][0]['quote'] or "You look beautiful today"
            auth = res['contents']['quotes'][0]['author'] or "Mighty Chen"

        content = quote + " --" + auth

        cafe_board['properties']['message'] = content
        map_state['objects'][cafe_board_index] = cafe_board

        print("update_cafe_board", self.set_gather_map_state(map_state, map_name))


    def get_gather_object_index_by_id(self, map_state, obj_id):
        """
        Go through all of the objects and find the index of a specific obj_id
        """
        for i in range(len(map_state['objects'])):
            obj = map_state['objects'][i]
            if "id" in obj.keys():
                if obj['id'] == obj_id:
                    return i
        return None

    def unlock_bookshelf(self):
        """
        Removes the collision object where the bookshelf is.
        """
        map_name = "library"
        map_state = self.get_gather_map_state(map_name)
        door_x = 11
        door_y = 37

        collision_array = GatherTownBase64HexArray(
            map_state['collisions'],
            map_state['dimensions']
        )

        collision_array.set_value_at_location(door_x, door_y, 0)
        map_state['collisions'] = collision_array.hex_array_base64
        print("unlocking bookshelf", self.set_gather_map_state(map_state, map_name))

    def lock_bookshelf(self):
        """
        Replaces the collision object where the bookshelf is.
        """
        map_name = "library"
        map_state = self.get_gather_map_state(map_name)
        door_x = 11
        door_y = 37

        collision_array = GatherTownBase64HexArray(
            map_state['collisions'],
            map_state['dimensions']
        )

        collision_array.set_value_at_location(door_x, door_y, 1)
        map_state['collisions'] = collision_array.hex_array_base64
        print("locking bookshelf", self.set_gather_map_state(map_state, map_name))


    def test(self):
        """
        Lower exp, happiness, and hunger to test the cat
        """
        db.child("cats").child("Lily").child("happiness").set(29)
        db.child("cats").child("Lily").child("hunger").set(29)

    def get_state(self):
        return db.child("cats").child("Lily").get().val()

    def get_gather_map_state(self, map_id):
        map_state = requests.get("https://gather.town/api/getMap",
            params={
                "apiKey": os.environ["GATHER_API_KEY"],
                "spaceId": "Uu7dRIJ7BdzD44NS\\party",
                "mapId": map_id
            }
        )
        return map_state.json()

    def set_gather_map_state(self, new_map, map_id):
        req = requests.post("https://gather.town/api/setMap",
            json={
                "apiKey": os.environ["GATHER_API_KEY"],
                "spaceId": "Uu7dRIJ7BdzD44NS\\party",
                "mapId": map_id,
                "mapContent": new_map
            }
        )
        return req.status_code
