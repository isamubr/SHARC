# -*- coding: utf-8 -*-
"""
Created on Tue Jan 30 16:00:22 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import numpy as np
import matplotlib.axes
import matplotlib.pyplot as plt
from itertools import product
import matplotlib.patches as patches
from shapely.geometry import Point
import random


from sharc.topology.topology import Topology
from sharc.parameters.parameters_imt_vale import ParametersImtVale
from sharc.map.topography import Topography


class TopologyInputMap(Topology):
    """
    Generates the coordinates of the BSs based on the base station physical cell data input file.
    """
    def __init__(self, param: ParametersImtVale, topography: Topography):
        self.param = param
        self.topography = topography

        # List of all pixel central x and y values
        self.x_vals = np.arange(self.topography.low_left[0] +
                                self.topography.resolution / 2,
                                self.topography.up_right[0],
                                self.topography.resolution)
        self.y_vals = np.arange(self.topography.low_left[1] +
                                self.topography.resolution / 2,
                                self.topography.up_right[1],
                                self.topography.resolution)

        # List of polygon-points tuples
        self.poly_points = []
        self.polys = []

        # Initialize attributes
        self.x_ue = np.empty(0)
        self.y_ue = np.empty(0)
        self.z_ue = np.empty(0)
        self.z = np.empty(0)

        # FIXME: cells are not supposed to be deffined for this topology
        intersite_distance = 500
        cell_radius = 100
        super().__init__(intersite_distance, cell_radius)

    def calculate_coordinates(self, random_number_gen=np.random.RandomState()):
        """
        Read the base station coordinates from Base Station data parsed from file.
        :param random_number_gen is ignored but is added to function signature for compatibility
        """
        self.x = self.param.x_bs
        self.y = self.param.y_bs
        self.z = self.topography.get_z(self.x, self.y)
        self.num_base_stations = len(self.x)
        self.azimuth = self.param.azimuth

        # Taking the Mechanical Down-tilt
        self.elevation = self.param.elevation

        # No indoor stations
        self.indoor = np.zeros(self.num_base_stations, dtype=bool)

    def map_polygons(self, polys: list):
        """
        Maps polygons as mask on grid

        Parameters
        ----------
            polys (list): list of shapely.geometry.Polygon objects
        """
        self.polys = polys
        # TODO: try and vectorize this loop
        for poly in self.polys:
            # List of points inside polygon
            x = []
            y = []
            num_pts = 0
            # Loop through all x and y combinations
            for coord in product(self.x_vals, self.y_vals):
                pt = Point(coord)
                # Append pixel center point if inside polygon
                if poly.contains(pt):
                    x.append(coord[0])
                    y.append(coord[1])
                    num_pts += 1
            self.poly_points.append((poly, np.array(x), np.array(y), num_pts))

    def distribute_ues(self, num_ues: list, random_number_gen: np.random.RandomState):
        """
        Uniformly distributes UEs onto polygons

        Parameters
        ----------
            num_ues (list): number of UEs in each polygon. Indexing must
                match the polygon indexing given in map_polygons method
        """
        x = np.array([])
        y = np.array([])

        for k, num in enumerate(num_ues):
            idxs = random_number_gen.randint(0, self.poly_points[k][3], num)
            x = np.append(x, self.poly_points[k][1][idxs])
            y = np.append(y, self.poly_points[k][2][idxs])

        self.x_ue = x
        self.y_ue = y
        self.z_ue = self.topography.get_z(self.x_ue, self.y_ue)

    def plot(self, ax: matplotlib.axes.Axes):
        # plot base station locations
        plt.scatter(self.x, self.y, color='g', edgecolor="w", linewidth=0.5, label="Map_base_station")

        # plot base stations coverage area
        for x, y, a, pattern in zip(self.x, self.y, self.azimuth, self.param.bs_antenna_pattern):
            if pattern == 'omni_10dBi':
                pa = patches.CirclePolygon((x, y), 100, 20, fill=False, edgecolor="green", linestyle='solid')
                ax.add_patch(pa)
            else:
                angle = np.deg2rad(a)
                ax.arrow(x, y, self.cell_radius*np.cos(angle), self.cell_radius*np.sin(angle),
                         fc="k", ec="k", head_width=10.0, head_length=15.0)

        # plot UE locations inside delimitation polygons
        for poly in self.polys:
            x_poly, y_poly = poly.exterior.xy
            ax.plot(x_poly, y_poly)

        ax.plot(self.x_ue, self.y_ue, '.r', label="UEs")
        ax.grid()


if __name__ == '__main__':
    seed = 101
    random.seed(seed)
    secondary_seed = random.randint(1, 2**32 - 1)
    random_number_gen = np.random.RandomState(seed=secondary_seed)
    parameters_imt = ParametersImtVale(imt_link='DOWNLINK')
    parameters_imt.bs_physical_data_file = '../parameters/bs_data/brucutu-2Macros-1Small-omni.xls'
    parameters_imt.bs_data = parameters_imt.read_input_cell_data_file(parameters_imt.bs_physical_data_file)
    parameters_imt.ue_polygon_file = '../parameters/polygons/ContornoBrucutu.kml'
    parameters_imt.ue_polygons = ParametersImtVale.read_input_ue_polygon_kml_file(parameters_imt.ue_polygon_file, '23K')
    parameters_imt.topography_data_file = '../parameters/maps/Brucutu_res_20m.asc'
    topography = Topography()
    topography.parse_raster_data(parameters_imt.topography_data_file)

    topology = TopologyInputMap(parameters_imt, topography)
    topology.calculate_coordinates()
    topology.map_polygons(parameters_imt.ue_polygons)
    num_ues = [3]
    topology.distribute_ues(num_ues, random_number_gen)

    fig = plt.figure(figsize=(8, 8), facecolor='w', edgecolor='k')  # create a figure object
    ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure

    topology.plot(ax)

    plt.axis('image')
    plt.title("Input map topology")
    plt.xlabel("x-coordinate [m]")
    plt.ylabel("y-coordinate [m]")
    plt.legend(loc="upper left", scatterpoints=1)
    plt.tight_layout()

    axes = plt.gca()

    plt.show()
