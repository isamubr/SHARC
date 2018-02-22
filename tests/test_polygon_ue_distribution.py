# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 16:23:22 2018

@author: Calil
"""

import unittest
import numpy.testing as npt
import numpy as np
from shapely.geometry import Polygon

from sharc.polygon_ue_distribution import PolygonUeDistribution

class PolygonUeDistributionTest(unittest.TestCase):
    
    def setUp(self):
        # Test 1
        low_left = [10.0, 10.0]
        up_right = [60.0, 60.0]
        res = 10.0
        self.poly_dist_1 = PolygonUeDistribution(low_left,up_right,res)
        
        # Test 2
        # TODO: create larger grid for Test 2
        
    def test_construction(self):
        # Test 1
        self.assertListEqual(self.poly_dist_1.low_left,[10.0, 10.0])
        self.assertListEqual(self.poly_dist_1.up_right,[60.0, 60.0])
        self.assertEqual(self.poly_dist_1.resolution,10.0)
        npt.assert_equal(self.poly_dist_1.x_vals,
                         np.array([15.0, 25.0, 35.0, 45.0, 55.0]))
        npt.assert_equal(self.poly_dist_1.y_vals,
                         np.array([15.0, 25.0, 35.0, 45.0, 55.0]))
    
    def test_map_polygons(self):
        # Test 1
        poly_1 = Polygon([(10,10),(10,30),(30,30),(30,10)])
        poly_2 = Polygon([(20,20),(60,50),(60,20),(20,50)])
        poly_3 = Polygon([(20,50),(20,70),(40,50)])
        poly_list = [poly_1,poly_2,poly_3]
        self.poly_dist_1.map_polygons(poly_list)
        self.assertEqual(self.poly_dist_1.poly_points[0][0],poly_1)
        npt.assert_equal(self.poly_dist_1.poly_points[0][1],
                         np.array([15.0,15.0,25.0,25.0]))
        npt.assert_equal(self.poly_dist_1.poly_points[0][2],
                         np.array([15.0,25.0,15.0,25.0]))
        self.assertEqual(self.poly_dist_1.poly_points[0][3],4)
        self.assertEqual(self.poly_dist_1.poly_points[1][0],poly_2)
        npt.assert_equal(self.poly_dist_1.poly_points[1][1],
                         np.array([25.0,25.0,25.0,35.0,45.0,55.0,55.0,55.0]))
        npt.assert_equal(self.poly_dist_1.poly_points[1][2],
                         np.array([25.0,35.0,45.0,35.0,35.0,25.0,35.0,45.0]))
        self.assertEqual(self.poly_dist_1.poly_points[1][3],8)
        # Pixel centered at the edege of polygon is not included
        self.assertEqual(self.poly_dist_1.poly_points[2][0],poly_3)
        npt.assert_equal(self.poly_dist_1.poly_points[2][1],np.array([25.0]))
        npt.assert_equal(self.poly_dist_1.poly_points[2][2],np.array([55.0]))
        self.assertEqual(self.poly_dist_1.poly_points[2][3],1)
    
    def test_distribute_ues(self):
        # Test 1
        poly_1 = Polygon([(10,10),(10,30),(30,30),(30,10)])
        poly_2 = Polygon([(20,20),(60,50),(60,20),(20,50)])
        poly_3 = Polygon([(20,50),(20,70),(40,50)])
        poly_list = [poly_1,poly_2,poly_3]
        num_ues = [2,3,1]
        self.poly_dist_1.map_polygons(poly_list)
        x, y = self.poly_dist_1.distribute_ues(num_ues)
        self.assertTrue(set(x[0:2]) <= set([15,25]))
        self.assertTrue(set(x[2:5]) <= set([25,35,45,55]))
        self.assertTrue(set(x[5:]) <= set([25,35]))
        self.assertTrue(set(y[0:2]) <= set([15,25]))
        self.assertTrue(set(y[2:5]) <= set([25,35,45]))
        self.assertTrue(set(y[5:]) <= set([55]))
    
if __name__ == '__main__':
    unittest.main()