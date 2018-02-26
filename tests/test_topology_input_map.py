#-*- coding: utf-8 -*-
"""
Created on Feb 07 16:53 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import unittest
import pandas as pd
import numpy as np
import numpy.testing as npt

from sharc.parameters.parameters_imt import ParametersImt
from sharc.topology.topology_input_map import TopologyInputMap
# TODO: replace this with Topography class
from sharc.support.named_tuples import Topography
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
        parameters_imt = ParametersImt()
        bs_physical_data_file = './topology_input_map_files/cell_data_test_file.xlsx'
        parameters_imt.bs_data = parameters_imt.read_input_cell_data_file(bs_physical_data_file)
        topo = Topography([10.0,10.0],
                          [60.0,60.0],
                          10.0)
        self.topology = TopologyInputMap(parameters_imt,topo)

    def test_coordinates(self):

        self.topology.calculate_coordinates()

        x_ref = np.array(self.TEST_VECTOR['dWECoordinateMeter'])
        y_ref = np.array(self.TEST_VECTOR['dSNCoordinateMeter'])
        azimuth_ref = np.array(self.TEST_VECTOR['dBearing'])
        elevation_ref = np.array(self.TEST_VECTOR['dMDownTilt'])
        num_bs_ref = len(self.TEST_VECTOR['strSiteID'])

        npt.assert_array_equal(self.topology.x, x_ref)
        npt.assert_array_equal(self.topology.y, y_ref)
        npt.assert_array_equal(self.topology.azimuth, azimuth_ref)
        npt.assert_array_equal(self.topology.elevation, elevation_ref)
        self.assertEqual(self.topology.num_base_stations, num_bs_ref)
        
    def test_map_polygons(self):
        poly_1 = Polygon([(10,10),(10,30),(30,30),(30,10)])
        poly_2 = Polygon([(20,20),(60,50),(60,20),(20,50)])
        poly_3 = Polygon([(20,50),(20,70),(40,50)])
        poly_list = [poly_1,poly_2,poly_3]
        self.topology.map_polygons(poly_list)
        self.assertEqual(self.topology.poly_points[0][0],poly_1)
        npt.assert_equal(self.topology.poly_points[0][1],
                         np.array([15.0,15.0,25.0,25.0]))
        npt.assert_equal(self.topology.poly_points[0][2],
                         np.array([15.0,25.0,15.0,25.0]))
        self.assertEqual(self.topology.poly_points[0][3],4)
        self.assertEqual(self.topology.poly_points[1][0],poly_2)
        npt.assert_equal(self.topology.poly_points[1][1],
                         np.array([25.0,25.0,25.0,35.0,45.0,55.0,55.0,55.0]))
        npt.assert_equal(self.topology.poly_points[1][2],
                         np.array([25.0,35.0,45.0,35.0,35.0,25.0,35.0,45.0]))
        self.assertEqual(self.topology.poly_points[1][3],8)
        # Pixel centered at the edege of polygon is not included
        self.assertEqual(self.topology.poly_points[2][0],poly_3)
        npt.assert_equal(self.topology.poly_points[2][1],np.array([25.0]))
        npt.assert_equal(self.topology.poly_points[2][2],np.array([55.0]))
        self.assertEqual(self.topology.poly_points[2][3],1)
        
    def test_distribute_ues(self):
        poly_1 = Polygon([(10,10),(10,30),(30,30),(30,10)])
        poly_2 = Polygon([(20,20),(60,50),(60,20),(20,50)])
        poly_3 = Polygon([(20,50),(20,70),(40,50)])
        poly_list = [poly_1,poly_2,poly_3]
        num_ues = [2,3,1]
        self.topology.map_polygons(poly_list)
        self.topology.distribute_ues(num_ues)
        self.assertTrue(set(self.topology.x_ue[0:2]) <= set([15,25]))
        self.assertTrue(set(self.topology.x_ue[2:5]) <= set([25,35,45,55]))
        self.assertTrue(set(self.topology.x_ue[5:]) <= set([25,35]))
        self.assertTrue(set(self.topology.y_ue[0:2]) <= set([15,25]))
        self.assertTrue(set(self.topology.y_ue[2:5]) <= set([25,35,45]))
        self.assertTrue(set(self.topology.y_ue[5:]) <= set([55]))


if __name__ == '__main__':
    unittest.main()
