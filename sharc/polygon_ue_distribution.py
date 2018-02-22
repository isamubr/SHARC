# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 16:19:59 2018

@author: Calil
"""

import numpy as np
from itertools import product
from shapely.geometry import Point, Polygon
import matplotlib.pyplot as plt

class PolygonUeDistribution(object):
    """
    Implements UE distribution inside given polygons.
    
    Attributes
    ----------
        low_left (list): lower left corner of grid
        up_right (list): upper right corner of grid
        resolution (float): grid resolution
        x_vals (np.array): possible x values on grid
        y_vals (np.array): possible y values on grid
    
    Construction
    ------------
        p = PolygonUeDistribution(low_left,up_right,resolution)
    """
    
    def __init__(self,low_left: list, up_right: list, resolution: float):
        # Set attributes
        self.low_left = low_left
        self.up_right = up_right
        self.resolution = resolution
        
        # List of all pixel central x and y values 
        self.x_vals = np.arange(low_left[0] + resolution/2,
                                up_right[0],
                                resolution)
        self.y_vals = np.arange(low_left[1] + resolution/2,
                                up_right[1],
                                resolution)
        
        # List of polygon-points tuples
        self.poly_points = []
        
    def map_polygons(self, polys: list):
        """
        Maps polygons as mask on grid
        
        Parameters
        ----------
            polys (list): list of shapely.geometry.Polygon objects
        """
        # TODO: try and vectorize this loop
        for poly in polys:
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
            
        return x,y
    
    def plot(self,polys: list, x_ue: np.array, y_ue: np.array):
        # Create axis object
        fig = plt.figure(1, figsize=(5,5), dpi=90)
        ax = fig.add_subplot(111)        
        
        for poly in polys:
            x_poly, y_poly = poly.exterior.xy
            ax.plot(x_poly,y_poly)
        
        ax.plot(x_ue,y_ue,'.r')
        ax.grid()
        return ax
    
if __name__ == '__main__':
    # Set object
    low_left = [0.0, 0.0]
    up_right = [600.0, 600.0]
    res = 5
    poly_dist = PolygonUeDistribution(low_left,up_right,res)
          
    # Map polygons into grid
    poly_1 = Polygon([(0,0),(100,100),(100,0)])
    poly_2 = Polygon([(350,350),(350,550),(550,550),(550,350)])
    poly_3 = Polygon([(110,0),(110,200),(500,200),(380,50),(300,350)])
    poly_4 = Polygon([(100,500),(450,500),(450,400),(100,400)])
    poly_list = [poly_1,poly_2,poly_3,poly_4]
    poly_dist.map_polygons(poly_list)
    
    # Distribute UEs
    num_ues = [15,100,150,200]
    x, y = poly_dist.distribute_ues(num_ues)
    
    # Plot it all
    ax = poly_dist.plot(poly_list,x,y)
    plt.show(ax)
