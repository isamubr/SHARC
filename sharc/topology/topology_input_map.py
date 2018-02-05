# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:00:22 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import numpy as np
import matplotlib.axes
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd

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
        antenna_patterns = self.param.bs_data['pattern']
        # FIXME: define antenna Azimuths for other antenna patterns
        self.azimuth = [self.AZIMUTH[0] if pattern.startswith('omni') else None for pattern in antenna_patterns]

        # FIXME: Need to parse elevation information from input file
        self.elevation = self.ELEVATION

    def plot(self, ax: matplotlib.axes.Axes):
        # plot base station locations
        plt.scatter(self.x, self.y, color='g', edgecolor="w", linewidth=0.5, label="Map_base_station")
        cell_radius_m = 100

        # plot base stations coverage area
        for x, y, a in zip(self.x, self.y, self.azimuth):
            pa = patches.CirclePolygon((x, y), cell_radius_m, 20, fill=False, edgecolor="green", linestyle='solid')
            ax.add_patch(pa)


if __name__ == '__main__':

    parameters_ims = ParametersImt()
    parameters_ims.bs_physical_data_file = '../parameters/brucuCCO2600.xlsx'
    bs_data_df = pd.read_excel(parameters_ims.bs_physical_data_file)
    parameters_ims.bs_data = bs_data_df.to_dict('list')
    topology = TopologyInputMap(parameters_ims)
    topology.calculate_coordinates()

    fig = plt.figure(figsize=(8, 8), facecolor='w', edgecolor='k')  # create a figure object
    ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure

    topology.plot(ax)

    plt.axis('image')
    plt.title("Macro cell topology with hotspots")
    plt.xlabel("x-coordinate [m]")
    plt.ylabel("y-coordinate [m]")
    plt.legend(loc="upper left", scatterpoints=1)
    plt.tight_layout()

    axes = plt.gca()
    # axes.set_xlim([-1500, 1000])

    plt.show()

