#-*- coding: utf-8 -*-
"""
Created on Feb 07 18:07 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""
import unittest
import pandas as pd
import numpy as np
import numpy.testing as npt

from sharc.parameters.parameters_imt import ParametersImt


class ParametersImtTest(unittest.TestCase):

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
        pass

    def test_read_input_cell_data_file(self):

        input_file = './topology_input_map_files/cell_data_test_file.xlsx'
        bs_data = ParametersImt.read_input_cell_data_file(input_file)

        self.assertDictEqual(bs_data, self.TEST_VECTOR)


if __name__ == '__main__':
    unittest.main()
