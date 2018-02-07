# -*- coding: utf-8 -*-
"""
Created on Wed Feb 15 16:05:58 2017

@author: edgar
"""

import pandas as pd
import sys

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
            sys.stderr.write(str(err) + "\n")
            sys.exit(1)

        bs_data_headers = set(list(bs_data_df.columns))
        if not bs_data_headers.issuperset(param_min_set):
            sys.stderr.write('Parameter file error: Parameter(s) not recognized or the parameters file does not \n'
                             'contain the minimal set of parametes: {}'.format(param_min_set))
            sys.exit(1)
        else:
            return bs_data_df.to_dict('list')
