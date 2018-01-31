# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:00:22 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

from sharc.topology.topology import Topology
import pandas as pd
import numpy as np
import matplotlib.axes
import matplotlib.pyplot as plt


class TopologyMap(Topology):
    """
    Generates the coordinates of the BSs based on the base station physical cell data input file.
    """

    def __init__(self):
        # TODO: This must came from parameters parsing
        self.cell_phy_data_file = 'brucuCCO2600.xlsx'

    def read_cell_data_file(self):

        return pd.read_excel(self.cell_phy_data_file)

    def calculate_coordinates(self):
        """
        Read the base station coordinates in from the file.
        """

        cell_data_df = self.read_cell_data_file()

        self.x = np.array(cell_data_df['dWECoordinateMeter'].tolist())
        self.y = np.array(cell_data_df['dSNCoordinateMeter'].tolist())
        self.num_base_stations = len(self.x)
        # Zero Azimuth for omni antennas
        # TODO: How to define antenna Azimuths for other antenna patterns
        antenna_patterns = cell_data_df['pattern'].tolist()
        self.azimuth = [0 if pattern.startswith('omni') else None for pattern in antenna_patterns]
        self.azimuth = np.zeros(self.num_base_stations)
        self.elevation = np.array(cell_data_df['dHeight'].tolist())
        # TODO: Guessing that this scenario should be static?
        self.static_base_stations = True

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

    topology = TopologyMap()
    topology.calculate_coordinates()
    topology.plot()


