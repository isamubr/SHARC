#-*- coding: utf-8 -*-
"""
Created on Feb 07 16:53 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import unittest
import numpy as np
import numpy.testing as npt
import os

from sharc.parameters.parameters_imt import ParametersImt
from sharc.topology.topology_input_map import TopologyInputMap


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
        self.our_path = os.path.dirname(__file__)
        bs_physical_data_file = os.path.join(self.our_path, 'topology_input_map_files', 'cell_data_test_file.xlsx')
        parameters_imt.bs_data = parameters_imt.read_input_cell_data_file(bs_physical_data_file)
        self.topology = TopologyInputMap(parameters_imt)

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


if __name__ == '__main__':
    unittest.main()
