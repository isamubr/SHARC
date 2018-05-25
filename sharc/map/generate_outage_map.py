# -*- coding: utf-8 -*-
"""
Created on May 10 15:02 2018

@author: Gustavo Cid (gustavo.cid@ektrum.com)
"""

import numpy as np
import matplotlib.pyplot as plt

from sharc.parameters.parameters_imt_vale import ParametersImtVale
from sharc.map.topography import Topography


class GridElement():
    """
    Implements each of the grid's element
    """

    def __init__(self, x, y, x_increment, y_increment):

        # attributes of a rectangular grid element
        self.x_min = x
        self.x_max = x + x_increment
        self.y_min = y
        self.y_max = y + y_increment

        # counter always initialized as zero
        self.counter = 0


if __name__ == '__main__':

    # loading the topography parameters
    parameters_imt = ParametersImtVale(imt_link='DOWNLINK')
    parameters_imt.bs_physical_data_file = '../parameters/bs_data/brucutu-2Macros-1Small-omni.xls'
    parameters_imt.bs_data = parameters_imt.read_input_cell_data_file(parameters_imt.bs_physical_data_file)
    parameters_imt.ue_polygon_file = '../parameters/polygons/ContornoBrucutu.kml'
    parameters_imt.ue_polygons = ParametersImtVale.read_input_ue_polygon_kml_file(parameters_imt.ue_polygon_file, '23K')
    parameters_imt.topography_data_file = '../parameters/maps/Brucutu_res_20m.asc'
    topography = Topography()
    topography.parse_raster_data(parameters_imt.topography_data_file)

    # creating the grid
    x_grid = np.linspace(topography.low_left[0],
                         topography.low_left[0] + topography.ncols * topography.resolution,
                         num=topography.ncols)

    y_grid = np.linspace(topography.low_left[1],
                         topography.low_left[1] + topography.nrows * topography.resolution,
                         num=topography.nrows)

    # calculating the x and y steps
    x_step = y_step = topography.resolution

    # creating the array that represents the total grid, with its grid's elements
    total_grid = [[GridElement(x_grid[i], y_grid[j], x_step, y_step) for i in range(len(x_grid))] for j in
                  reversed(range(len(y_grid)))]

    # reading the data from the txt file
    file = '../output/Outage map.txt'
    data = np.loadtxt(file, skiprows=1)
    x_data = data[:, 0]
    y_data = data[:, 1]
    count_data = data[:, 2]

    x_y_coordinates = list(zip(x_data, y_data))

    # initializing the histogram
    H = np.zeros((len(y_grid), len(x_grid)))

    # building the histogram
    for current_point in x_y_coordinates:
        # getting the index of the current coordinates
        index = x_y_coordinates.index(current_point)
        # searching to which element in the total grid the current coordinates belong to
        for i in range(len(x_grid)):
            # firstly, finding the grid element with the x position
            if total_grid[0][i].x_min < current_point[0] <= total_grid[0][i].x_max:
                for j in range(len(y_grid)):
                    # after locating the x, searching for the grid element with the y position
                    if total_grid[j][i].y_min < current_point[1] <= total_grid[j][i].y_max:
                        # count one more occurrence
                        total_grid[j][i].counter += count_data[index]
                        H[j][i] = total_grid[j][i].counter

    # plotting the histogram
    plt.figure()
    plt.imshow(H, interpolation='nearest', extent=[x_grid[0], x_grid[-1], y_grid[0], y_grid[-1]])
    plt.colorbar()
    plt.title("Outage map")
    plt.xlabel("x-coordinate [m]")
    plt.ylabel("y-coordinate [m]")
    plt.show()



