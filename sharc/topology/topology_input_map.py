# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:00:22 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import numpy as np
import matplotlib.pyplot as plt

from sharc.topology.topology import Topology
from sharc.parameters.parameters_imt import ParametersImt


class TopologyInputMap(Topology):
    """
    Generates the coordinates of the BSs based on the base station physical cell data input file.
    """

    # Possible values for antenna Azimuth and elevation
    # FIXME: Those parameters must come from input file
    AZIMUTH = [0, 90, 180, 270]
    ELEVATION = -10

    def __init__(self, param: ParametersImt):
        self.param = param

    def calculate_coordinates(self):
        """
        Read the base station coordinates from Base Station data parsed from file.
        """

        self.x = np.array(self.param.bs_data['dWECoordinateMeter'])
        self.y = np.array(self.param.bs_data['dSNCoordinateMeter'])
        self.num_base_stations = len(self.x)

        # Zero Azimuth for omni antennas
        antenna_patterns = self.params.bs_data['pattern']
        # FIXME: define antenna Azimuths for other antenna patterns
        self.azimuth = [self.AZIMUTH[0] if pattern.startswith('omni') else None for pattern in antenna_patterns]

        # FIXME: Need to parse elevation information from input file
        self.elevation = self.ELEVATION

    def plot(self):
        plt.figure()  # create a figure object

        # ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure

        plt.scatter(self.x, self.y, color='g', edgecolor="w", linewidth=0.5, label="Map_base_station")
        plt.axis('image')
        plt.title("Map base station topology")
        plt.xlabel("x-coordinate [m]")
        plt.ylabel("y-coordinate [m]")
        plt.tight_layout()
        plt.show()


if __name__ == '__main__':

    topology = TopologyInputMap()
    topology.calculate_coordinates()
    topology.plot()


