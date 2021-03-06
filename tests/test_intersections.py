import unittest

import numpy as np
from multimethod import DispatchError
from scipy.spatial import HalfspaceIntersection

from probRobScene.core.intersections import intersect, to_hsi
from probRobScene.core.regions import All, Empty, Spherical, Cuboid, Intersection, Rectangle3D, HalfSpace, ConvexPolyhedron, contains, contains_point, ConvexPolygon3D
from probRobScene.core.vectors import Vector3D, rotate_euler, rotate_euler_v3d


class TestIntersections(unittest.TestCase):
    """
    Regions:
        Halfspace
        ConvexPolyhedron
        ConvexPolygon3D
        Cuboid
        Rectangle3D
        Plane
        Line
        LineSeg
        PointSet
    """

    def test_all_all(self):
        it = intersect(All(), All())
        self.assertEqual(All(), it)

    def test_all_empty(self):
        it = intersect(All(), Empty())
        self.assertEqual(Empty(), it)

    def test_all_others(self):
        s = Spherical(Vector3D(0, 0, 0), 3)
        c = Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1)

        it_1 = intersect(All(), s)
        it_2 = intersect(All(), c)

        self.assertEqual(it_1, s)
        self.assertEqual(it_2, c)

    def test_others_all(self):
        s = Spherical(Vector3D(0, 0, 0), 3)
        c = Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1)

        it_1 = intersect(s, All())
        it_2 = intersect(c, All())

        self.assertEqual(it_1, s)
        self.assertEqual(it_2, c)

    def test_empty_all(self):
        self.assertEqual(Empty(), intersect(Empty(), All()))

    def test_empty_empty(self):
        self.assertEqual(Empty(), intersect(Empty(), Empty()))

    def test_empty_others(self):
        s = Spherical(Vector3D(0, 0, 0), 3)
        c = Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1)
        self.assertEqual(Empty(), intersect(Empty(), s))
        self.assertEqual(Empty(), intersect(Empty(), c))

    def test_others_empty(self):
        s = Spherical(Vector3D(0, 0, 0), 3)
        c = Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1)
        self.assertEqual(Empty(), intersect(s, Empty()))
        self.assertEqual(Empty(), intersect(c, Empty()))

    def test_spherical_others(self):
        s = Spherical(Vector3D(0, 0, 0), 3)
        c = Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1)
        self.assertRaises(DispatchError, intersect, s, c)

    def test_others_spherical(self):
        s = Spherical(Vector3D(0, 0, 0), 3)
        c = Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1)
        self.assertRaises(DispatchError, intersect, c, s)

    def test_intersection_others(self):
        inter = Intersection([Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1), Rectangle3D(1, 1, Vector3D(0, 0, 0), Vector3D(0, 0, 0))])
        c = Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1)
        self.assertRaises(DispatchError, intersect, c, inter)

    def test_others_intersection(self):
        inter = Intersection([Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1), Rectangle3D(1, 1, Vector3D(0, 0, 0), Vector3D(0, 0, 0))])
        c = Cuboid(Vector3D(0, 0, 0), Vector3D(0, 0, 0), 1, 1, 1)
        self.assertRaises(DispatchError, intersect, inter, c)

    def test_halfspace_halfspace_same(self):
        hs_1 = HalfSpace(Vector3D(0, 0, 0), Vector3D(0, 1, 0))
        hs_2 = HalfSpace(Vector3D(0, 0, 0), Vector3D(0, 1, 0))
        it = intersect(hs_1, hs_2)

        self.assertTrue(isinstance(it, ConvexPolyhedron))

        self.assertTrue(contains_point(hs_1, Vector3D(*it.hsi.interior_point)))
        self.assertTrue(contains_point(hs_2, Vector3D(*it.hsi.interior_point)))

    def test_halfspace_halfspace_diff(self):
        hs_1 = HalfSpace(Vector3D(0, 0, 0), Vector3D(0, 1, 0))
        hs_2 = HalfSpace(Vector3D(0, 1.0, 0), Vector3D(0, -1, 0))
        it = intersect(hs_1, hs_2)

        self.assertTrue(isinstance(it, ConvexPolyhedron))

        self.assertTrue(contains_point(hs_1, Vector3D(*it.hsi.interior_point)))
        self.assertTrue(contains_point(hs_2, Vector3D(*it.hsi.interior_point)))

    def test_halfspace_halfspace_redundant(self):
        hs_1 = HalfSpace(Vector3D(0, 0, 0), Vector3D(0, 1, 0))
        hs_2 = HalfSpace(Vector3D(0, 1.0, 0), Vector3D(0, 1, 0))
        it = intersect(hs_1, hs_2)

        self.assertTrue(isinstance(it, ConvexPolyhedron))

        self.assertTrue(contains_point(hs_1, Vector3D(*it.hsi.interior_point)))
        self.assertTrue(contains_point(hs_2, Vector3D(*it.hsi.interior_point)))

    def test_halfspace_halfspace_noIntersection(self):
        hs_1 = HalfSpace(Vector3D(0, 1, 0), Vector3D(0, 1, 0))
        hs_2 = HalfSpace(Vector3D(0, -1, 0), Vector3D(0, -1, 0))
        it = intersect(hs_1, hs_2)

        self.assertTrue(isinstance(it, Empty))

    def test_halfspace_halfspace_noIntersectionByDistance(self):
        hs_1 = HalfSpace(Vector3D(0, 1, 0), Vector3D(0, 1, 0))
        hs_2 = HalfSpace(Vector3D(0, 10000, 0), Vector3D(0, 1, 0))
        it = intersect(hs_1, hs_2)

        self.assertTrue(isinstance(it, Empty))

    def test_halfspace_convpolyh_intersection(self):
        hs = HalfSpace(Vector3D(0, 1, 0), Vector3D(0, 1, 0))
        cp = ConvexPolyhedron(to_hsi(Cuboid(Vector3D(0.0, 0.0, 0.0), Vector3D(0, 0, 0), 5, 5, 5)))
        it = intersect(hs, cp)

        self.assertTrue(isinstance(it, ConvexPolyhedron))
        self.assertTrue(contains_point(hs, Vector3D(*it.hsi.interior_point)))
        self.assertTrue(contains_point(cp, Vector3D(*it.hsi.interior_point)))

    def test_halfspace_convpolyh_noIntersection(self):
        hs = HalfSpace(Vector3D(0, 4, 0), Vector3D(0, 1, 0))
        cp = ConvexPolyhedron(to_hsi(Cuboid(Vector3D(0.0, 0.0, 0.0), Vector3D(0, 0, 0), 1, 1, 1)))
        it = intersect(hs, cp)

        self.assertTrue(isinstance(it, Empty))

    def test_halfspace_convpg_noIntersection(self):
        hs = HalfSpace(Vector3D(0, 4, 0), Vector3D(0, 1, 0))
        hsi = HalfspaceIntersection(
            np.array([
                [1, 0, -3],
                [0, 1, -3],
                [-1, 0, 0],
                [0, -1, 0]
            ]),
            np.array([1.0, 1.0]))
        cp = ConvexPolygon3D(hsi=hsi, origin=Vector3D(0, 0, 0), rot=Vector3D(0, 0, 0))
        it = intersect(hs, cp)

        self.assertTrue(isinstance(it, Empty))

    def test_halfspace_convpg_intersection(self):
        hs = HalfSpace(Vector3D(0, 2, 0), Vector3D(0, 1, 0))
        hsi = HalfspaceIntersection(
            np.array([
                [1, 0, -3],
                [0, 1, -3],
                [-1, 0, 0],
                [0, -1, 0]
            ]),
            np.array([1.0, 1.0]))
        cp = ConvexPolygon3D(hsi=hsi, origin=Vector3D(0, 0, 0), rot=Vector3D(0, 0, 0))
        it = intersect(hs, cp)

        int_point_3d: Vector3D = rotate_euler_v3d(Vector3D(*it.hsi.interior_point, 0.0), it.rot) + it.origin

        self.assertTrue(isinstance(it, ConvexPolygon3D))
        self.assertTrue(contains_point(hs, int_point_3d))
        self.assertTrue(contains_point(cp, int_point_3d))

    def test_halfspace_cuboid_intersect(self):
        pass

    def test_halfspace_cuboid_noIntersect(self):
        pass

    def test_halfspace_rect3d_intersect(self):
        pass

    def test_halfspace_rect3d_noIntersect(self):
        pass

    def test_halfspace_plane_intersect(self):
        pass

    def test_halfspace_plane_noIntersect(self):
        pass

    def test_halfspace_line_intersect(self):
        pass

    def test_halfspace_line_noIntersect(self):
        pass

    def test_halfspace_lineSeg_intersect(self):
        pass

    def test_halfspace_lineSeg_noIntersect(self):
        pass

    def test_halfspace_pointset_intersect(self):
        pass

    def test_halfspace_pointset_noIntersect(self):
        pass




if __name__ == '__main__':
    unittest.main()
