# -*- coding: utf-8 -*-
"""
Created on Sat Apr 15 16:29:36 2017

@author: Calil
"""
import configparser
import sys
from collections import OrderedDict
from sharc.support.named_tuples import AntennaPar
from sharc.parameters.parameter_handler import ParameterHandler


class ParametersAntennaImt(ParameterHandler):
    """
    Defines parameters for antenna array.
    """

    def __init__(self):
        super().__init__()

        self.default_values = \
            OrderedDict([('ue_rx_element_max_g', 5.0),
                         ('bs_tx_n_rows', 8.0),
                         ('ue_rx_n_rows', 4.0),
                         ('bs_rx_element_theta_3db', 65.0),
                         ('ue_tx_element_sla_v', 25.0),
                         ('ue_tx_element_theta_3db', 90.0),
                         ('ue_tx_element_horiz_spacing', 0.5),
                         ('bs_rx_element_am', 30.0),
                         ('bs_rx_element_max_g', 5.0),
                         ('bs_tx_element_vert_spacing', 0.5),
                         ('bs_tx_n_columns', 8.0),
                         ('ue_tx_element_max_g', 5.0),
                         ('bs_rx_element_vert_spacing', 0.5),
                         ('ue_tx_element_am', 25.0),
                         ('bs_rx_element_phi_3db', 65.0),
                         ('ue_rx_element_phi_3db', 90.0),
                         ('bs_tx_element_max_g', 5.0),
                         ('bs_tx_element_horiz_spacing', 0.5),
                         ('ue_rx_element_sla_v', 25.0),
                         ('bs_tx_element_theta_3db', 65.0),
                         ('bs_tx_element_phi_3db', 65.0),
                         ('bs_rx_n_columns', 8.0),
                         ('ue_rx_element_am', 25.0),
                         ('ue_tx_element_vert_spacing', 0.5),
                         ('bs_rx_element_sla_v', 30.0),
                         ('ue_rx_element_horiz_spacing', 0.5),
                         ('bs_rx_n_rows', 8.0),
                         ('ue_tx_element_phi_3db', 90.0),
                         ('ue_rx_n_columns', 4.0),
                         ('ue_tx_n_rows', 4.0),
                         ('ue_rx_element_vert_spacing', 0.5),
                         ('bs_rx_element_horiz_spacing', 0.5),
                         ('ue_rx_element_theta_3db', 90.0),
                         ('bs_tx_element_sla_v', 30.0),
                         ('bs_tx_element_am', 30.0),
                         ('ue_tx_n_columns', 4.0)])

        for key in self.default_values:
            setattr(self, key, self.default_values[key])

    def read_params(self, config_file: str):

        config = configparser.ConfigParser(defaults=self.default_values)
        config.read(config_file, encoding='utf-8')

        self.bs_tx_element_max_g = config.getfloat("IMT_ANTENNA", "bs_tx_element_max_g")
        self.bs_tx_element_phi_3db = config.getfloat("IMT_ANTENNA", "bs_tx_element_phi_3db")
        self.bs_tx_element_theta_3db = config.getfloat("IMT_ANTENNA", "bs_tx_element_theta_3db")
        self.bs_tx_element_am = config.getfloat("IMT_ANTENNA", "bs_tx_element_am")
        self.bs_tx_element_sla_v = config.getfloat("IMT_ANTENNA", "bs_tx_element_sla_v")
        self.bs_tx_n_rows = config.getfloat("IMT_ANTENNA", "bs_tx_n_rows")
        self.bs_tx_n_columns = config.getfloat("IMT_ANTENNA", "bs_tx_n_columns")
        self.bs_tx_element_horiz_spacing = config.getfloat("IMT_ANTENNA", "bs_tx_element_horiz_spacing")
        self.bs_tx_element_vert_spacing = config.getfloat("IMT_ANTENNA", "bs_tx_element_vert_spacing")

        self.bs_rx_element_max_g = config.getfloat("IMT_ANTENNA", "bs_rx_element_max_g")
        self.bs_rx_element_phi_3db = config.getfloat("IMT_ANTENNA", "bs_rx_element_phi_3db")
        self.bs_rx_element_theta_3db = config.getfloat("IMT_ANTENNA", "bs_rx_element_theta_3db")
        self.bs_rx_element_am = config.getfloat("IMT_ANTENNA", "bs_rx_element_am")
        self.bs_rx_element_sla_v = config.getfloat("IMT_ANTENNA", "bs_rx_element_sla_v")
        self.bs_rx_n_rows = config.getfloat("IMT_ANTENNA", "bs_rx_n_rows")
        self.bs_rx_n_columns = config.getfloat("IMT_ANTENNA", "bs_rx_n_columns")
        self.bs_rx_element_horiz_spacing = config.getfloat("IMT_ANTENNA", "bs_rx_element_horiz_spacing")
        self.bs_rx_element_vert_spacing = config.getfloat("IMT_ANTENNA", "bs_rx_element_vert_spacing")

        self.ue_tx_element_max_g = config.getfloat("IMT_ANTENNA", "ue_tx_element_max_g")
        self.ue_tx_element_phi_3db = config.getfloat("IMT_ANTENNA", "ue_tx_element_phi_3db")
        self.ue_tx_element_theta_3db = config.getfloat("IMT_ANTENNA", "ue_tx_element_theta_3db")
        self.ue_tx_element_am = config.getfloat("IMT_ANTENNA", "ue_tx_element_am")
        self.ue_tx_element_sla_v = config.getfloat("IMT_ANTENNA", "ue_tx_element_sla_v")
        self.ue_tx_n_rows = config.getfloat("IMT_ANTENNA", "ue_tx_n_rows")
        self.ue_tx_n_columns = config.getfloat("IMT_ANTENNA", "ue_tx_n_columns")
        self.ue_tx_element_horiz_spacing = config.getfloat("IMT_ANTENNA", "ue_tx_element_horiz_spacing")
        self.ue_tx_element_vert_spacing = config.getfloat("IMT_ANTENNA", "ue_tx_element_vert_spacing")

        self.ue_rx_element_max_g = config.getfloat("IMT_ANTENNA", "ue_rx_element_max_g")
        self.ue_rx_element_phi_3db = config.getfloat("IMT_ANTENNA", "ue_rx_element_phi_3db")
        self.ue_rx_element_theta_3db = config.getfloat("IMT_ANTENNA", "ue_rx_element_theta_3db")
        self.ue_rx_element_am = config.getfloat("IMT_ANTENNA", "ue_rx_element_am")
        self.ue_rx_element_sla_v = config.getfloat("IMT_ANTENNA", "ue_rx_element_sla_v")
        self.ue_rx_n_rows = config.getfloat("IMT_ANTENNA", "ue_rx_n_rows")
        self.ue_rx_n_columns = config.getfloat("IMT_ANTENNA", "ue_rx_n_columns")
        self.ue_rx_element_horiz_spacing = config.getfloat("IMT_ANTENNA", "ue_rx_element_horiz_spacing")
        self.ue_rx_element_vert_spacing = config.getfloat("IMT_ANTENNA", "ue_rx_element_vert_spacing")

    def get_antenna_parameters(self, sta_type: str, txrx: str) -> AntennaPar:
        """
        Get antenna parameters based on station type and the direction (TX/RX)

        :param sta_type: Station type. ["BS", "UE"]
        :param txrx: Direction of communication ["TX", "RX"]
        :return: Antenna Parameters named tuple. None if parameters are wrong
        """

        tpl = None
        if sta_type == "BS":
            if txrx == "TX":
                tpl = AntennaPar(self.bs_tx_element_max_g,
                                 self.bs_tx_element_phi_3db,
                                 self.bs_tx_element_theta_3db,
                                 self.bs_tx_element_am,
                                 self.bs_tx_element_sla_v,
                                 self.bs_tx_n_rows,
                                 self.bs_tx_n_columns,
                                 self.bs_tx_element_horiz_spacing,
                                 self.bs_tx_element_vert_spacing)
            elif txrx == "RX":
                tpl = AntennaPar(self.bs_rx_element_max_g,
                                 self.bs_rx_element_phi_3db,
                                 self.bs_rx_element_theta_3db,
                                 self.bs_rx_element_am,
                                 self.bs_rx_element_sla_v,
                                 self.bs_rx_n_rows,
                                 self.bs_rx_n_columns,
                                 self.bs_rx_element_horiz_spacing,
                                 self.bs_rx_element_vert_spacing)
        elif sta_type == "UE":
            if txrx == "TX":
                tpl = AntennaPar(self.ue_tx_element_max_g,
                                 self.ue_tx_element_phi_3db,
                                 self.ue_tx_element_theta_3db,
                                 self.ue_tx_element_am,
                                 self.ue_tx_element_sla_v,
                                 self.ue_tx_n_rows,
                                 self.ue_tx_n_columns,
                                 self.ue_tx_element_horiz_spacing,
                                 self.ue_tx_element_vert_spacing)
            elif txrx == "RX":
                tpl = AntennaPar(self.ue_rx_element_max_g,
                                 self.ue_rx_element_phi_3db,
                                 self.ue_rx_element_theta_3db,
                                 self.ue_rx_element_am,
                                 self.ue_rx_element_sla_v,
                                 self.ue_rx_n_rows,
                                 self.ue_rx_n_columns,
                                 self.ue_rx_element_horiz_spacing,
                                 self.ue_rx_element_vert_spacing)
        else:
            err_msg = "{} Invalid station type {}".format(__file__, sta_type)
            sys.stderr.write(err_msg)
            sys.exit(1)

        return tpl
