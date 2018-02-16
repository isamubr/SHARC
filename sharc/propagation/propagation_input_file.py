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
import sys
import os


class PropagationInputFile(Propagation):
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
                head_dict = dict()
                line = next(f)
                while "BEGIN_DATA" not in line:
                    split_line = line.split()
                    
                    # Load next line before skiping blank line
                    line = next(f)
                    # Skip blank line. This way the user can insert blank
                    # lines between parameters and it still works
                    if len(split_line) < 2: continue
                
                    # Create dict
                    head_dict[split_line[0]] = split_line[1:]
                    
                # Test set of minimal parameters
                min_params = set(["ANTENNA",
                                  "LOWER_LEFT",
                                  "UPPER_RIGHT",
                                  "RESOLUTION",
                                  "RECEIVER_GAIN"])
                param_keys = set(head_dict.keys())
                if not min_params.issubset(param_keys):
                    missing_params = min_params - param_keys
                    sys.stderr.write("Minimal parameter(s) " + 
                                     str(missing_params) + 
                                     " not in path loss file " +
                                     file + "\n")
                    sys.exit(1)
                    
                # Parse minimal parameters
                antenna = head_dict["ANTENNA"][0][1:-1]
                lower_left = [float(x) for x in head_dict["LOWER_LEFT"]]
                upper_right = [float(x) for x in head_dict["UPPER_RIGHT"]]
                resolution = float(head_dict["RESOLUTION"][0])
                receive_gain = float(head_dict["RECEIVER_GAIN"][0])
                
                # Undefined parameter value
                undefined = np.nan
                
                # Parse other parameters
                try: location = [float(x) for x in head_dict["LOCATION"]]
                except KeyError: location = undefined
                
                try: frequency = float(head_dict["FREQUENCY"][0])
                except KeyError: frequency = undefined
                
                try: power = head_dict["POWER"]
                except KeyError: power = undefined
                
                try: antenna_type = head_dict["ANTENNATYPE"][0]
                except KeyError: antenna_type = undefined
                
                try: height = float(head_dict["HEIGHT"][0])
                except KeyError: height = undefined

                # Create header struct
                head = PathLossHeader(antenna,
                                      location,
                                      frequency,
                                      power,
                                      antenna_type,
                                      lower_left,
                                      upper_right,
                                      height,
                                      resolution,
                                      receive_gain)

                # Initialize path loss array
                n_lin = int((head.upper_right[1] -
                             head.lower_left[1]) / head.resolution)
                n_col = int((head.upper_right[0] -
                             head.lower_left[0]) / head.resolution)
                loss = -np.inf * np.ones((n_lin, n_col))

                # Loop through all the remaining lines
                line = next(f)
                while "END_DATA" not in line:
                    data = [float(x) for x in line.split()]

                    # Define line and column of array
                    lin = int((data[1] - (head.lower_left[1] +
                                          head.resolution / 2)) / head.resolution)
                    col = int((data[0] - (head.lower_left[0] +
                                          head.resolution / 2)) / head.resolution)
                    # Invert signal to match simulator convention
                    loss[lin, col] = (-1) * (data[2] + head.receiver_gain)

                    line = next(f)

                # Add values to dict
                self.path_loss[head.antenna] = (head, loss)

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
        for k in range(len(bs_id)):
            # Convert positions to array indexes
            bs = bs_id[k]
            lowleft_y = self.path_loss[bs][0].lower_left[1]
            lowleft_x = self.path_loss[bs][0].lower_left[0]
            res = self.path_loss[bs][0].resolution
            lin_f = (ue_position_y - lowleft_y) / res
            col_f = (ue_position_x - lowleft_x) / res
            lin = lin_f.astype(int)
            col = col_f.astype(int)

            # Fill array
            # Invert signal to match the rest of simulator
            loss[k:] = self.path_loss[bs][1][lin, col]

        return loss


if __name__ == '__main__':
    prop = PropagationInputFile("../parameters/measurements")

    plt.imshow(prop.path_loss["BRCU0010"][1], cmap='hot',
               interpolation='nearest',
               extent=[prop.path_loss["BRCU0010"][0].lower_left[0],
                       prop.path_loss["BRCU0010"][0].upper_right[0],
                       prop.path_loss["BRCU0010"][0].lower_left[1],
                       prop.path_loss["BRCU0010"][0].upper_right[1]])
    plt.colorbar()
    plt.show()

    plt.imshow(prop.path_loss["BRUC0020"][1], cmap='hot',
               interpolation='nearest',
               extent=[prop.path_loss["BRUC0020"][0].lower_left[0],
                       prop.path_loss["BRUC0020"][0].upper_right[0],
                       prop.path_loss["BRUC0020"][0].lower_left[1],
                       prop.path_loss["BRUC0020"][0].upper_right[1]])
    plt.colorbar()
    plt.show()
