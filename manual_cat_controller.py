from Cat import Cat

c = Cat()

while True:
    direction = input("")
    if direction == "w":
        map_state = c.gather_move_up()
    elif direction == "a":
        map_state = c.gather_move_left()
    elif direction == "s":
        map_state = c.gather_move_down()
    elif direction == "d":
        map_state = c.gather_move_right()
    else:
        print("invalid input")
    print(c.set_gather_map_state(map_state))
