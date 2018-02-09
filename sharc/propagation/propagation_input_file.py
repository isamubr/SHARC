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
        path_loss_files = glob(input_folder + '/' + '*.txt')
        if not path_loss_files:
            sys.stderr.write("No Path Loss input file were found in {}".format(input_folder))
            sys.exit(1)

        for file in path_loss_files:

            self.files.append(file)

            with open(file) as f:

                # Find where data begins and extract header
                head_raw = ""
                line = next(f)
                while "BEGIN_DATA" not in line:
                    head_raw = head_raw + line
                    line = next(f)

                # Find tokens in file header
                head_list = head_raw.split() + 4*[np.nan]
                param_list = ["ANTENNA",
                              "LOCATION",
                              "FREQUENCY",
                              "POWER",
                              "ANTENNATYPE",
                              "LOWER_LEFT",
                              "UPPER_RIGHT",
                              "HEIGHT",
                              "RESOLUTION",
                              "RECEIVER_GAIN"]
                essential_params = ["ANTENNA",
                                    "LOWER_LEFT",
                                    "UPPER_RIGHT",
                                    "RESOLUTION",
                                    "RECEIVER_GAIN"]
                idx_list = []
                for param in param_list:
                    try:
                        idx_list.append(head_list.index(param))
                    except ValueError as err:
                        if param in essential_params:
                            sys.stderr.write(param +
                                         " parameter not in path loss file " +
                                         file + "\n")
                            sys.exit(1)
                        else:
                            idx_list.append(-4)

                # Get parameter values
                antenna = head_list[idx_list[0] + 1][1:-1]
                location = [float(x) for x in head_list[idx_list[1] + 1:
                                                        idx_list[1] + 4]]
                frequency = float(head_list[idx_list[2] + 1])
                power = head_list[idx_list[3] + 1:idx_list[3] + 4]
                antenna_type = head_list[idx_list[4] + 1]
                lower_left = [float(x) for x in head_list[idx_list[5] + 1:
                                                          idx_list[5] + 3]]
                upper_right = [float(x) for x in head_list[idx_list[6] + 1:
                                                           idx_list[6] + 3]]
                height = float(head_list[idx_list[7] + 1])
                resolution = float(head_list[idx_list[8] + 1])
                receive_gain = float(head_list[idx_list[9] + 1])

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
                         head.lower_left[1])/head.resolution)
                n_col = int((head.upper_right[0] -
                         head.lower_left[0])/head.resolution)
                loss = -np.inf*np.ones((n_lin,n_col))

                # Loop through all the remaining lines
                line = next(f)
                while "END_DATA" not in line:
                    data = [float(x) for x in line.split()]

                    # Define line and column of array
                    lin = int((data[1] - (head.lower_left[1] +
                           head.resolution/2))/head.resolution)
                    col = int((data[0] - (head.lower_left[0] +
                           head.resolution/2))/head.resolution)
                    # Invert signal to match simulator convention
                    loss[lin, col] = (-1)*(data[2] + head.receiver_gain)

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
        loss = np.zeros((len(bs_id),len(ue_position_x)))

        # Loop through all the cells
        for k in range(len(bs_id)):
            # Convert positions to array indexes
            bs = bs_id[k]
            lowleft_y = self.path_loss[bs][0].lower_left[1]
            lowleft_x = self.path_loss[bs][0].lower_left[0]
            res = self.path_loss[bs][0].resolution
            lin_f = (ue_position_y - lowleft_y)/res
            col_f = (ue_position_x - lowleft_x)/res
            lin = lin_f.astype(int)
            col = col_f.astype(int)

            # Fill array
            # Invert signal to match the rest of simulator
            loss[k:] = self.path_loss[bs][1][lin,col]

        return loss

if __name__ == '__main__':

    prop = PropagationInputFile("../parameters/measurements")

    plt.imshow(prop.path_loss["BRCU0010"][1], cmap='hot',
               interpolation='nearest',
               extent = [prop.path_loss["BRCU0010"][0].lower_left[0],
                         prop.path_loss["BRCU0010"][0].upper_right[0],
                         prop.path_loss["BRCU0010"][0].lower_left[1],
                         prop.path_loss["BRCU0010"][0].upper_right[1]])
    plt.colorbar()
    plt.show()

    plt.imshow(prop.path_loss["BRUC0020"][1], cmap='hot',
               interpolation='nearest',
               extent = [prop.path_loss["BRUC0020"][0].lower_left[0],
                         prop.path_loss["BRUC0020"][0].upper_right[0],
                         prop.path_loss["BRUC0020"][0].lower_left[1],
                         prop.path_loss["BRUC0020"][0].upper_right[1]])
    plt.colorbar()
    plt.show()
