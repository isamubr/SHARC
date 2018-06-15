# -*- coding: utf-8 -*-
"""
Created on Apr 05 10:37 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""
import numpy as np
import math
from scipy.interpolate import interp1d

from sharc.simulation_imt_vale import SimulationImtVale
from sharc.parameters.parameters import Parameters
from sharc.station_factory import StationFactory

from sharc.propagation.propagation_factory import PropagationFactory


class SimulationImtValeDownlink(SimulationImtVale):
    """
    Implements the flowchart of simulation downlink method
    """

    def __init__(self, parameters: Parameters):
        super().__init__(parameters)
        self.SCHED_MAX_ALLOC_ROUNDS = 2
        self.mcs_curve = None
        self.initialize_mcs_curve()

    def initialize_mcs_curve(self):
        """
        Initializes the MCS curve for DL that maps the SINR to the max throughput.
        This is done in initialization time to save some computation
        :return: None
        """
        SINR_VALS = [-6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                     21, 22, 23, 24, 25]

        TPUT_VALS = [39.7154, 48.2521, 58.2422, 69.7951, 82.9873, 97.8559, 114.3942, 132.5529, 152.2445, 173.3518,
                     195.7379, 219.2562, 243.7591, 269.1051, 295.1634, 321.8168, 348.9628, 376.5132, 404.5830, 442.8072,
                     481.8425, 521.5469, 561.7995, 602.4986, 643.5594, 684.9121, 726.4998, 768.2760, 810.2032, 852.2511,
                     894.3953, 936.6164]

        self.mcs_curve = interp1d(SINR_VALS, TPUT_VALS)

    def snapshot(self, *args, **kwargs):
        write_to_file = kwargs["write_to_file"]
        snapshot_number = kwargs["snapshot_number"]
        seed = kwargs["seed"]

        random_number_gen = np.random.RandomState(seed)

        self.propagation_imt = PropagationFactory.create_propagation(self.parameters.imt.channel_model,
                                                                     self.parameters,
                                                                     random_number_gen)

        # In case of hotspots, base stations coordinates have to be calculated
        # on every snapshot. Anyway, let topology decide whether to calculate
        # or not
        self.topology.calculate_coordinates(random_number_gen)

        # Create the base stations (remember that it takes into account the
        # network load factor)
        self.bs = StationFactory.generate_imt_vale_base_stations(self.parameters.imt,
                                                                 self.parameters.antenna_imt,
                                                                 self.topology,
                                                                 random_number_gen)

        # Create IMT user equipments
        self.ue = StationFactory.generate_imt_ue_vale_outdoor(self.parameters.imt,
                                                              self.parameters.antenna_imt,
                                                              random_number_gen,
                                                              self.topology)
        # Associating UEs and BSs based on the RSSI
        self.connect_ue_to_bs(self.parameters.imt)

        # Calculate coupling loss
        self.coupling_loss_imt = self.calculate_coupling_loss(self.bs,
                                                              self.ue,
                                                              self.propagation_imt)
        # Allocating and activating the UEs
        self.scheduler()

        self.power_control()

        self.calculate_sinr()

        self.collect_results(write_to_file, snapshot_number)

    def finalize(self, *args, **kwargs):
        self.notify_observers(source=__name__, results=self.results)

    def scheduler(self):
        """
        Implements the scheluder algorithm on the DL direction
        The scheduler allocates resources based on SINR. The potential allocated UEs are sorted in order of the best
        SINR and the RBs are allocated based on the minimum data rate. The numbers of RB depends on the MCS for that
        UE.
        :return: None
        """

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
            self.ue.sinr[self.link[bs]] = np.sort(sinr_vector)[::-1]

            # Each round the SINR estimation is updated. At least 2 rounds are needed for a stable estimation.
            for i in range(self.SCHED_MAX_ALLOC_ROUNDS):
                # number of available RB for the current BS
                num_available_rbs = math.ceil(self.parameters.imt.bs_rb_load_factor*self.num_rb_per_bs[bs])

                allocated_ues = list()

                # allocation through the ue_list
                for ue in self.link[bs]:

                    # get the throughput per RB for the current UE
                    ue_tput = self.get_throughput_dl(self.ue.sinr[ue])*1e3

                    # calculate the number of RB required for the current UE
                    ue_num_rb = math.ceil(self.parameters.imt.min_ue_data_rate/ue_tput)

                    # checking if there are still available RBs in the current BS
                    if num_available_rbs > ue_num_rb:
                        # allocates the UE
                        num_available_rbs = num_available_rbs - ue_num_rb
                        allocated_ues.append(ue)

                        # number of RB allocated for the UE
                        self.num_rb_per_ue[ue] = ue_num_rb

                    else:
                        # storing the x and y coordinates of the UE in outage
                        self.get_outage_positions(self.ue.x[ue], self.ue.y[ue])

                # self.link only with the allocated UEs
                self.link[bs] = allocated_ues

                # Update the estimation of DL SINR after allocation
                self.power_control()
                self.calculate_sinr()

            if self.link[bs]:
                # Distribute the remaining RB to the UEs in a round-robin fashion
                n = -1
                num_rb_per_ue = self.num_rb_per_ue[self.link[bs]]
                while num_available_rbs:
                    n += 1
                    num_rb_per_ue[n % len(num_rb_per_ue)] += 1
                    num_available_rbs -= 1
                self.num_rb_per_ue[self.link[bs]] = num_rb_per_ue

                # calculating the UE's bandwidth
                self.ue.bandwidth[self.link[bs]] = self.num_rb_per_ue[self.link[bs]] * self.parameters.imt.rb_bandwidth

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

    def get_throughput_dl(self, ue_sinr):
        """
        This method returns the throughput per RB in kbps for a given SINR in the DL
        """
        if ue_sinr > 25:
            ue_tput = 936.6164
        elif ue_sinr < - 6:
            # negligible value to represent a throughput equal to zero. Cannot set to zero due to the division done in
            # the scheduler method
            ue_tput = np.power(0.1, 50)
        else:
            # throughput per RB for the given MCS
            ue_tput = self.mcs_curve(ue_sinr)

        return ue_tput

    def power_control(self):
        """
        Apply downlink power control algorithm
        """
        # The maximum transmit power of the base station is divided among
        # active UEs, proportionally to the number of RBs occupied
        total_power = self.parameters.imt.bs_conducted_power + self.bs_power_gain

        # calculate transmit powers to have a structure such as
        # {bs_1: [pwr_1, pwr_2,...], ...}, where bs_1 is the base station id,
        # pwr_1 is the transmit power from bs_1 to ue_1, pwr_2 is the transmit
        # power from bs_1 to ue_2, etc
        bs_active = np.where(self.bs.active)[0]
        self.bs.tx_power = dict([(bs, list()) for bs in bs_active])

        for bs in bs_active:
            # checking if there are UEs allocated in the current BS
            if len(self.link[bs]) != 0:
                # allocated UEs
                ue_list = self.link[bs]

                for ue in ue_list:
                    # distribute power proportionally to the number of RBs occupied
                    self.bs.tx_power[bs].append(total_power[bs] + 10*np.log10(self.num_rb_per_ue[ue]
                                                                              / self.num_rb_per_bs[bs]))

                # converting the list to array
                self.bs.tx_power[bs] = np.asarray(self.bs.tx_power[bs])

            else:
                # de-activate current BS
                self.bs.tx_power[bs] = np.asarray([])

        # Update the spectral mask
        if self.adjacent_channel:
            for bs in bs_active:
                self.bs.spectral_mask[bs].set_mask(power=total_power[bs])

    def calculate_sinr(self):
        """
        Calculates the downlink SINR for each UE.
        """
        bs_active = np.where(self.bs.active)[0]
        for bs in bs_active:
            ue = self.link[bs]
            self.ue.rx_power[ue] = self.bs.tx_power[bs] - self.parameters.imt.bs_ohmic_loss \
                                       - self.coupling_loss_imt[bs, ue] \
                                       - self.parameters.imt.ue_body_loss \
                                       - self.parameters.imt.ue_ohmic_loss

            # create a list with base stations that generate interference in ue_list
            bs_interf = [b for b in bs_active if b not in [bs]]
            # eliminating BSs that don't have associated UEs
            bs_interf = [b for b in bs_interf if self.link[b]]

            # calculate intra system interference
            for bi in bs_interf:
                interference = self.bs.tx_power[bi][0] - self.parameters.imt.bs_ohmic_loss \
                                 - self.coupling_loss_imt[bi, ue] \
                                 - self.parameters.imt.ue_body_loss - self.parameters.imt.ue_ohmic_loss

                self.ue.rx_interference[ue] = 10*np.log10(np.power(10, -50.0) +  # Prevent log(0)
                                                          np.power(10, 0.1*interference))

        self.ue.thermal_noise = \
            10*math.log10(self.parameters.imt.BOLTZMANN_CONSTANT * self.parameters.imt.noise_temperature*1e3) + \
            10*np.log10(self.ue.bandwidth * 1e6) + \
            self.ue.noise_figure

        self.ue.total_interference = \
            10*np.log10(np.power(10, 0.1*self.ue.rx_interference) +
                        np.power(10, 0.1*self.ue.thermal_noise))

        self.ue.sinr = self.ue.rx_power - self.ue.total_interference
        self.ue.snr = self.ue.rx_power - self.ue.thermal_noise

    def collect_results(self, write_to_file: bool, snapshot_number: int):

        bs_active = np.where(self.bs.active)[0]
        for bs in bs_active:
            ue = self.link[bs]
            self.results.imt_path_loss.extend(self.path_loss_imt[bs, ue])
            self.results.imt_coupling_loss.extend(self.coupling_loss_imt[bs, ue])

            self.results.imt_bs_antenna_gain.extend(self.imt_bs_antenna_gain[bs, ue])
            self.results.imt_ue_antenna_gain.extend(self.imt_ue_antenna_gain[bs, ue])

            tput = self.calculate_imt_tput(self.ue.sinr[ue],
                                           self.parameters.imt.dl_sinr_min,
                                           self.parameters.imt.dl_sinr_max,
                                           self.parameters.imt.dl_attenuation_factor)
            self.results.imt_dl_tput.extend(tput.tolist())
            self.results.imt_dl_tx_power.extend(self.bs.tx_power[bs].tolist())
            self.results.imt_dl_sinr.extend(self.ue.sinr[ue].tolist())
            self.results.imt_dl_snr.extend(self.ue.snr[ue].tolist())

            self.results.imt_outage_per_drop.append(self.outage_per_drop)

            ue_x = [i[0] for i in self.ues_in_outage_coordinates]
            ue_y = [i[1] for i in self.ues_in_outage_coordinates]

            self.results.imt_ues_in_outage_map = list(zip(ue_x, ue_y, self.ues_in_outage_counter))

        if write_to_file:
            self.results.write_files(snapshot_number)
            self.notify_observers(source=__name__, results=self.results)

