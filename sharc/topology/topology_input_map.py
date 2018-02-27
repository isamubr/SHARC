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
from itertools import product
from shapely.geometry import Point, Polygon

from sharc.topology.topology import Topology
from sharc.parameters.parameters_imt import ParametersImt
from sharc.map.topography import Topography


class TopologyInputMap(Topology):
    """
    Generates the coordinates of the BSs based on the base station physical cell data input file.
    """
    # TODO: topography type hint
    def __init__(self, param: ParametersImt, topography: Topography):
        self.param = param
        self.topography = topography
        
        # List of all pixel central x and y values 
        self.x_vals = np.arange(self.topography.low_left[0] + 
                                self.topography.resolution/2,
                                self.topography.up_right[0],
                                self.topography.resolution)
        self.y_vals = np.arange(self.topography.low_left[1] + 
                                self.topography.resolution/2,
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

    def calculate_coordinates(self):
        """
        Read the base station coordinates from Base Station data parsed from file.
        """
        self.x = np.array(self.param.bs_data['dWECoordinateMeter'])
        self.y = np.array(self.param.bs_data['dSNCoordinateMeter'])
        self.z = self.topography.get_z(self.x,self.y)
        self.num_base_stations = len(self.x)
        self.azimuth = np.array(self.param.bs_data['dBearing'])

        # Taking the Mechanical Down-tilt
        self.elevation = np.array(self.param.bs_data['dMDownTilt'])

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
            for coord in product(self.x_vals,self.y_vals):
                pt = Point(coord)
                # Append pixel center point if inside polygon
                if poly.contains(pt):
                    x.append(coord[0])
                    y.append(coord[1])
                    num_pts+=1
            self.poly_points.append((poly,np.array(x),np.array(y),num_pts))
            
    def distribute_ues(self, num_ues: list):
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
            idxs = np.random.randint(0,self.poly_points[k][3],num)
            x = np.append(x,self.poly_points[k][1][idxs])
            y = np.append(y,self.poly_points[k][2][idxs])
            
        self.x_ue = x
        self.y_ue = y
        self.z_ue = self.topography.get_z(self.x_ue,self.y_ue)

    def plot_bs(self, ax: matplotlib.axes.Axes):
        # plot base station locations
        plt.scatter(self.x, self.y, color='g', edgecolor="w", linewidth=0.5, label="Map_base_station")

        # plot base stations coverage area
        for x, y, a in zip(self.x, self.y, self.azimuth):
            pa = patches.CirclePolygon((x, y), self.cell_radius, 20, fill=False, edgecolor="green", linestyle='solid')
            ax.add_patch(pa)
            
    def plot_ue(self, ax: matplotlib.axes.Axes):      
        for poly in self.polys:
            x_poly, y_poly = poly.exterior.xy
            ax.plot(x_poly,y_poly)
        
        ax.plot(self.x_ue,self.y_ue,'.r',label = "UEs")
        ax.grid()


if __name__ == '__main__':

    parameters_ims = ParametersImt()
    # TODO: Add a method to ParamatersImt that reads the input cell data file
    parameters_ims.bs_physical_data_file = '../parameters/brucuCCO2600.xlsx'
    bs_data_df = pd.read_excel(parameters_ims.bs_physical_data_file)
    parameters_ims.bs_data = bs_data_df.to_dict('list')
    topograph = Topography([664740.0,7799900.0],
                           [672760.0,7805400.0],
                           20.0)
    topology = TopologyInputMap(parameters_ims,topograph)
    topology.calculate_coordinates()
    
    # Map polygons into grid
    poly_1 = Polygon([(669000.0,7803000.0),
                      (669200.0,7803000.0),
                      (669000.0,7803200.0)])
    poly_2 = Polygon([(670000.0,7803200.0),
                      (670500.0,7803200.0),
                      (670500.0,7802900.0),
                      (670000.0,7802900.0)])
    poly_3 = Polygon([(670200.0,7803250.0),
                      (670700.0,7803250.0),
                      (670200.0,7802850.0),
                      (670700.0,7802850.0)])
    poly_list = [poly_1,poly_2,poly_3]
    topology.map_polygons(poly_list)
    
    # Distribute UEs
    num_ues = [15,60,40]
    topology.distribute_ues(num_ues)

    fig = plt.figure(figsize=(8, 8), facecolor='w', edgecolor='k')  # create a figure object
    ax = fig.add_subplot(1, 1, 1)  # create an axes object in the figure

    topology.plot_bs(ax)
    topology.plot_ue(ax)

    plt.axis('image')
    plt.title("Macro cell topology with hotspots")
    plt.xlabel("x-coordinate [m]")
    plt.ylabel("y-coordinate [m]")
    plt.legend(loc="upper left", scatterpoints=1)
    plt.tight_layout()

    axes = plt.gca()
    # axes.set_xlim([-1500, 1000])

    plt.show()

