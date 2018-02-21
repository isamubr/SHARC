# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 16:23:22 2018

@author: Calil
"""

import unittest
import numpy.testing as npt
import numpy as np

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
    
    def test_distribute_ues(self):
        pass
    
if __name__ == '__main__':
    unittest.main()