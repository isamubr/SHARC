# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 14:39:17 2018

@author: Calil
"""

from sharc.propagation.propagation import Propagation
from sharc.support.named_tuples import PathLossHeader

import matplotlib.pyplot as plt
import numpy as np
from glob import glob

class PropagationInputFile(Propagation):
    """
    Implements path loss from specified files
    
    Attributes:
        files (list): list containing names (and path to) path loss files
        path_loss (dict): keys are the antenna names, while values are tuples
            with header of respective path loss file and np.array of path loss
            values
    """
    def __init__(self, input_folder:str):
        """
        Constructs PropagationInputFile object, initializing the path_loss
        attribute.
        
        Parameters:
            input_folder (str): path to folder containing the path loss files
        """
        super().__init__()
        
        self.files = []
        self.path_loss = dict()
        
        # Find where data begins
        begin_data_line = 12
        
        # Loop through all the txt files in the folder
        for file in glob(input_folder + "\\*.txt"):
            
            self.files.append(file)
            
            with open(file) as f:
                
                # Treat file header
                head_raw = [next(f) for x in range(begin_data_line)]
                head = PathLossHeader(head_raw[0].split()[1][1:-1],
                                      [float(x) for x in head_raw[1].split()[1:]],
                                      float(head_raw[2].split()[1]),
                                      head_raw[3].split()[1:],
                                      head_raw[4].split()[1],
                                      [float(x) for x in head_raw[5].split()[1:]],
                                      [float(x) for x in head_raw[6].split()[1:]],
                                      float(head_raw[7].split()[1]),
                                      float(head_raw[8].split()[1]),
                                      float(head_raw[9].split()[1]))
                
                # Initialize path loss array
                # Remember that data in file is in LAT LONG format, so y value
                # is given befor the x value
                n_col = int((head.upper_right[1] - 
                         head.lower_left[1])/head.resolution)
                n_lin = int((head.upper_right[0] - 
                         head.lower_left[0])/head.resolution)
                loss = -np.inf*np.ones((n_lin,n_col))
                
                # Loop through all the remaining lines
                line = next(f)
                while "END_DATA" not in line:
                    data = [float(x) for x in line.split()]
                    
                    # Define line and column of array
                    lin = int((data[0] - (head.lower_left[0] + 
                           head.resolution/2))/head.resolution)
                    col = int((data[1] - (head.lower_left[1] + 
                           head.resolution/2))/head.resolution)
                    loss[lin,col] = data[2]
                    
                    line = next(f)
                    
                # Add values to dict
                self.path_loss[head.antenna] = (head,loss)
        
    def get_loss(self, *args, **kwargs) -> np.array:
        """
        Keyword Arguments:
            cell_id (np.array): array of strings with IDs of cells to which
                calculate the path loss
            ue_position_x (np.array): array of x coordinate of UEs to 
                which calculate path loss
            ue_position_y (np.array):array of y coordinate of UEs to 
                which calculate path loss
        """
        # Get keywork arguments
        cell_id = kwargs["cell_id"]
        ue_position_x = kwargs["ue_position_x"]
        ue_position_y = kwargs["ue_position_y"]
        
        # Initialize array
        loss = np.zeros((len(cell_id),len(ue_position_x)))
        
        # Loop through all the cells
        for k in range(len(cell_id)):
            # Convert positions to array indexes
            cell = cell_id[k]
            lowleft_y = self.path_loss[cell][0].lower_left[0]
            lowleft_x = self.path_loss[cell][0].lower_left[1]
            res = self.path_loss[cell_id[0]][0].resolution
            lin_f = (ue_position_y - lowleft_y)/res
            col_f = (ue_position_x - lowleft_x)/res
            lin = lin_f.astype(int)
            col = col_f.astype(int)
            
            # Fill array
            loss[k:] = self.path_loss[cell][1][lin,col]
            
        return loss
    
if __name__ == '__main__':
    
    prop = PropagationInputFile("measurements")
    
    plt.imshow(prop.path_loss["BRCU0010"][1], cmap='hot', 
               interpolation='nearest',
               extent = [prop.path_loss["BRCU0010"][0].lower_left[1],
                         prop.path_loss["BRCU0010"][0].upper_right[1],
                         prop.path_loss["BRCU0010"][0].lower_left[0],
                         prop.path_loss["BRCU0010"][0].upper_right[0]])
    plt.colorbar()
    plt.show()
    
    plt.imshow(prop.path_loss["BRUC0020"][1], cmap='hot', 
               interpolation='nearest',
               extent = [prop.path_loss["BRUC0020"][0].lower_left[1],
                         prop.path_loss["BRUC0020"][0].upper_right[1],
                         prop.path_loss["BRUC0020"][0].lower_left[0],
                         prop.path_loss["BRUC0020"][0].upper_right[0]])
    plt.colorbar()
    plt.show()