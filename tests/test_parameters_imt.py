#-*- coding: utf-8 -*-
"""
Created on Feb 07 18:07 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""
import unittest
import pandas as pd
import numpy as np
import numpy.testing as npt
from array import array
import os

from sharc.parameters.parameters_imt_vale import ParametersImtVale


class ParametersImtTest(unittest.TestCase):

    def setUp(self):
        self.our_dir = os.path.dirname(__file__)
        self.parameters_imt = ParametersImtVale(imt_link='DOWNLINK')
        self.parameters_imt.utm_zone = '23K'
        self.parameters_imt.ue_polygon_file = os.path.join(self.our_dir,
                                                           'kml_polygon_test_files',
                                                           'PolygonBrucutuTest.kml')
        self.parameters_imt.bs_physical_data_file = os.path.join(self.our_dir,
                                                                 'topology_input_map_files',
                                                                 'cell_data_test_file.xlsx')
        self.parameters_imt.path_loss_folder = os.path.join(self.our_dir, 'propagation_test_files', 'test_1')

        self.parameters_imt.read_input_cell_data_file(self.parameters_imt.bs_physical_data_file)

    def test_read_input_ue_polygon_kml_file(self):
        poly_list = self.parameters_imt.read_input_ue_polygon_kml_file(self.parameters_imt.ue_polygon_file,
                                                                       self.parameters_imt.utm_zone)
        self.assertEqual(len(poly_list), 4)
        x_ref = array('d', [671451.6655523514, 671138.9485129344, 671405.6879327301, 671667.1419657345, 671596.2585219325,
                            671451.6655523514])
        y_ref = array('d', [7803479.999423526, 7802850.070545908, 7802922.00750212, 7803302.335699345, 7803504.286430689,
                            7803479.999423526])
        self.assertEqual(poly_list[0].exterior.coords.xy[0], x_ref)
        self.assertEqual(poly_list[0].exterior.coords.xy[1], y_ref)

    def test_get_path_loss_files(self):
        file_list = self.parameters_imt.get_path_loss_files(self.parameters_imt.path_loss_folder)
        test_dummy_1_file_name = os.path.join(self.our_dir, 'propagation_test_files', 'test_1', 'DUMMY0010.txt')
        test_dummy_2_file_name = os.path.join(self.our_dir, 'propagation_test_files', 'test_1', 'DUMMY0020.txt')
        self.assertCountEqual(file_list, [test_dummy_1_file_name, test_dummy_2_file_name])


if __name__ == '__main__':
    unittest.main()
