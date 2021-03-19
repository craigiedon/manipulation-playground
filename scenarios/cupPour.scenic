from model import *

table_1 = Table on Vector3D(0,0,0), with width 1.8, with length 0.8, with height 0.8, with color "0.9"
r = Robot on (top back table_1).position - Vector3D(0.4, 0, 0), with color "0.5"

cup_1 = Cup completely on table_1, with color "0.12"
cup_2 = Cup completely on table_1, with color "0.12"
cup_3 = Cup completely on table_1, with color "0.12"

table_2 = Table on Vector3D(0.2, 0.75, 0.3), with width 0.7, with length 0.65, with height 0.56, with color "0.9"
bowl = Bowl on (top back table_2).position + Vector3D(0, 0.2, 0)

camera = Camera at Vector3D(table_1.x + (-0.1, 0.1), table_1.y + (-0.1, 0.1), (1.9, 2.1)), facing Vector3D(0, 0, -1)

