from Cat import Cat

c = Cat()

while True:
    direction = input("")
    if direction == "w":
        c.gather_move_up()
    elif direction == "a":
        c.gather_move_left()
    elif direction == "s":
        c.gather_move_down()
    elif direction == "d":
        c.gather_move_right()
    else:
        print("invalid input")
