# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 14:39:17 2018

@author: Calil
"""

from sharc.propagation.propagation import Propagation

import matplotlib.pyplot as plt
import numpy as np
from glob import glob
import sys
import os


class PropagationInputFiles(Propagation):
    """
    Implements path loss from specified files

    Attributes:
        files (list): list containing names (and path to) path loss files
        path_loss (dict): keys are the antenna names, while values are tuples
            with header of respective path loss file and np.array of path loss
            values
    """

    def __init__(self, input_folder: str):
        """
        Constructs PropagationInputFile object, initializing the path_loss
        attribute.

        Parameters:
            input_folder (str): path to folder containing the path loss files
        """
        super().__init__()

        self.files = []
        self.path_loss = dict()

        # Loop through all the txt files in the folder
        path_loss_files = glob(os.path.join(input_folder, '*.txt'))
        if not path_loss_files:
            sys.stderr.write("No Path Loss input file were found in {}\n".format(input_folder))
            sys.exit(1)

        for file in path_loss_files:

            self.files.append(file)

            with open(file) as f:

                # Find where data begins and extract header
                head = dict()
                line = next(f)
                while "BEGIN_DATA" not in line:
                    split_line = line.split()
                    
                    # Load next line before skiping blank line
                    line = next(f)
                    # Skip blank line. This way the user can insert blank
                    # lines between parameters and it still works
                    if len(split_line) < 2: continue
                
                    # Create dict
                    head[split_line[0]] = split_line[1:]
                    
                # Test set of minimal parameters
                min_params = set(["ANTENNA",
                                  "LOWER_LEFT",
                                  "UPPER_RIGHT",
                                  "RESOLUTION",
                                  "RECEIVER_GAIN"])
                param_keys = set(head.keys())
                if not min_params.issubset(param_keys):
                    missing_params = min_params - param_keys
                    sys.stderr.write("Minimal parameter(s) " + 
                                     str(missing_params) + 
                                     " not in path loss file " +
                                     file + "\n")
                    sys.exit(1)
                    
                # Parse minimal parameters
                head["ANTENNA"] = head["ANTENNA"][0][1:-1]
                head["LOWER_LEFT"] = [float(x) for x in head["LOWER_LEFT"]]
                head["UPPER_RIGHT"] = [float(x) for x in head["UPPER_RIGHT"]]
                head["RESOLUTION"] = float(head["RESOLUTION"][0])
                head["RECEIVER_GAIN"] = float(head["RECEIVER_GAIN"][0])
                
                # Undefined parameter value
                undefined = np.nan
                
                # Parse other parameters
                if 'LOCATION' not in head.keys(): head["LOCATION"] = undefined
                else: head["LOCATION"] = [float(x) 
                                              for x in head["LOCATION"]]
                
                if 'FREQUENCY' not in head.keys(): 
                    head["FREQUENCY"] = undefined
                else: head["FREQUENCY"] = float(head["FREQUENCY"][0])
                
                if "POWER" not in head.keys(): 
                    head["POWER"] = undefined
                
                if 'ANTENNATYPE' not in head.keys():
                    head["ANTENNATYPE"] = undefined
                else: head["ANTENNATYPE"] = head["ANTENNATYPE"][0]
                
                if 'HEIGHT' not in head.keys(): head["HEIGHT"] = undefined
                else: head["HEIGHT"] = float(head["HEIGHT"][0])

                # Initialize path loss array
                n_lin = int((head["UPPER_RIGHT"][1] -
                             head["LOWER_LEFT"][1]) / head["RESOLUTION"])
                n_col = int((head["UPPER_RIGHT"][0] -
                             head["LOWER_LEFT"][0]) / head["RESOLUTION"])
                loss = -np.inf * np.ones((n_lin, n_col))

                # Loop through all the remaining lines
                line = next(f)
                while "END_DATA" not in line:
                    data = [float(x) for x in line.split()]

                    # Define line and column of array
                    lin = int((data[1] - (head["LOWER_LEFT"][1] +
                                          head["RESOLUTION"] / 2)) / head["RESOLUTION"])
                    col = int((data[0] - (head["LOWER_LEFT"][0] +
                                          head["RESOLUTION"] / 2)) / head["RESOLUTION"])
                    # Invert signal to match simulator convention
                    loss[lin, col] = (-1) * (data[2] + head["RECEIVER_GAIN"])

                    line = next(f)

                # Add values to dict
                self.path_loss[head["ANTENNA"]] = (head, loss)

    def get_loss(self, *args, **kwargs) -> np.array:
        """
        Returns from given BSs in the specified UE positions

        Keyword Arguments:
            bs_id (np.array): array of strings with IDs of BSs to which
                calculate the path loss
            ue_position_x (np.array): array of x coordinate of UEs to
                which calculate path loss
            ue_position_y (np.array):array of y coordinate of UEs to
                which calculate path loss

        Returns:
            loss (np.array): path loss matrix. Lines correspond to BSs while
                columns correspond to UEs
        """
        # Get keywork arguments
        bs_id = kwargs["bs_id"]
        ue_position_x = kwargs["ue_position_x"]
        ue_position_y = kwargs["ue_position_y"]

        # Initialize array
        loss = np.zeros((len(bs_id), len(ue_position_x)))

        # Loop through all the cells
        for k, bs in enumerate(bs_id):
            # Convert positions to array indexes
            lowleft_y = self.path_loss[bs][0]["LOWER_LEFT"][1]
            lowleft_x = self.path_loss[bs][0]["LOWER_LEFT"][0]
            res = self.path_loss[bs][0]["RESOLUTION"]
            lin_f = (ue_position_y - lowleft_y) / res
            col_f = (ue_position_x - lowleft_x) / res
            lin = lin_f.astype(int)
            col = col_f.astype(int)

            # Fill array
            # Invert signal to match the rest of simulator
            loss[k:] = self.path_loss[bs][1][lin, col]

        return loss


if __name__ == '__main__':
    prop = PropagationInputFiles("../parameters/measurements")

    plt.imshow(prop.path_loss["BRCU0010"][1], cmap='hot_r',
               interpolation='nearest',
               extent=[prop.path_loss["BRCU0010"][0]["LOWER_LEFT"][0],
                       prop.path_loss["BRCU0010"][0]["UPPER_RIGHT"][0],
                       prop.path_loss["BRCU0010"][0]["LOWER_LEFT"][1],
                       prop.path_loss["BRCU0010"][0]["UPPER_RIGHT"][1]])
    plt.colorbar()
    plt.show()

    plt.imshow(prop.path_loss["BRUC0020"][1], cmap='hot_r',
               interpolation='nearest',
               extent=[prop.path_loss["BRUC0020"][0]["LOWER_LEFT"][0],
                       prop.path_loss["BRUC0020"][0]["UPPER_RIGHT"][0],
                       prop.path_loss["BRUC0020"][0]["LOWER_LEFT"][1],
                       prop.path_loss["BRUC0020"][0]["UPPER_RIGHT"][1]])
    plt.colorbar()
    plt.show()
