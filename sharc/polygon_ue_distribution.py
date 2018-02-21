# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 16:19:59 2018

@author: Calil
"""

import numpy as np
from itertools import product
from shapely.geometry import Point

class PolygonUeDistribution(object):
    
    def __init__(self,low_left: list, up_right: list, resolution: float):
        # Set attributes
        self.low_left = low_left
        self.up_right = up_right
        self.resolution = resolution
        
        # Set of all pixel central x and y values 
        self.x_vals = np.arange(low_left[0] + resolution/2,
                                up_right[0],
                                resolution)
        self.y_vals = np.arange(low_left[1] + resolution/2,
                                up_right[1],
                                resolution)
        
    def distribute_ues(self, polys: list, num_ues: int):
        
        points = []
        
        for poly in polys:
            for coord in product(self.x_vals,self.y_vals):
                pt = Point(coord)
                if poly.contains(pt):
                    points.append(pt)
    
    def plot(self,polys: list, x: np.array, y: np.array):
        pass
    
if __name__ == '__main__':
    
    poly_dist = PolygonUeDistribution()
#    polys = 
#    mun_ues = 
#    
#    x, y = poly_dist.distribute_ues(polys,num_ues)
#    poly_dist.plot(polys,x,y)