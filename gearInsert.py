from pyrep import PyRep
from pyrep.robots.arms.panda import Panda
from pyrep.robots.end_effectors.panda_gripper import PandaGripper
from pyrep.objects import Camera, VisionSensor
import numpy as np
from wrappers.setupFuncs import setAonB, create_table
from wrappers import robotControl as rc

### SETUP CODE ###
pr = PyRep()
pr.launch("scenes/emptyVortex.ttt", headless=False, responsive_ui=True)

scene_view = Camera('DefaultCamera')
scene_view.set_position([3.45, 0.18, 2.0])
scene_view.set_orientation(np.array([180, -70, 90]) * np.pi / 180.0)

pr.step_ui()

depth_cam = VisionSensor.create([256, 256], position=[0, 0, 2.0], orientation=np.array([0.0, 180.0, -90.0]) * np.pi / 180.0 )

# Import Robots
pr.import_model("models/Panda.ttm")
panda_1 = Panda(0)
gripper_1 = PandaGripper(0)

# Prop Creation
table = create_table(pr, 0.75, 0.75, 0.8)
gear = pr.import_model("models/HexagonalGear.ttm")
g_base = pr.import_model("models/HexagonalPegBase.ttm")

setAonB(panda_1, table, -0.3)

setAonB(gear, table, 0.0, 0.2)
setAonB(g_base, table, 0.0, -0.2)

###################

pr.start()

### Robot Movement Code Goes Here ###

rc.move_above_object(pr, panda_1, gear, z_offset=-0.1, ig_cols=True)
# rc.move_to_pos(pr, panda_1, top_of(table) + np.array([-0.4, 0.2, 0.0]), ig_cols=True)

for i in range(2000):
    pr.step()
    if i % 100 == 0:
        print(i)

######################################

pr.stop()
pr.shutdown()