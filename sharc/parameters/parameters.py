# -*- coding: utf-8 -*-
"""
Created on Wed Aug  9 19:35:52 2017

@author: edgar
"""

import sys
from sharc.parameters.parameters_general import ParametersGeneral
from sharc.parameters.parameters_imt import ParametersImt
from sharc.parameters.parameters_imt_vale import ParametersImtVale
from sharc.parameters.parameters_hotspot import ParametersHotspot
from sharc.parameters.parameters_indoor import ParametersIndoor
from sharc.parameters.parameters_antenna_imt import ParametersAntennaImt
from sharc.parameters.parameters_fs import ParametersFs
from sharc.parameters.parameters_fss_ss import ParametersFssSs
from sharc.parameters.parameters_fss_es import ParametersFssEs
from sharc.parameters.parameters_haps import ParametersHaps
from sharc.parameters.parameters_rns import ParametersRns
from sharc.parameters.parameters_ras import ParametersRas


class Parameters(object):
    """
    Reads parameters from input file.
    """

    def __init__(self):
        self.file_name = None

        self.general = ParametersGeneral()
        self.imt = ParametersImt()
        self.antenna_imt = ParametersAntennaImt()
        self.hotspot = ParametersHotspot()
        self.indoor = ParametersIndoor()
        self.fss_ss = None
        self.fss_es = None
        self.fs = None
        self.haps = None
        self.rns = None
        self.ras = None

    def set_file_name(self, file_name: str):
        self.file_name = file_name

    def read_params(self):
        #######################################################################
        # GENERAL
        #######################################################################

        self.general.read_params(self.file_name)

        #######################################################################
        # Read the configuration files for the systems to be studied
        #######################################################################

        #######################################################################
        # IMT
        #######################################################################
        if self.general.simulation_type == 'IMT_VALE':
            self.imt = ParametersImtVale(self.general.imt_link)

        self.imt.read_params(self.general.imt_config_file)

        #######################################################################
        # IMT ANTENNA
        #######################################################################

        self.antenna_imt.read_params(self.general.imt_config_file)

        #######################################################################
        # HOTSPOT
        #######################################################################

        self.hotspot.read_params(self.general.imt_config_file)

        #######################################################################
        # INDOOR
        #######################################################################

        self.indoor.read_params(self.general.imt_config_file)

        if self.general.simulation_type == 'IMT_SHARING':

            #######################################################################
            # SYSTEM PARAMETERS
            #######################################################################

            self.general.set_system()

            if self.general.system == "FSS_SS":
                #######################################################################
                # FSS space station
                #######################################################################
                self.fss_ss = ParametersFssSs()
                self.fss_ss.read_params(self.general.system_config_file)

            elif self.general.system == "FSS_ES":
                #######################################################################
                # FSS earth station
                #######################################################################
                self.fss_es = ParametersFssEs()
                self.fss_es.read_params(self.general.system_config_file)

            elif self.general.system == "FS":
                #######################################################################
                # Fixed wireless service
                #######################################################################
                self.fs = ParametersFs()
                self.fs.read_params(self.general.system_config_file)

            elif self.general.system == "HAPS":
                #######################################################################
                # HAPS (airbone) station
                #######################################################################
                self.haps = ParametersHaps()
                self.haps.read_params(self.general.system_config_file)

            elif self.general.system == "RNS":
                #######################################################################
                # RNS
                #######################################################################
                self.rns = ParametersRns()
                self.rns.read_params(self.general.system_config_file)

            elif self.general.system_config_file == "RAS":
                #######################################################################
                # RAS
                #######################################################################
                self.ras = ParametersRas()
                self.ras.read_parames(self.general.system_config_file)

