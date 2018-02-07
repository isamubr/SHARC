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
        # FIXME: Need to do some sanity check on the input file

        try:
            bs_data_df = pd.read_excel(cell_data_file_name)
        except FileNotFoundError as err:
            sys.stderr.write(str(err) + "\n")
            sys.exit(1)
        return bs_data_df.to_dict('list')

