# -*- coding: utf-8 -*-
"""
Created on Feb 26 15:08 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import unittest
import os
import numpy as np
import numpy.testing as npt

from sharc.map.topography import Topography


class TopographyTest(unittest.TestCase):
    TEST_VALUES = {
        'low_left': [664740.0, 7799900.0],
        'up_right': [672800.0, 7805440.0],
        'resolution': 20.0,
        'nrows': 276,
        'ncols': 402
    }

    def setUp(self):
        self.our_dir = os.path.dirname(__file__)
        self.topo_file = os.path.join(self.our_dir, 'map_test_files', 'Test_brucutu_res_20m.asc')
        self.topo_data = Topography()
        self.topo_data.parse_raster_data(self.topo_file)

    def test_topography_parser(self):
        self.assertEqual(self.topo_data.nrows, self.TEST_VALUES['nrows'])
        self.assertEqual(self.topo_data.ncols, self.TEST_VALUES['ncols'])
        self.assertEqual(self.topo_data.resolution,
                         self.TEST_VALUES['resolution'])
        self.assertEqual(self.topo_data.low_left,
                         self.TEST_VALUES['low_left'])
        self.assertEqual(self.topo_data.up_right,
                         self.TEST_VALUES['up_right'])

    def test_get_z(self):
        x = np.array([668899.0, 665881.0, 671632.0, 666998.0])
        y = np.array([7803680.0, 7805070.0, 7800620.0, 7804701.0])
        z = self.topo_data.get_z(x, y)
        npt.assert_equal(z, np.array([1091, 660, 691, 720]))


if __name__ == '__main__':
    unittest.main()
