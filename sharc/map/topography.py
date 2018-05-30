# -*- coding: utf-8 -*-
"""
Created on Feb 26 15:02 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import os

class Topography:
    """
    Read an ESRI Grid in ASCII format file with topography data information
    """

    def __init__(self):
        self.low_left = [0, 0]
        self.up_right = [0, 0]
        self.resolution = 0.0
        self.nrows = 0
        self.ncols = 0
        self.topography_grid = np.array([])
        pass

    def parse_raster_data(self, file_name: str):
        """
        Parse the topography data in the ESRI ASCII file format
        :param file_name:
        """

        ESRI_ASCII_HEADER = {'ncols', 'nrows', 'xllcorner', 'yllcorner', 'cellsize', 'nodata_value'}

        with open(file_name) as f:

            header = dict()
            grid_data = list()
            line = next(f)
            while not (set(header.keys()) == ESRI_ASCII_HEADER):
                split_line = line.split()
                line = next(f)

                # Skip blank line. This way the user can insert blank
                # lines between parameters and it still works
                if len(split_line) < 2:
                    continue

                param = split_line[0].lower()
                if param not in ESRI_ASCII_HEADER:
                    sys.stderr.write('{} is not a valid keyword in ESRI ASCII file format!'.format(split_line[0]))
                    sys.exit(-1)

                header[param] = split_line[1]

            while line:
                line_data = [int(data) for data in line.split()]
                grid_data.append(line_data)
                # Check if we reached the end of the line
                try:
                    line = next(f)
                except StopIteration:
                    break

            self.nrows = int(header['nrows'])
            self.ncols = int(header['ncols'])
            self.resolution = float(header['cellsize'])
            xllcorner = float(header['xllcorner'])
            yllcorner = float(header['yllcorner'])
            self.low_left = [xllcorner, yllcorner]
            self.up_right = [xllcorner + (1 + self.ncols) * self.resolution,
                             yllcorner + (1 + self.nrows) * self.resolution]
            self.topography_grid = np.array(grid_data)

    def get_z(self, x:np.array, y: np.array):

        lin_f = (y - self.low_left[1]) / self.resolution
        col_f = (x - self.low_left[0]) / self.resolution
        lin = self.nrows - lin_f.astype(int) - 1
        col = col_f.astype(int)

        return self.topography_grid[lin,col]


if __name__ == '__main__':
    file = os.path.join('..', 'parameters', 'maps', 'Brucutu_res_20m.asc')
    topo_data = Topography()
    topo_data.parse_raster_data(file)
    print(topo_data)

    print(topo_data.topography_grid)

    custom_map = plt.cm.get_cmap('Blues', 7)
    cmaplist = [custom_map(i) for i in range(custom_map.N)]
    # reverse the colors
    cmaplist = cmaplist[::-1]
    custom_map = custom_map.from_list('custom_map', cmaplist, custom_map.N)

    topo_grid = np.ma.array(topo_data.topography_grid)

    # The invalid value is -9999 but this specific data set has invalid values that are below 300
    masked_grid = np.ma.masked_where(topo_grid <= 400, topo_grid)

    plt.imshow(masked_grid, cmap=custom_map, extent=[topo_data.low_left[0],
                                                  topo_data.low_left[0] + topo_data.ncols*topo_data.resolution,
                                                  topo_data.low_left[1],
                                                  topo_data.low_left[1] + topo_data.nrows*topo_data.resolution])
    plt.colorbar()
    plt.show()





