from datetime import datetime

class Cat:
    def __init__(self):
        self.name = "todo"
        self.hunger = 100
        self.happiness = 50
        self.is_sleeping = False

    def update_state(self):
        """
        Update state variables of Cat
        """
        # Determines if it is night time or not and returns True or False
        # Night time is determined as 10:00pm PST - 8am PST
        current_time = datetime.now()
        if current_time.hour >= 22 and current_time.hour <= 8:
            self.is_sleeping = True
        else:
            self.is_sleeping = False

        # Reduce 1 hunger every 6 minutes--
        # 10 hunger every hour
        # 80 hunger every 8 hours
        if current_time.minute % 6:
            if self.is_sleeping:
                self.hunger = self.hunger - 0.5
            else:
                self.hunger = self.hunger - 1

        if current_time.minute % 20:
            if not self.is_sleeping:
                self.happiness = self.happiness - 1

    def play(self):
        self.happiness = self.happiness + 20

    def feed(self):
        self.hunger = self.hunger + 30
