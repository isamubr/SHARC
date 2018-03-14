# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 16:05:58 2017

@author: edgar
"""

import pandas as pd
import sys
import configparser
from sharc.parameters.parameter_handler import ParameterHandler
from collections import OrderedDict


class ParametersImt(ParameterHandler):

    def __init__(self):

        self.default_values = \
                          OrderedDict([('topology', 'HOTSPOT'),
                                       ('bs_physical_data_file', 'parameters/brucuCCO2600.xlsx'),
                                       ('num_macrocell_sites', 19),
                                       ('num_clusters', 1),
                                       ('intersite_distance', 1000),
                                       ('minimum_separation_distance_bs_ue', 10),
                                       ('interfered_with', 'false'),
                                       ('frequency', 27250),
                                       ('bandwidth', 200),
                                       ('rb_bandwidth', 0.180),
                                       ('guard_band_ratio', 0.1),
                                       ('bs_load_probability', .5),
                                       ('bs_conducted_power', 10),
                                       ('bs_height', 6),
                                       ('bs_aclr', 40),
                                       ('bs_acs', 30),
                                       ('bs_noise_figure', 10),
                                       ('bs_noise_temperature', 290),
                                       ('bs_ohmic_loss', 3),
                                       ('ul_attenuation_factor', 0.4),
                                       ('ul_sinr_min', -10),
                                       ('ul_sinr_max', 22),
                                       ('ue_k', 3),
                                       ('ue_k_m', 1),
                                       ('ue_indoor_percent', 0),
                                       ('ue_distribution_distance', 'RAYLEIGH'),
                                       ('ue_distribution_azimuth', 'UNIFORM'),
                                       ('ue_tx_power_control', 'ON'),
                                       ('ue_p_o_pusch', -95),
                                       ('ue_alfa', 1),
                                       ('ue_p_cmax', 22),
                                       ('ue_conducted_power', 10),
                                       ('ue_height', 1.5),
                                       ('ue_aclr', 35),
                                       ('ue_acs', 25),
                                       ('ue_noise_figure', 10),
                                       ('ue_ohmic_loss', 3),
                                       ('ue_body_loss', 4),
                                       ('dl_attenuation_factor', 0.6),
                                       ('dl_sinr_min', -10),
                                       ('dl_sinr_max', 30),
                                       ('channel_model', 'UMi'),
                                       ('propagation_folder', 'parameters/measurements'),
                                       ('line_of_sight_prob', 0.95),
                                       ('shadowing', 'true'),
                                       ('noise_temperature', 290),
                                       ('boltzmann_constant', 1.38064852e-23)])

        self.valid_options = {
            "topology": ["MACROCELL", "HOTSPOT", "SINGLE_BS", "INDOOR", "INPUT_MAP"],
            "interfered_with": ["true", "false"],
            "ue_distribution_distance": ["RAYLEIGH", "UNIFORM"],
            "ue_distribution_azimuth": ["NORMAL", "UNIFORM"],
            "ue_tx_power_control": ["ON", "OFF"],
            "channel_model": ["FSPL", "CI", "UMa", "UMi", "ABG", "INPUT_FILES"],
        }

        # Initialize class attributes to the default values
        for key in self.default_values:
            setattr(self, key, self.default_values[key])

    def read_params(self, config_file: str):

        config = configparser.ConfigParser(defaults=self.default_values)
        config.read(config_file, encoding='utf-8')

        self.topology = config.get("IMT", "topology")
        setattr(self, 'topology', config.get('IMT', 'topology'))
        self.check_param_option("IMT", "topology")

        self.channel_model = config.get("IMT", "channel_model")
        self.check_param_option("IMT", "channel_model")

        # For INPUT_MAP the input file with BS physical data must be loaded
        # the self.imt.bs_data contain a dict of BS parameters
        if self.topology == "INPUT_MAP":
            self.bs_data = {}
            if config.has_option("IMT", "bs_physical_data_file"):
                self.bs_physical_data_file = config.get("IMT", "bs_physical_data_file")
                self.bs_data = ParametersImt.read_input_cell_data_file(self.bs_physical_data_file)
            else:
                err_msg = "ERROR\nInvalid configuration: For topology type INPUT_MAP, the base station physical data " \
                          "file must be set in parameter bs_physical_data_file\n"
                sys.stderr.write(err_msg)
                sys.exit(1)

        if self.channel_model == "INPUT_FILES":
            if config.has_option("IMT", "propagation_folder"):
                self.path_loss_folder = config.get("IMT", "propagation_folder")
            else:
                err_msg = "ERROR\nInvalid configuration: For channel model " \
                          "type INPUT_FILES,  the folder containing the " \
                          "path loss measurement files must be set in " \
                          "parameter propagation_folder\n"
                sys.stderr.write(err_msg)
                sys.exit(1)

            if self.topology != "INPUT_MAP":
                err_msg = "ERROR\nInvalid configuration: For channel model " \
                          "type INPUT_FILES,  parameter " \
                          "bs_physical_data_file must be set to INPUT_MAP " \
                          "value\n"
                sys.stderr.write(err_msg)
                sys.exit(1)

        self.num_macrocell_sites = config.getint("IMT", "num_macrocell_sites")
        self.num_clusters = config.getint("IMT", "num_clusters")
        self.intersite_distance = config.getfloat("IMT", "intersite_distance")
        self.minimum_separation_distance_bs_ue = config.getfloat("IMT", "minimum_separation_distance_bs_ue")
        self.interfered_with = config.getboolean("IMT", "interfered_with")
        self.frequency = config.getfloat("IMT", "frequency")
        self.bandwidth = config.getfloat("IMT", "bandwidth")
        self.rb_bandwidth = config.getfloat("IMT", "rb_bandwidth")
        self.guard_band_ratio = config.getfloat("IMT", "guard_band_ratio")
        self.bs_load_probability = config.getfloat("IMT", "bs_load_probability")
        self.bs_conducted_power = config.getfloat("IMT", "bs_conducted_power")
        self.bs_height = config.getfloat("IMT", "bs_height")
        self.bs_aclr = config.getfloat("IMT", "bs_aclr")
        self.bs_acs = config.getfloat("IMT", "bs_acs")
        self.bs_noise_figure = config.getfloat("IMT", "bs_noise_figure")
        self.bs_noise_temperature = config.getfloat("IMT", "bs_noise_temperature")
        self.bs_ohmic_loss = config.getfloat("IMT", "bs_ohmic_loss")
        self.ul_attenuation_factor = config.getfloat("IMT", "ul_attenuation_factor")
        self.ul_sinr_min = config.getfloat("IMT", "ul_sinr_min")
        self.ul_sinr_max = config.getfloat("IMT", "ul_sinr_max")
        self.ue_k = config.getint("IMT", "ue_k")
        self.ue_k_m = config.getint("IMT", "ue_k_m")
        self.ue_indoor_percent = config.getfloat("IMT", "ue_indoor_percent")

        self.ue_distribution_distance = config.get("IMT", "ue_distribution_distance")
        self.check_param_option("IMT", "ue_distribution_distance")

        self.ue_distribution_azimuth = config.get("IMT", "ue_distribution_azimuth")
        self.check_param_option("IMT", "ue_distribution_azimuth")

        self.ue_tx_power_control = config.get("IMT", "ue_tx_power_control")
        self.check_param_option("IMT", "ue_tx_power_control")

        self.ue_p_o_pusch = config.getfloat("IMT", "ue_p_o_pusch")
        self.ue_alfa = config.getfloat("IMT", "ue_alfa")
        self.ue_p_cmax = config.getfloat("IMT", "ue_p_cmax")
        self.ue_conducted_power = config.getfloat("IMT", "ue_conducted_power")
        self.ue_height = config.getfloat("IMT", "ue_height")
        self.ue_aclr = config.getfloat("IMT", "ue_aclr")
        self.ue_acs = config.getfloat("IMT", "ue_acs")
        self.ue_noise_figure = config.getfloat("IMT", "ue_noise_figure")
        self.ue_ohmic_loss = config.getfloat("IMT", "ue_ohmic_loss")
        self.ue_body_loss = config.getfloat("IMT", "ue_body_loss")
        self.dl_attenuation_factor = config.getfloat("IMT", "dl_attenuation_factor")
        self.dl_sinr_min = config.getfloat("IMT", "dl_sinr_min")
        self.dl_sinr_max = config.getfloat("IMT", "dl_sinr_max")
        self.line_of_sight_prob = config.getfloat("IMT", "line_of_sight_prob")
        self.shadowing = config.getboolean("IMT", "shadowing")
        self.noise_temperature = config.getfloat("IMT", "noise_temperature")
        self.BOLTZMANN_CONSTANT = config.getfloat("IMT", "BOLTZMANN_CONSTANT")

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
            sys.stderr.write(str(err) + "\n")
            sys.exit(1)

        bs_data_headers = set(list(bs_data_df.columns))
        if not bs_data_headers.issuperset(param_min_set):
            sys.stderr.write('Parameter file error: Parameter(s) not recognized or the parameters file does not \n'
                             'contain the minimal set of parametes: {}'.format(param_min_set))
            sys.exit(1)
        else:
            return bs_data_df.to_dict('list')
