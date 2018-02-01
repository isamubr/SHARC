# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 14:40:58 2018

@author: Calil
"""

import unittest
import numpy.testing as npt
import numpy as np

from sharc.propagation.propagation_input_file import PropagationInputFile
from sharc.support.named_tuples import PathLossHeader

class PropagationInputFileTest(unittest.TestCase):
    
    def setUp(self):
        # Test 1
        input_folder = "propagation_test_files\\test_1"
        self.propagation_1 = PropagationInputFile(input_folder)
        
        # Test 2
        input_folder = "propagation_test_files\\test_2"
        self.propagation_2 = PropagationInputFile(input_folder)
        
    def test_files(self):
        # Test 1
        npt.assert_equal(self.propagation_1.files,
                         ['propagation_test_files\\test_1\\test_dummy_1.txt',
                          'propagation_test_files\\test_1\\test_dummy_2.txt'])
        # Test 2
        npt.assert_equal(self.propagation_2.files,
                         ['propagation_test_files\\test_2\\test_dummy_1.txt',
                          'propagation_test_files\\test_2\\test_dummy_2.txt',
                          'propagation_test_files\\test_2\\test_dummy_3.txt'])
    
    def test_path_loss(self):
        # Test 1
        npt.assert_equal(list(self.propagation_1.path_loss.keys()),
                         ['DUMMY02', 'DUMMY01'])
        self.assertEqual(self.propagation_1.path_loss['DUMMY01'][0],
                         PathLossHeader(antenna='DUMMY01', 
                                        location=[24.0, 42.0, 44.0], 
                                        frequency=2600.0, 
                                        power=['10.000', 'W', 'EIRP'], 
                                        antennatype='ISO', 
                                        lower_left=[10.0, 10.0], 
                                        upper_right=[60.0, 60.0], 
                                        height=1.5, 
                                        resolution=10.0, 
                                        receiver_gain=0.0))
        self.assertEqual(self.propagation_1.path_loss['DUMMY02'][0],
                         PathLossHeader(antenna='DUMMY02', 
                                        location=[42.0, 24.0, 44.0], 
                                        frequency=2500.0, 
                                        power=['10.000', 'W', 'EIRP'], 
                                        antennatype='ISO', 
                                        lower_left=[10.0, 10.0], 
                                        upper_right=[60.0, 60.0], 
                                        height=1.5, 
                                        resolution=10.0, 
                                        receiver_gain=0.0))
        self.assertEqual(self.propagation_1.path_loss['DUMMY01'][1].shape,
                         (5, 5))
        self.assertEqual(self.propagation_1.path_loss['DUMMY02'][1].shape,
                         (5, 5))
        npt.assert_equal(self.propagation_1.path_loss['DUMMY01'][1],
                         np.array([[-11, -12, -13, -14, -15],
                                   [-21, -22, -23, -24, -25],
                                   [-31, -32, -33, -34, -35],
                                   [-41, -42, -43, -44, -45],
                                   [-51, -52, -53, -54, -55]]))
        npt.assert_equal(self.propagation_1.path_loss['DUMMY02'][1],
                         np.array([[-51, -52, -53, -54, -55],
                                   [-41, -42, -43, -44, -45],
                                   [-31, -32, -33, -34, -35],
                                   [-21, -22, -23, -24, -25],
                                   [-11, -12, -13, -14, -15]]))
    
        # Test 2
        self.assertEqual(self.propagation_2.path_loss['DUMMY01'][1].shape,
                         (4, 5))
        self.assertEqual(self.propagation_2.path_loss['DUMMY02'][1].shape,
                         (5, 4))
        self.assertEqual(self.propagation_2.path_loss['DUMMY03'][1].shape,
                         (5, 5))
        npt.assert_equal(self.propagation_2.path_loss['DUMMY01'][1],
                         np.array([[-11, -12, -13, -14, -15],
                                   [-21, -22, -23, -24, -25],
                                   [-31, -32, -33, -34, -35],
                                   [-41, -42, -43, -44, -45]]))
        npt.assert_equal(self.propagation_2.path_loss['DUMMY02'][1],
                         np.array([[-51, -52, -53, -54],
                                   [-41, -42, -43, -44],
                                   [-31, -32, -33, -34],
                                   [-21, -22, -23, -24],
                                   [-11, -12, -13, -14]]))
        npt.assert_equal(self.propagation_2.path_loss['DUMMY03'][1],
                         np.array([[-51, -52, -53, -54, -55],
                                   [-41, -42, -43, -44, -45],
                                   [-31, -32, -33, -34, -35],
                                   [-21, -22, -23, -24, -25],
                                   [-11, -12, -13, -14, -15]]))
        
        
if __name__ == '__main__':
    unittest.main()