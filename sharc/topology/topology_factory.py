# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 16:41:25 2017

@author: edgar
"""
import sys

from sharc.topology.topology import Topology
from sharc.topology.topology_macrocell import TopologyMacrocell
from sharc.topology.topology_hotspot import TopologyHotspot
from sharc.topology.topology_indoor import TopologyIndoor
from sharc.topology.topology_single_base_station import TopologySingleBaseStation
from sharc.topology.topology_input_map import TopologyInputMap
from sharc.parameters.parameters import Parameters
# TODO: replace this with Topography class
from sharc.support.named_tuples import Topography

class TopologyFactory(object):

    @staticmethod
    def createTopology(parameters: Parameters) -> Topology:
        if parameters.imt.topology == "SINGLE_BS":
            return TopologySingleBaseStation(parameters.imt.intersite_distance*2/3, parameters.imt.num_clusters)
        elif parameters.imt.topology == "MACROCELL":
            return TopologyMacrocell(parameters.imt.intersite_distance, parameters.imt.num_clusters)
        elif parameters.imt.topology == "HOTSPOT":
            return TopologyHotspot(parameters.hotspot, parameters.imt.intersite_distance, parameters.imt.num_clusters)
        elif parameters.imt.topology == "INDOOR":
            return TopologyIndoor(parameters.indoor)
        elif parameters.imt.topology == "INPUT_MAP":
            # TODO: this Topography is just a dummy. Replace it with real Topography class.
            topography = Topography([664740.0,7799900.0],
                                   [672760.0,7805400.0],
                                   20.0)
            return TopologyInputMap(parameters.imt,topography)
        else:
            sys.stderr.write("ERROR\nInvalid topology: " + parameters.imt.topology)
            sys.exit(1)
