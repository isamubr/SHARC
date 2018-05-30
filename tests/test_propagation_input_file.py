# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 14:40:58 2018

@author: Calil
"""

import unittest
import numpy.testing as npt
import numpy as np
import os
from glob import glob

from sharc.propagation.propagation_input_files import PropagationInputFiles
from sharc.parameters.parameters_imt_vale import ParametersImtVale


class PropagationInputFilesTest(unittest.TestCase):

    def setUp(self):
        self.parameters_imt = ParametersImtVale(imt_link='DOWNLINK')
        self.my_path = os.path.dirname(__file__)
        # Test 1
        self.parameters_imt.path_loss_folder = os.path.join(self.my_path, 'propagation_test_files', 'test_1')
        self.parameters_imt.bs_physical_data_file = os.path.join(self.my_path,
                                                                 'topology_input_map_files',
                                                                 'cell_data_test_file.xlsx')
        self.parameters_imt.read_input_cell_data_file(self.parameters_imt.bs_physical_data_file)
        self.parameters_imt.path_loss_files = \
            self.parameters_imt.get_path_loss_files(self.parameters_imt.path_loss_folder)
        self.propagation_1 = PropagationInputFiles(self.parameters_imt)

        # Test 2
        self.parameters_imt.path_loss_folder = os.path.join(self.my_path, 'propagation_test_files', 'test_2')
        self.parameters_imt.path_loss_files = \
            self.parameters_imt.get_path_loss_files(self.parameters_imt.path_loss_folder)
        self.propagation_2 = PropagationInputFiles(self.parameters_imt)

    def test_files(self):
        # Test 1
        test_dummy_1_file_name = os.path.join(self.my_path, 'propagation_test_files', 'test_1', 'DUMMY0010.txt')
        test_dummy_2_file_name = os.path.join(self.my_path, 'propagation_test_files', 'test_1', 'DUMMY0020.txt')

        self.assertCountEqual(self.propagation_1.files, [test_dummy_1_file_name, test_dummy_2_file_name])

        # Test 2
        test_dummy_1_file_name = os.path.join(self.my_path, 'propagation_test_files', 'test_2', 'DUMMY0010.txt')
        test_dummy_2_file_name = os.path.join(self.my_path, 'propagation_test_files', 'test_2', 'DUMMY0020.txt')
        test_dummy_3_file_name = os.path.join(self.my_path, 'propagation_test_files', 'test_2', 'DUMMY0030.txt')

        self.assertCountEqual(self.propagation_2.files,
                              [test_dummy_1_file_name, test_dummy_2_file_name, test_dummy_3_file_name])

    def test_parameters(self):
        # Test 3
        self.parameters_imt.path_loss_folder = os.path.join(self.my_path, 'propagation_test_files', 'test_3')
        self.parameters_imt.path_loss_files = \
            self.parameters_imt.get_path_loss_files(self.parameters_imt.path_loss_folder)
        propagation_3 = PropagationInputFiles(self.parameters_imt)

        self.assertDictEqual(propagation_3.path_loss['DUMMY01'][0],
                             {"ANTENNA": 'DUMMY01',
                              "LOCATION": np.nan,
                              "FREQUENCY": 2600.0,
                              "POWER": ['10.000', 'W', 'EIRP'],
                              "ANTENNATYPE": 'ISO',
                              "LOWER_LEFT": [10.0, 10.0],
                              "UPPER_RIGHT": [50.0, 50.0],
                              "HEIGHT": np.nan,
                              "RESOLUTION": 10.0,
                              "RECEIVER_GAIN": 0.0})

    def test_path_loss(self):
        # Test 1
        self.assertTrue('DUMMY01' in list(self.propagation_1.path_loss.keys()))
        self.assertTrue('DUMMY02' in list(self.propagation_1.path_loss.keys()))
        self.assertEqual(len(list(self.propagation_1.path_loss.keys())), 2)
        self.assertDictEqual(self.propagation_1.path_loss['DUMMY01'][0],
                             {"ANTENNA": 'DUMMY01',
                              "LOCATION": [24.0, 42.0, 44.0],
                              "FREQUENCY": 2600.0,
                              "POWER": ['10.000', 'W', 'EIRP'],
                              "ANTENNATYPE": 'ISO',
                              "LOWER_LEFT": [10.0, 10.0],
                              "UPPER_RIGHT": [50.0, 50.0],
                              "HEIGHT": 1.5,
                              "RESOLUTION": 10.0,
                              "RECEIVER_GAIN": 0.0})
        self.assertDictEqual(self.propagation_1.path_loss['DUMMY02'][0],
                             {"ANTENNA": 'DUMMY02',
                              "LOCATION": [42.0, 24.0, 44.0],
                              "FREQUENCY": 2500.0,
                              "POWER": ['10.000', 'W', 'EIRP'],
                              "ANTENNATYPE": 'ISO',
                              "LOWER_LEFT": [10.0, 10.0],
                              "UPPER_RIGHT": [50.0, 50.0],
                              "HEIGHT": 1.5,
                              "RESOLUTION": 10.0,
                              "RECEIVER_GAIN": 0.0})
        self.assertEqual(self.propagation_1.path_loss['DUMMY01'][1].shape,
                         (5, 5))
        self.assertEqual(self.propagation_1.path_loss['DUMMY02'][1].shape,
                         (5, 5))
        npt.assert_equal(self.propagation_1.path_loss['DUMMY01'][1],
                         np.array([[11, 12, 13, 14, 15],
                                   [21, 22, 23, 24, 25],
                                   [31, 32, 33, 34, 35],
                                   [41, 42, 43, 44, 45],
                                   [51, 52, 53, 54, 55]]))
        npt.assert_equal(self.propagation_1.path_loss['DUMMY02'][1],
                         np.array([[51, 52, 53, 54, 55],
                                   [41, 42, 43, 44, 45],
                                   [31, 32, 33, 34, 35],
                                   [21, 22, 23, 24, 25],
                                   [11, 12, 13, 14, 15]]))

        # Test 2
        self.assertEqual(self.propagation_2.path_loss['DUMMY01'][1].shape,
                         (5, 4))
        self.assertEqual(self.propagation_2.path_loss['DUMMY02'][1].shape,
                         (4, 5))
        self.assertEqual(self.propagation_2.path_loss['DUMMY03'][1].shape,
                         (5, 5))
        npt.assert_equal(self.propagation_2.path_loss['DUMMY01'][1],
                         np.array([[11, 12, 13, 14],
                                   [21, 22, 23, 24],
                                   [31, 32, 33, 34],
                                   [41, 42, 43, 44],
                                   [51, 52, 53, 54]]))
        npt.assert_equal(self.propagation_2.path_loss['DUMMY02'][1],
                         np.array([[51, 52, 53, 54, 55],
                                   [41, 42, 43, 44, 45],
                                   [31, 32, 33, 34, 35],
                                   [21, 22, 23, 24, 25]]))
        npt.assert_equal(self.propagation_2.path_loss['DUMMY03'][1],
                         np.array([[51, 52, 53, 54, 55],
                                   [41, 42, 43, 44, 45],
                                   [31, 32, 33, 34, 35],
                                   [21, 22, 23, 24, 25],
                                   [11, 12, 13, 14, 15]]))

    def test_get_loss(self):
        # Test 1
        c_id = np.array(['DUMMY01', 'DUMMY02'])
        ue_x = np.array([35.0, 12.5, 49.9, 10.0, 10.0])
        ue_y = np.array([35.0, 42.0, 19.9, 10.0, 20.0])
        pl = self.propagation_1.get_loss(bs_id=c_id,
                                         ue_position_x=ue_x,
                                         ue_position_y=ue_y)
        npt.assert_equal(pl, np.array([[33.0, 41.0, 14.0, 11.0, 21.0],
                                       [33.0, 21.0, 54.0, 51.0, 41.0]]))

        # Test 2
        c_id = np.array(['DUMMY01', 'DUMMY02', 'DUMMY03'])
        ue_x = np.array([35.0, 12.5, 49.9, 10.0, 10.0])
        ue_y = np.array([35.0, 42.0, 19.9, 10.0, 20.0])
        pl = self.propagation_2.get_loss(bs_id=c_id,
                                         ue_position_x=ue_x,
                                         ue_position_y=ue_y)
        npt.assert_equal(pl, np.array([[33.0, 41.0, 14.0, 11.0, 21.0],
                                       [33.0, 21.0, 54.0, 51.0, 41.0],
                                       [33.0, 21.0, 54.0, 51.0, 41.0]]))


if __name__ == '__main__':
    unittest.main()
