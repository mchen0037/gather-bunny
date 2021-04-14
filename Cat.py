from datetime import datetime
import time

SPRITE_URLS = {
    'HAPPY_URL' :
    'HUNGRY_URL' : "https://raw.githubusercontent.com/mchen0037/gather-bunny/master/static/hunger/hungry_0.png",
}

class Cat:
    def __init__(self):
        self.name = "todo"
        self.hunger = 100
        self.happiness = 50
        self.is_sleeping = False
        self.current_sprite_url = SPRITE_URLS['HAPPY_URL']

        self.level = 1
        self.exp = 0
        self.update_state()

    def update_state(self):
        """
        Update state variables of Cat
        """
        # Determines if it is night time or not and returns True or False
        # Night time is determined as 10:00pm PST - 8am PST
        current_time = datetime.now()
        if current_time.hour >= 22 or current_time.hour <= 8:
            self.is_sleeping = True
        else:
            self.is_sleeping = False

        # Reduce 1 hunger every 6 minutes--
        # 10 hunger every hour
        # 80 hunger every 8 hours
        if current_time.minute % 6:
            if self.is_sleeping:
                self.hunger = max(self.hunger - 0.5, 0)
            else:
                self.hunger = max(self.hunger - 1, 0)

        if current_time.minute % 20:
            if not self.is_sleeping:
                self.happiness = self.happiness - 1

        # Update Sprites
        if self.hunger < 30:
            self.current_sprite_url = SPRITE_URLS['HUNGRY_URL']

    def play(self):
        delta = min(self.happiness + 20, 100) - self.happiness
        self.happiness = self.happiness + delta
        self.exp = self.exp + (1 / self.level * delta)

    def feed(self):
        delta = min(self.hunger + 20, 100) - self.hunger
        self.hunger = self.hunger + delta
        self.exp = self.exp + (1 / self.level * delta)
