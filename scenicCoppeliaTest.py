import scenic3d
from scenic3d.core.object_types import Point3D
from scenic3d.core.vectors import Vector3D
from scenic3d.syntax.veneer import With
from pyrep import PyRep
from pyrep.robots.arms.panda import Panda
from pyrep.robots.end_effectors.panda_gripper import PandaGripper
from pyrep.backend.utils import script_call
from pyrep.const import PrimitiveShape
from pyrep.objects import Camera, Shape, VisionSensor
from pyrep.backend import sim
from multiprocessing import Process
import numpy as np
import matplotlib.pyplot as plt
from setupFuncs import setAonB, create_table, top_of
import robotControl as rc

from scenicCoppeliaSimWrapper import cop_from_scenic

pr = PyRep()

scenario = scenic3d.scenarioFromFile("scenarios/tableCube.scenic")

max_sims = 1
sim_result = []
inputs = []
for i in range(max_sims):
    pr.launch("scenes/emptyVortex.ttt", headless=False, responsive_ui=True)

    scene_view = Camera('DefaultCamera')
    scene_view.set_position([3.45, 0.18, 2.0])
    scene_view.set_orientation(np.array([180, -70, 90]) * np.pi / 180.0)

    ex_world, used_its = scenario.generate()
    inputs.append(ex_world)
    # ex_world.show_3d()

    # Import Robots
    c_objs = cop_from_scenic(pr, ex_world)

    panda_1, gripper_1 = Panda(0), PandaGripper(0)
    panda_2, gripper_2 = Panda(1), PandaGripper(1)

    pr.start()
    pr.step()

    ## Neatness setup
    d_cam = c_objs["Camera"][0]
    cube = c_objs["CUBOID"][0]
    tr1, tr2 = c_objs["Tray"]
    d_cam.set_entity_to_render(cube.get_handle())
    pr.step()

    d_im = np.array(d_cam.capture_depth())

    ## Robot movement code

    try:
        cube_pos_from_im = rc.location_from_depth_cam(pr, d_cam, cube)

        rc.move_to_pos(pr, panda_1, cube_pos_from_im, z_offset=-0.021)
        rc.grasp(pr, gripper_1, True)
        rc.move_to_pos(pr, panda_1, cube_pos_from_im, z_offset=0.1)

        lift_pos = (np.array(tr1.get_position()) + np.array(tr2.get_position())) / 2.0
        rc.move_to_pos(pr, panda_1, lift_pos, z_offset=0.2)
        rc.grasp(pr, gripper_1, False)

        lift_pos[0] -= 0.45
        rc.move_to_pos(pr, panda_1, lift_pos, z_offset=0.2)

        cube_pos_from_im = rc.location_from_depth_cam(pr, d_cam, cube)
        rc.move_to_pos(pr, panda_2, cube_pos_from_im, z_offset=-0.021)
        rc.grasp(pr, gripper_2, True)

        rc.move_above_object(pr, panda_2, tr2, z_offset=0.1)
        rc.grasp(pr, gripper_2, False)

        target_diff = np.abs(np.array(cube.get_position()) - np.array(tr2.get_position()))
        if (target_diff[0] <= 0.453  and target_diff[1] <= 0.453):
            sim_result.append("Success!")
        else:
            sim_result.append("Failure: Missed Target")

        pr.stop()


    except Exception as e:
        print("There was an error, it was:")
        print(e)
        sim_result.append(e)
        # pr.stop()

    # # Clean up for next iteration
    # if i < max_sims - 1:
    #     for o_list in c_objs.values():
    #         for o in o_list:
    #             o.remove()

    pr.shutdown()

print("Phew! We got home nice and safe...")

print(len(sim_result))
print(sim_result)