#-*- coding: utf-8 -*-
"""
Created on Apr 05 14:40 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import pandas as pd
import geopandas as gpd
import numpy as np
import sys
import os
from glob import glob
from sharc.parameters.parameter_handler import ParameterHandler


class ParametersImtVale(ParameterHandler):
    """
    Loads IMT parameters for IMT_VALE simulation
    """

    def __init__(self, imt_link: str):
        super().__init__('IMT')
        self.imt_link = imt_link

    def read_input_cell_data_file(self, cell_data_file_name: str):
        """
        Read cell data excel file with base station parameters and load IMT parameters accordingly
        :param cell_data_file_name: file name
        :param imt_dir: IMT Direction DOWNLINK or UPLINK
        :return: None
        """

        # This is the minimal set of parameters that the file must contain. This is used for a minimal sanity check
        param_min_set = {
            "strSiteID",
            "strCellID",
            "dWECoordinateMeter",
            "dSNCoordinateMeter",
            "dBearing",
            "dMDownTilt",
            "dEDownTilt",
            "bDeleted",
            "dMaxTxPowerdBm",
            "dDLCarrierMHz",
            "dULCarrierMHz",
            "dHeight",
            "BSCat",
            "pattern",
            "dDLBWMHz",
            "PilotPower"
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

        # Load only active cell data
        active_cell_idx = [i for i, v in enumerate(bs_data_df['bDeleted'].tolist()) if not v]
        bs_data = bs_data_df.iloc[active_cell_idx].to_dict('list')

        self.num_macrocell_sites = len(bs_data['strCellID'])
        self.site_id = bs_data['strSiteID']
        self.cell_id = bs_data['strCellID']
        self.x_bs = np.array(bs_data['dWECoordinateMeter'])
        self.y_bs = np.array(bs_data['dSNCoordinateMeter'])
        self.azimuth = np.array(bs_data['dBearing']).astype(float)
        self.elevation = np.array(bs_data['dMDownTilt']).astype(float)
        self.electrical_dt = np.array(bs_data['dEDownTilt']).astype(float)
        self.is_deleted = np.bool(bs_data['bDeleted'])
        self.bs_conducted_power = np.array(bs_data['dMaxTxPowerdBm']).astype(float)
        if self.imt_link == 'DOWNLINK':
            self.frequency = np.array(bs_data['dDLCarrierMHz']).astype(float)
        else:
            self.frequency = np.array(bs_data['dULCarrierMHz']).astype(float)
        self.bs_height = np.array(bs_data['dHeight']).astype(float)
        self.bs_category = bs_data['BSCat']
        self.bs_antenna_pattern = bs_data['pattern']
        self.bandwidth = np.array(bs_data['dDLBWMHz']).astype(float)
        self.bs_pilot_pow = np.array(bs_data['PilotPower']).astype(float)

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

    def get_path_loss_files(self, path_loss_files_folder: str):
        # Loop through all the txt files in the folder
        all_path_loss_files = glob(os.path.join(path_loss_files_folder, '*.txt'))
        path_loss_files = []
        for pl_file in all_path_loss_files:
            for cid in self.cell_id:
                if cid in pl_file:
                    path_loss_files.append(pl_file)

        if not path_loss_files:
            sys.stderr.write("\n No Path Loss input file were found in {}\n".format(path_loss_files_folder))
            sys.exit(1)
        return path_loss_files

    def read_params(self, config_file: str):
        super().read_params(config_file)

        if self.topology == 'INPUT_MAP':
            if self.bs_physical_data_file:
                self.read_input_cell_data_file(self.bs_physical_data_file)
            else:
                err_msg = "PARAMETER ERROR[{}]: Parameter 'bs_physical_data_file' must be set" \
                          "to topology type INPUT_MAP\n".format(self.__class__.__name__)
                sys.stderr.write(err_msg)
                sys.exit(1)
        else:
            err_msg = "PARAMETER ERROR[{}]: Parameter 'topology' must be set" \
                      "to INPUT_MAP for simulation type 'IMT_VALE.\n".format(self.__class__.__name__)
            sys.stderr.write(err_msg)
            sys.exit(1)

        if self.ue_polygon_file:
            self.ue_polygons = self.read_input_ue_polygon_kml_file(self.ue_polygon_file, self.utm_zone)
        else:
            err_msg = "PARAMETER ERROR[{}]: Parameter 'ue_polygons' must be set" \
                      "for simulation type 'IMT_VALE'.\n".format(self.__class__.__name__)
            sys.stderr.write(err_msg)
            sys.exit(1)

        if self.channel_model == "INPUT_FILES":
            self.path_loss_files = self.get_path_loss_files(self.propagation_folder)
        else:
            err_msg = "PARAMETER ERROR[{}]: Parameter 'channel_model' must be set" \
                      "to 'INPUT_FILES' for simulation type 'IMT_VALE'.\n".format(self.__class__.__name__)
            sys.stderr.write(err_msg)
            sys.exit(1)
