import base64

# by Fragrag#5448 on the discord channel
class GatherTownBase64HexArray:
    """
    Class that represents a Base64 Hexadecimal array
    These arrays are used in the GatherTownMap data to represent positions of collisions, walls, floors etc...
    """

    def __init__(self, _hex_array_base64: str, map_dimensions):
        self.hex_array_base64 = _hex_array_base64
        self.map_dimensions = map_dimensions

    def get_byte_array(self):
        hex_array_base64_bytes = self.hex_array_base64.encode('ascii')
        hex_array_bytes = base64.b64decode(hex_array_base64_bytes)

        return bytearray(hex_array_bytes)

    def get_collision_neighbors(self, my_x, my_y):
        # i.e. (10, 2)
        # 10 + 2 * 20
        my_position = my_x + (my_y * self.map_dimensions[0])
        byte_array = self.get_byte_array()

        # up, down, left, right
        collision_neighbors = [False, False, False, False]

        up_position = my_position - self.map_dimensions[0]
        down_position = my_position + self.map_dimensions[0]
        left_position = my_position - 1
        right_position = my_position + 1

        # set collision to 1 if it's a collision or if we're at the edge of map
        if byte_array[up_position] == 1 or up_position < self.map_dimensions[0]:
            collision_neighbors[0] = True
        if (byte_array[down_position] == 1 or
            down_position > len(byte_array) - self.map_dimensions[0]
        ):
            collision_neighbors[1] = True
        if (byte_array[left_position] == 1 or
            left_position % self.map_dimensions[0] == 0
        ):
            collision_neighbors[2] = True
        if (byte_array[right_position] == 1 or
            right_position % (self.map_dimensions[0] - 1) == 0
        ):
            collision_neighbors[3] = True

        return collision_neighbors
