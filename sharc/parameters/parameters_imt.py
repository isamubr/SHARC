# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 16:05:58 2017

@author: edgar
"""

import pandas as pd
import geopandas as gpd
import sys
from glob import glob
import os


class ParametersImt(object):
    def __init__(self):
        pass

    @staticmethod
    def read_input_cell_data_file(cell_data_file_name: str) -> dict:

        # This is the minimal set of parameters that the file must contain. This is used for a minimal sanity check
        param_min_set = {
            'strSiteID',
            'strCellID',
            'dWECoordinateMeter',
            'dSNCoordinateMeter',
            'dBearing',
            'dMDownTilt',
            'dEDownTilt',
            'bDeleted',
            'dMaxTxPowerdBm',
            'dDLCarrierMHz',
            'dHeight',
            'NodeType',
            'pattern',
            'dDLBWMHz',
            'PilotPower'
        }

        try:
            bs_data_df = pd.read_excel(cell_data_file_name)
        except FileNotFoundError as err:
            sys.stderr.write("\n" + str(err) + "\n")
            sys.exit(1)

        bs_data_headers = set(list(bs_data_df.columns))
        if not bs_data_headers.issuperset(param_min_set):
            sys.stderr.write('Parameter file error: Parameter(s) not recognized or the parameters file does not \n'
                             'contain the minimal set of parametes: {}'.format(param_min_set))
            sys.exit(1)
        else:
            return bs_data_df.to_dict('list')

    @staticmethod
    def read_input_ue_polygon_kml_file(ue_polygon_file: str, utm_zone: str) -> list:
        """
        Parse KML data from file and return a list of Shapely Polygons
        Note that the Simulator deals with UTM projection, so the it expects that the KML file is in WSG84 lat/lon
        and returns the polygon with UTM coordinates.
        :param ue_polygon_file: KML file path containing the polygons
        :param utm_zone: The UTM zone where the KML polygons reside
        :return: list of Polygons inside KML file
        """
        # enable the KML-driver, which is not enabled by default
        gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'
        gdf = gpd.read_file(ue_polygon_file, driver='KML')

        # Re-projecting from WSG84 to UTM.
        proj_str = '+proj=utm +zone={}, +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs'.format(utm_zone.upper())
        gdf = gdf.to_crs(proj_str)

        shape_list = list()
        for idx, geom in gdf['geometry'].iteritems():
            if geom.is_valid:
                shape_list.append(geom)
            else:
                # try to fix this polygon. Hope it works.
                geom_fix = geom.buffer(0)
                shape_list.append(geom_fix)

        return shape_list

    @staticmethod
    def get_path_loss_files(path_loss_files_folder: str):
        # Loop through all the txt files in the folder
        path_loss_files = glob(os.path.join(path_loss_files_folder, '*.txt'))
        if not path_loss_files:
            sys.stderr.write("\n No Path Loss input file were found in {}\n".format(path_loss_files_folder))
            sys.exit(1)
        return path_loss_files

