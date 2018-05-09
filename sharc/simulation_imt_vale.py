# -*- coding: utf-8 -*-
"""
Created on Apr 05 14:40 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""
from abc import ABC, abstractmethod
from sharc.support.observable import Observable

import numpy as np
import math
import sys
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

from sharc.support.enumerations import StationType
from sharc.topology.topology_factory import TopologyFactory
from sharc.parameters.parameters import Parameters
from sharc.parameters.parameters_imt_vale import ParametersImtVale
from sharc.propagation.propagation import Propagation
from sharc.station_manager import StationManager
from sharc.results import Results
from sharc.spectral_mask_imt import SpectralMaskImt
from sharc.spectral_mask_3gpp import SpectralMask3Gpp


class SimulationImtVale(ABC, Observable):

    def __init__(self, parameters: Parameters):
        ABC.__init__(self)
        Observable.__init__(self)

        self.parameters = parameters
        self.parameters_filename = parameters.file_name

        self.co_channel = self.parameters.general.enable_cochannel
        self.adjacent_channel = self.parameters.general.enable_adjacent_channel

        self.topology = TopologyFactory.createTopology(self.parameters)

        self.bs_power_gain = 0
        self.ue_power_gain = 0

        self.imt_bs_antenna_gain = list()
        self.imt_ue_antenna_gain = list()

        self.path_loss_imt = np.empty(0)
        self.coupling_loss_imt = np.empty(0)

        self.bs_to_ue_phi = np.empty(0)
        self.bs_to_ue_theta = np.empty(0)
        self.bs_to_ue_beam_rbs = np.empty(0)

        self.ue = np.empty(0)
        self.bs = np.empty(0)

        self.link = dict()

        self.num_rb_per_bs = 0
        self.num_rb_per_ue = 0

        self.results = None

        self.propagation_imt = None

        self.outage_per_drop = 0

        self.ues_in_outage_coordinates = []
        self.ues_in_outage_counter = []

    def add_observer_list(self, observers: list):
        for o in observers:
            self.add_observer(o)

    def initialize(self, *args, **kwargs):
        """
        This method is executed only once to initialize the simulation variables.
        """

        self.topology.calculate_coordinates()
        num_bs = self.topology.num_base_stations
        num_ue = self.parameters.imt.num_ue

        self.bs_power_gain = 10*math.log10(self.parameters.antenna_imt.bs_tx_n_rows *
                                           self.parameters.antenna_imt.bs_tx_n_columns)
        self.ue_power_gain = 10*math.log10(self.parameters.antenna_imt.ue_tx_n_rows *
                                           self.parameters.antenna_imt.ue_tx_n_columns)
        self.imt_bs_antenna_gain = list()
        self.imt_ue_antenna_gain = list()
        self.path_loss_imt = np.empty([num_bs, num_ue])
        self.coupling_loss_imt = np.empty([num_bs, num_ue])

        self.bs_to_ue_phi = np.empty([num_bs, num_ue])
        self.bs_to_ue_theta = np.empty([num_bs, num_ue])
        self.bs_to_ue_beam_rbs = -1.0*np.ones(num_ue, dtype=int)

        self.ue = np.empty(num_ue)
        self.bs = np.empty(num_bs)

        # this attribute indicates the list of UE's that are connected to each
        # base station. The position the the list indicates the resource block
        # group that is allocated to the given UE
        self.link = dict([(bs, list()) for bs in range(num_bs)])

        # calculates the number of RB per BS
        self.num_rb_per_bs = np.trunc((1 - self.parameters.imt.guard_band_ratio) *
                                             self.parameters.imt.bandwidth / self.parameters.imt.rb_bandwidth)

        # calculates the number of RB per UE on a given BS
        #self.num_rb_per_ue = np.trunc(self.num_rb_per_bs/self.parameters.imt.ue_k)
        self.num_rb_per_ue = np.power(0.1, 50)*np.ones(num_ue)

        self.results = Results(self.parameters_filename, self.parameters.general.overwrite_output)

    def finalize(self, *args, **kwargs):
        """
        Finalizes the simulation (collect final results, etc...)
        """
        snapshot_number = kwargs["snapshot_number"]
        self.results.write_files(snapshot_number)

    def calculate_coupling_loss(self,
                                station_a: StationManager,
                                station_b: StationManager,
                                propagation: Propagation) -> np.array:
        """
        Calculates the path coupling loss from each station_a to all station_b.
        Result is returned as a numpy array with dimensions num_a x num_b
        TODO: calculate coupling loss between activa stations only
        """
        path_loss = propagation.get_loss(bs_id=self.bs.station_id,
                                         ue_position_x=self.ue.x,
                                         ue_position_y=self.ue.y)

        # define antenna gains
        gain_a = self.calculate_gains(station_a, station_b)
        gain_b = np.transpose(self.calculate_gains(station_b, station_a))

        # collect IMT BS and UE antenna gain samples
        self.path_loss_imt = path_loss
        self.imt_bs_antenna_gain = gain_a
        self.imt_ue_antenna_gain = gain_b

        # calculate coupling loss
        coupling_loss = np.squeeze(path_loss - gain_a - gain_b)

        return coupling_loss

    def connect_ue_to_bs(self, param: ParametersImtVale):
        """
        Link the UE to the BS based on the RSSI.
        """
        # array with the path losses.
        path_loss = self.propagation_imt.get_loss(bs_id=self.bs.station_id, ue_position_x=self.ue.x,
                                                  ue_position_y=self.ue.y)
        num_bs = path_loss.shape[0]
        num_ue = path_loss.shape[1]

        # Initialize the BS links for each drop
        self.link = dict([(bs, list()) for bs in range(num_bs)])

        # forming the links between UEs and BSs based on the path loss
        ue_path_loss = {}
        ue_to_bs = {}

        for ue_index in range(0, num_ue):
            ue_path_loss[ue_index] = [path_loss[row, ue_index] for row in range(0, num_bs)]

            bs_index = ue_path_loss[ue_index].index(min(ue_path_loss[ue_index]))

            ue_to_bs[ue_index] = bs_index

            self.link[bs_index].append(ue_index)

        # UE BW and frequency is the same of it's connected BS.
        for bs in self.link.keys():
            for ue in self.link[bs]:
                self.ue.bandwidth[ue] = self.bs.bandwidth[bs]
                self.ue.center_freq[ue] = self.bs.center_freq[bs]

                if param.spectral_mask == "ITU 265-E":
                    self.ue.spectral_mask[ue] = SpectralMaskImt(StationType.IMT_UE, self.ue.center_freq[ue],
                                                                self.ue.bandwidth[ue], scenario="OUTDOOR")

                elif param.spectral_mask == "3GPP 36.104":
                    self.ue.spectral_mask[ue] = SpectralMask3Gpp(StationType.IMT_UE, self.ue.center_freq[ue],
                                                                 self.ue.bandwidth[ue])

                self.ue.spectral_mask[ue].set_mask()

    def scheduler(self):

        if self.parameters.general.imt_link == "DOWNLINK":
            # initializing the variables total_associated_ues and num_allocated_ues
            total_associated_ues = 0
            num_allocated_ues = 0

            bs_active = np.where(self.bs.active)[0]

            for bs in bs_active:
                ue_list = self.link[bs]

                # counting the total number of UEs associated to active BSs
                total_associated_ues += len(ue_list)

                # estimating the SINR for the first allocation
                sinr_vector = self.estimate_dl_sinr(bs, ue_list)

                # sort self.link[bs] in descending order of SINR
                self.link[bs] = [x for _, x in sorted(zip(sinr_vector, self.link[bs]))][::-1]
                sinr_vector = np.sort(sinr_vector)[::-1]

                # number of available RB for the current BS
                num_available_rbs = math.ceil(self.parameters.imt.bs_rb_load_factor*self.num_rb_per_bs[bs])

                allocated_ues = list()

                # allocation through the ue_list
                for i in range(len(self.link[bs])):

                    # get the throughput per RB for the current UE
                    ue_tput = self.get_throughput_dl(sinr_vector[i])*1e3

                    # calculate the number of RB required for the current UE
                    ue_num_rb = math.ceil(self.parameters.imt.min_ue_data_rate/ue_tput)

                    # checking if there are still available RBs in the current BS
                    if num_available_rbs > ue_num_rb:
                        # allocates the UE
                        num_available_rbs = num_available_rbs - ue_num_rb
                        allocated_ues.append(self.link[bs][i])

                        # calculating the UE's bandwidth
                        self.ue.bandwidth[self.link[bs][i]] = ue_num_rb * self.parameters.imt.rb_bandwidth
                        # number of RB allocated for the UE
                        self.num_rb_per_ue[self.link[bs][i]] = ue_num_rb

                    else:
                        # storing the x and y coordinates of the UE in outage
                        self.get_outage_positions(self.ue.x[self.link[bs][i]], self.ue.y[self.link[bs][i]])

                # self.link only with the allocated UEs
                self.link[bs] = allocated_ues

                # counting the number of allocated UEs on the given BS
                num_allocated_ues += len(allocated_ues)

                # activating the allocated UEs
                self.ue.active[self.link[bs]] = np.ones(len(self.link[bs]), dtype=bool)

                # calculating the BS's bandwidth
                self.bs.bandwidth[bs] = self.num_rb_per_bs[bs] * self.parameters.imt.rb_bandwidth

            if total_associated_ues != 0:
                # calculating the outage for the current drop
                self.outage_per_drop = 1 - num_allocated_ues/total_associated_ues
            else:
                self.outage_per_drop = 0

        else:
            # initializing the variables total_associated_ues and num_allocated_ues
            total_associated_ues = 0
            num_allocated_ues = 0

            bs_active = np.where(self.bs.active)[0]

            for bs in bs_active:
                ue_list = self.link[bs]

                # counting the total number of UEs associated to active BSs
                total_associated_ues += len(ue_list)

                # estimating the SINR for the first allocation
                sinr_vector = self.estimate_ul_sinr(bs, ue_list)

                # sort self.link[bs] in descending order of SINR
                self.link[bs] = [x for _, x in sorted(zip(sinr_vector, self.link[bs]))][::-1]
                sinr_vector = np.sort(sinr_vector)[::-1]

                # number of available RB for the current BS
                num_available_rbs = math.ceil(self.parameters.imt.bs_rb_load_factor * self.num_rb_per_bs[bs])

                allocated_ues = list()
                # allocation through the ue_list
                for i in range(len(self.link[bs])):

                    # get the throughput per RB for the current UE
                    ue_tput = self.get_throughput_ul(sinr_vector[i])*1e3

                    # calculate the number of RB required for the current UE
                    ue_num_rb = math.ceil(self.parameters.imt.min_ue_data_rate / ue_tput)

                    # checking if there are still available RBs in the current BS
                    if num_available_rbs > ue_num_rb:
                        # allocates the UE
                        num_available_rbs = num_available_rbs - ue_num_rb
                        allocated_ues.append(self.link[bs][i])

                        # calculating the UE's bandwidth
                        self.ue.bandwidth[self.link[bs][i]] = ue_num_rb * self.parameters.imt.rb_bandwidth
                        # number of RB allocated for the UE
                        self.num_rb_per_ue[self.link[bs][i]] = ue_num_rb
                    else:
                        # storing the x and y coordinates of the UE in outage
                        self.get_outage_positions(self.ue.x[self.link[bs][i]], self.ue.y[self.link[bs][i]])

                # self.link only with the allocated UEs
                self.link[bs] = allocated_ues

                # counting the number of allocated UEs on the given BS
                num_allocated_ues += len(allocated_ues)

                # activating the allocated UEs
                self.ue.active[self.link[bs]] = np.ones(len(self.link[bs]), dtype=bool)

                # calculating the BS's bandwidth
                self.bs.bandwidth[bs] = self.num_rb_per_bs[bs] * self.parameters.imt.rb_bandwidth

                if total_associated_ues != 0:
                    # calculating the outage for the current drop
                    self.outage_per_drop = 1 - num_allocated_ues / total_associated_ues
                else:
                    self.outage_per_drop = 0

    def estimate_dl_sinr(self, current_bs, ue_list):
        """
        This method estimates the DL SINR for the first allocation done by the scheduler
        """
        # initializing the interference variable
        rx_interference = -500 * np.ones(len(ue_list))

        # determining the TX power of each BS
        total_power = self.parameters.imt.bs_conducted_power + self.bs_power_gain

        bs_active = np.where(self.bs.active)[0]
        tx_power = dict([(bs, list()) for bs in bs_active])
        bs_tx_power = dict([(bs, list()) for bs in bs_active])
        for bs in bs_active:
            # TX power equally divided among the RBs
            tx_power[bs] = total_power[bs] - 10 * np.log10(self.num_rb_per_bs[bs])
            # TX power to each UE connected to the current BS
            bs_tx_power[bs] = tx_power[bs] * np.ones(len(self.link[bs]))

        # array with the received power for each UE connected to the current BS
        ue_rx_power = bs_tx_power[current_bs] \
                        - self.parameters.imt.bs_ohmic_loss \
                        - self.parameters.imt.ue_body_loss \
                        - self.parameters.imt.ue_ohmic_loss \
                        - self.coupling_loss_imt[current_bs, ue_list]

        # create a list with base stations that generate interference in ue_list
        bs_interf = [b for b in bs_active if b not in [current_bs]]
        # eliminating BSs that don't have associated UEs
        bs_interf = [b for b in bs_interf if self.link[b]]

        # calculate intra system interference
        for bi in bs_interf:
            interference = bs_tx_power[bi][0] - self.parameters.imt.bs_ohmic_loss \
                            - self.coupling_loss_imt[bi, ue_list] \
                            - self.parameters.imt.ue_body_loss - self.parameters.imt.ue_ohmic_loss

            rx_interference = 10*np.log10( \
                    np.power(10, 0.1*rx_interference)
                    + np.power(10, 0.1*interference))

        # thermal noise (per RB)
        thermal_noise = \
            10 * np.log10(self.parameters.imt.BOLTZMANN_CONSTANT * self.parameters.imt.noise_temperature * 1e3) + \
            10 * np.log10(self.parameters.imt.rb_bandwidth * 1e6) + \
            self.ue.noise_figure[ue_list]

        # total interference per UE
        total_interference = 10 * np.log10(np.power(10, 0.1*rx_interference) + np.power(10, 0.1*thermal_noise))

        # calculating the SINR for each UE
        sinr_vector = ue_rx_power - total_interference

        return sinr_vector

    def estimate_ul_sinr(self, current_bs, ue_list):
        """
        This method estimates the DL SINR for the first allocation done by the scheduler
        """
        # initializing the interference variable
        rx_interference = -500 * np.ones(len(ue_list))

        # determining the TX power of each UE (no power control considered)
        ue_tx_power = self.parameters.imt.ue_p_cmax * np.ones(len(ue_list))

        # array with the received power of the BS from each UE
        bs_rx_power = ue_tx_power  \
                     - self.parameters.imt.ue_ohmic_loss \
                     - self.parameters.imt.ue_body_loss \
                     - self.coupling_loss_imt[current_bs, ue_list] \
                     - self.parameters.imt.bs_ohmic_loss

        # create a list with base stations that generate interference in the current BS
        bs_active = np.where(self.bs.active)[0]
        bs_interf = [b for b in bs_active if b not in [current_bs]]
        # eliminating BSs that don't have associated UEs
        bs_interf = [b for b in bs_interf if self.link[b]]

        # calculate intra system interference (consider only the UE closest to the current BS)
        for bi in bs_interf:
            ui = self.link[bi]

            # coupling loss from the interfering UEs to the current BS
            ui_losses = self.coupling_loss_imt[current_bs, ui]

            # minimum coupling loss between the current BS and an adjacent UE
            min_ui_loss = min(ui_losses)

            interference = ue_tx_power - self.parameters.imt.ue_ohmic_loss \
                           - self.parameters.imt.ue_body_loss \
                           - min_ui_loss - self.parameters.imt.bs_ohmic_loss

            rx_interference = 10*np.log10( \
                    np.power(10, 0.1*rx_interference)
                    + np.power(10, 0.1*interference))

        # calculate N
        thermal_noise = \
            10 * np.log10(self.parameters.imt.BOLTZMANN_CONSTANT * self.parameters.imt.noise_temperature * 1e3) + \
            10 * np.log10(self.parameters.imt.rb_bandwidth * self.num_rb_per_bs[current_bs] * 1e6) + \
            self.bs.noise_figure[current_bs]

        # total interference per UE
        total_interference = 10 * np.log10(np.power(10, 0.1 * rx_interference) + np.power(10, 0.1 * thermal_noise))

        # calculating the SINR for each UE
        sinr_vector = bs_rx_power - total_interference

        return sinr_vector

    def get_throughput_dl(self, ue_sinr):
        """
        This method returns the throughput per RB in kbps for a given SINR in the DL
        """
        sinr_vals = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                     21, 22, 23, 24, 25]
        tput_vals = [39.7154, 48.2521, 58.2422, 69.7951, 82.9873, 97.8559, 114.3942, 132.5529, 152.2445, 173.3518,
                     195.7379, 219.2562, 243.7591, 269.1051, 295.1634, 321.8168, 348.9628, 376.5132, 404.5830, 442.8072,
                     481.8425, 521.5469, 561.7995, 602.4986, 643.5594, 684.9121, 726.4998, 768.2760, 810.2032, 852.2511,
                     894.3953, 936.6164]

        if ue_sinr > 25:
            ue_tput = 936.6164
        elif ue_sinr < - 6:
            # negligible value to represent a throughput equal to zero. Cannot set to zero due to the division done in
            # the scheduler method
            ue_tput = np.power(0.1, 50)
        else:
            # interpolate and generate MCS curve
            mcs_curve = interp1d(sinr_vals, tput_vals)

            # throughput per RB for the given MCS
            ue_tput = mcs_curve(ue_sinr)

        return ue_tput

    def get_throughput_ul(self, ue_sinr):
        """
        This method returns the throughput per RB in kbps for a given SINR in the UL
        """
        sinr_vals = [-11.5, -10, -6, -2, 2, 6, 10, 14, 18, 22, 24.1, 30]
        tput_vals = [4.492, 8.532, 29.956, 71.008, 126.814, 211.917, 322.393, 443.439, 575.342, 692.987, 720.702,
                     720.702]

        if ue_sinr > 30:
            ue_tput = 720.702
        elif ue_sinr < - 11.5:
            # negligible value to represent a throughput equal to zero. Cannot set to zero due to the division done in
            # the scheduler method
            ue_tput = np.power(0.1, 50)
        else:
            # interpolate and generate MCS curve
            mcs_curve = interp1d(sinr_vals, tput_vals)

            # throughput per RB for the given MCS
            ue_tput = mcs_curve(ue_sinr)

        return ue_tput

    def get_outage_positions(self, ue_x, ue_y):
        """
        Saves the (x, y) coordinates of the UEs in outage and counts its occurrences
        """

        # tuple with the x,y coordinates of the UE in outage
        outage_position = (ue_x, ue_y)

        # checking if the current outage occurred before
        if outage_position not in self.ues_in_outage_coordinates:
            # appends the current coordinates to the list
            self.ues_in_outage_coordinates.append(outage_position)
            # counts the first occurrence of the current position
            self.ues_in_outage_counter.append(1)
        else:
            # get the index of the tuple that is already registered
            index = self.ues_in_outage_coordinates.index(outage_position)
            # counts one more occurrence
            self.ues_in_outage_counter[index] += 1


    def calculate_gains(self, station_1: StationManager, station_2: StationManager) -> np.array:
        """
        Calculates the gains of antennas in station_1 in the direction of
        station_2
        """
        phi, theta = station_1.get_pointing_vector_to(station_2)

        station_1_active = np.where(station_1.active)[0]
        station_2_active = np.where(station_2.active)[0]

        # Initialize variables (phi, theta, beams_idx)
        if station_1.station_type is StationType.IMT_BS:
            if station_2.station_type is StationType.IMT_UE:
                beams_idx = self.bs_to_ue_beam_rbs[station_2_active]

        elif station_1.station_type is StationType.IMT_UE:
            beams_idx = np.zeros(len(station_2_active), dtype=int)

        # Calculate gains
        gains = np.zeros(phi.shape)
        for k in station_1_active:
            gains[k, station_2_active] = station_1.antenna[k].calculate_gain(phi_vec=phi[k, station_2_active],
                                                                             theta_vec=theta[k, station_2_active],
                                                                             beams_l=beams_idx)

        return gains

    def calculate_imt_tput(self,
                           sinr: np.array,
                           sinr_min: float,
                           sinr_max: float,
                           attenuation_factor: float) -> np.array:
        tput_min = 0
        tput_max = attenuation_factor*math.log2(1+math.pow(10, 0.1*sinr_max))

        tput = attenuation_factor*np.log2(1+np.power(10, 0.1*sinr))

        id_min = np.where(sinr < sinr_min)[0]
        id_max = np.where(sinr > sinr_max)[0]

        if len(id_min) > 0:
            tput[id_min] = tput_min
        if len(id_max) > 0:
            tput[id_max] = tput_max

        return tput

    def calculate_bw_weights(self, bw_imt: float, bw_sys: float, ue_k: int) -> np.array:
        """
        Calculates the weight that each resource block group of IMT base stations
        will have when estimating the interference to other systems based on
        the bandwidths of both systems.

        Parameters
        ----------
            bw_imt : bandwidth of IMT system
            bw_sys : bandwidth of other system
            ue_k : number of UE's allocated to each IMT base station; it also
                corresponds to the number of resource block groups

        Returns
        -------
            K-dimentional array of weights
        """

        if bw_imt <= bw_sys:
            weights = np.ones(ue_k)

        elif bw_imt > bw_sys:
            weights = np.zeros(ue_k)

            bw_per_rbg = bw_imt / ue_k

            # number of resource block groups that will have weight equal to 1
            rb_ones = math.floor( bw_sys / bw_per_rbg )

            # weight of the rbg that will generate partial interference
            rb_partial = np.mod( bw_sys, bw_per_rbg ) / bw_per_rbg

            # assign value to weight array
            weights[:rb_ones] = 1
            weights[rb_ones] = rb_partial

        return weights

    def plot_scenario(self):
        fig = plt.figure(figsize=(8,8), facecolor='w', edgecolor='k')
        ax = fig.gca()

        # Plot network topology
        self.topology.plot(ax)

        # Plot user equipments
        ax.scatter(self.ue.x, self.ue.y, color='r', edgecolor="w", linewidth=0.5, label="UE")

        # Plot UE's azimuth
        d = 0.1 * self.topology.cell_radius
        for i in range(len(self.ue.x)):
            plt.plot([self.ue.x[i], self.ue.x[i] + d*math.cos(math.radians(self.ue.azimuth[i]))],
                     [self.ue.y[i], self.ue.y[i] + d*math.sin(math.radians(self.ue.azimuth[i]))],
                     'r-')

        plt.axis('image')
        plt.title("Simulation scenario")
        plt.xlabel("x-coordinate [m]")
        plt.ylabel("y-coordinate [m]")
        plt.legend(loc="upper left", scatterpoints=1)
        plt.tight_layout()
        plt.show()

        sys.exit(0)

    def get_simulation_description(self) -> str:

        description = "\nIMT Capacity Simulation for Vale Project:\n" \
                            + "\tdirection: {:s}\n".format(self.parameters.general.imt_link) \
                            + "\tnum_macrocell_sites: {:.0f}\n".format(self.parameters.imt.num_macrocell_sites) \
                            + "\tbs_physical_data_file: {:s}\n".format(self.parameters.imt.bs_physical_data_file) \
                            + "\ttopography_data_file: {:s}\n".format(self.parameters.imt.topography_data_file) \
                            + "\tue_polygon_file: {:s}\n".format(self.parameters.imt.ue_polygon_file) \
                            + "\ttopology: {:s}\n".format(self.parameters.imt.topology) \
                            + "\tpath loss model: {:s}\n".format(self.parameters.imt.channel_model)

        return description

    @abstractmethod
    def snapshot(self, *args, **kwargs):
        """
        Performs a single snapshot.
        """
        pass

    @abstractmethod
    def power_control(self):
        """
        Apply downlink power control algorithm
        """

    @abstractmethod
    def collect_results(self, *args, **kwargs):
        """
        Collects results.
        """
        pass
