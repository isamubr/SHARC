# -*- coding: utf-8 -*-
"""
Created on May 10 15:02 2018

@author: Gustavo Cid (gustavo.cid@ektrum.com)
"""

import numpy as np
import matplotlib.pyplot as plt

from sharc.parameters.parameters_imt_vale import ParametersImtVale
from sharc.map.topography import Topography

if __name__ == '__main__':

    file = '../output/Outage map.txt'

    # collect data
    data = np.loadtxt(file, skiprows=1)
    x = data[:, 0]
    y = data[:, 1]
    counts = data[:, 2]

    # loading the topography parameters
    parameters_imt = ParametersImtVale(imt_link='DOWNLINK')
    parameters_imt.bs_physical_data_file = '../parameters/bs_data/brucutu-2Macros-1Small.xls'
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

    # generating the 2D histogram from the data and the grid
    hist, y_edge, x_edge = np.histogram2d(y, x, bins=[y_grid, x_grid], normed=False, weights=counts)

    # plotting the outage map
    plt.figure(1)
    # plt.imshow(hist, cmap='hot_r', interpolation='nearest', extent=[x_edge[0], x_edge[-1], y_edge[0], y_edge[-1]])
    plt.pcolormesh(x_grid, y_grid, hist)
    plt.colorbar()
    plt.title("Outage map")
    plt.xlabel("x-coordinate [m]")
    plt.ylabel("y-coordinate [m]")
    plt.show()

