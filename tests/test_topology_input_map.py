# -*- coding: utf-8 -*-
"""
Created on Feb 07 16:53 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import unittest
import numpy as np
import numpy.testing as npt
import os

from sharc.parameters.parameters_imt_vale import ParametersImtVale
from sharc.topology.topology_input_map import TopologyInputMap
from sharc.map.topography import Topography
from shapely.geometry import Polygon


class TopologyInputMapTest(unittest.TestCase):
    # These are the same parameters that come inside the cell data file
    TEST_VECTOR = {
        'strSiteID': ['DUMMY001', 'DUMMY002', 'DUMMY003', 'DUMMY004'],
        'strCellID': ['DUMMY0010', 'DUMMY0020', 'DUMMY0030', 'DUMMY0040'],
        'dDLCarrierMHz': [2600, 2601, 2602, 2603],
        'bDeleted': [0, 0, 0, 0],
        'dDLBWMHz': [5, 6, 7, 8],
        'dHeight': [10, 11, 12, 13],
        'NodeType': ['Macro1', 'Pico', 'Macro1', 'Pico'],
        'PilotPower': [0, -1, -2, -3], 'dBearing': [0, 0, 0, 0],
        'pattern': ['omni_10dBi', 'omni_10dBi', 'omni_10dBi', 'omni_10dBi'],
        'dWECoordinateMeter': [669242.9, 671354.38, 671354.38, 669242.9],
        'dMaxTxPowerdBm': [20, 21, 22, 23],
        'dEDownTilt': [0, 0, 0, 0],
        'dMDownTilt': [0, -1, -2, -3],
        'dSNCoordinateMeter': [7803099.9, 7803206.72, 7803099.9, 7803206.72]
    }

    def setUp(self):
        self.random_number_gen = np.random.RandomState(seed=200)
        # Test 1
        parameters_imt = ParametersImtVale(imt_link='DOWNLINK')
        self.our_path = os.path.dirname(__file__)
        bs_physical_data_file = os.path.join(self.our_path, 'topology_input_map_files', 'cell_data_test_file.xlsx')
        parameters_imt.bs_data = parameters_imt.read_input_cell_data_file(bs_physical_data_file)
        topo = Topography()
        topo.low_left = [664740.0, 7799900.0]
        topo.up_right = [672780.0, 7805420.0]
        topo.resolution = 20.0
        topo.nrows = 276
        topo.ncols = 402
        topo.topography_grid = np.ones((topo.nrows, topo.ncols))
        self.topology_1 = TopologyInputMap(parameters_imt, topo)
        # Test 2
        parameters_imt = ParametersImtVale(imt_link='DOWNLINK')
        self.our_path = os.path.dirname(__file__)
        bs_physical_data_file = os.path.join(self.our_path, 'topology_input_map_files', 'cell_data_test_file_2.xlsx')
        parameters_imt.bs_data = parameters_imt.read_input_cell_data_file(bs_physical_data_file)
        topo = Topography()
        topo.low_left = [10.0, 10.0]
        topo.up_right = [60.0, 60.0]
        topo.resolution = 10.0
        topo.nrows = 5
        topo.ncols = 5
        topo.topography_grid = np.ones((topo.nrows, topo.ncols))
        self.topology_2 = TopologyInputMap(parameters_imt, topo)

    def test_coordinates(self):
        self.topology_1.calculate_coordinates()

        x_ref = np.array(self.TEST_VECTOR['dWECoordinateMeter'])
        y_ref = np.array(self.TEST_VECTOR['dSNCoordinateMeter'])
        azimuth_ref = np.array(self.TEST_VECTOR['dBearing'])
        elevation_ref = np.array(self.TEST_VECTOR['dMDownTilt'])
        num_bs_ref = len(self.TEST_VECTOR['strSiteID'])

        npt.assert_array_equal(self.topology_1.x, x_ref)
        npt.assert_array_equal(self.topology_1.y, y_ref)
        npt.assert_array_equal(self.topology_1.azimuth, azimuth_ref)
        npt.assert_array_equal(self.topology_1.elevation, elevation_ref)
        self.assertEqual(self.topology_1.num_base_stations, num_bs_ref)

    def test_map_polygons(self):
        poly_1 = Polygon([(10, 10), (10, 30), (30, 30), (30, 10)])
        poly_2 = Polygon([(20, 20), (60, 50), (60, 20), (20, 50)])
        poly_3 = Polygon([(20, 50), (20, 70), (40, 50)])
        poly_list = [poly_1, poly_2, poly_3]
        self.topology_2.map_polygons(poly_list)
        self.assertEqual(self.topology_2.poly_points[0][0], poly_1)
        npt.assert_equal(self.topology_2.poly_points[0][1],
                         np.array([15.0, 15.0, 25.0, 25.0]))
        npt.assert_equal(self.topology_2.poly_points[0][2],
                         np.array([15.0, 25.0, 15.0, 25.0]))
        self.assertEqual(self.topology_2.poly_points[0][3], 4)
        self.assertEqual(self.topology_2.poly_points[1][0], poly_2)
        npt.assert_equal(self.topology_2.poly_points[1][1],
                         np.array([25.0, 25.0, 25.0, 35.0, 45.0, 55.0, 55.0, 55.0]))
        npt.assert_equal(self.topology_2.poly_points[1][2],
                         np.array([25.0, 35.0, 45.0, 35.0, 35.0, 25.0, 35.0, 45.0]))
        self.assertEqual(self.topology_2.poly_points[1][3], 8)
        # Pixel centered at the edege of polygon is not included
        self.assertEqual(self.topology_2.poly_points[2][0], poly_3)
        npt.assert_equal(self.topology_2.poly_points[2][1], np.array([25.0]))
        npt.assert_equal(self.topology_2.poly_points[2][2], np.array([55.0]))
        self.assertEqual(self.topology_2.poly_points[2][3], 1)

    def test_distribute_ues(self):
        poly_1 = Polygon([(10, 10), (10, 30), (30, 30), (30, 10)])
        poly_2 = Polygon([(20, 20), (60, 50), (60, 20), (20, 50)])
        poly_3 = Polygon([(20, 50), (20, 70), (40, 50)])
        poly_list = [poly_1, poly_2, poly_3]
        num_ues = [2, 3, 1]
        self.topology_2.map_polygons(poly_list)
        self.topology_2.distribute_ues(num_ues, self.random_number_gen)
        self.assertTrue(set(self.topology_2.x_ue[0:2]) <= set([15, 25]))
        self.assertTrue(set(self.topology_2.x_ue[2:5]) <= set([25, 35, 45, 55]))
        self.assertTrue(set(self.topology_2.x_ue[5:]) <= set([25, 35]))
        self.assertTrue(set(self.topology_2.y_ue[0:2]) <= set([15, 25]))
        self.assertTrue(set(self.topology_2.y_ue[2:5]) <= set([25, 35, 45]))
        self.assertTrue(set(self.topology_2.y_ue[5:]) <= set([55]))


if __name__ == '__main__':
    unittest.main()
