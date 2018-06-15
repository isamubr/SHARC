# -*- coding: utf-8 -*-
"""
Created on Apr 06 09:29 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""

import numpy as np
import math
from scipy.interpolate import interp1d

from sharc.simulation_imt_vale import SimulationImtVale
from sharc.parameters.parameters import Parameters
from sharc.station_factory import StationFactory

from sharc.propagation.propagation_factory import PropagationFactory


class SimulationImtValeUplink(SimulationImtVale):
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
        Initializes the MCS curve for UL that maps the SINR to the max throughput.
        This is done in initialization time to save some computation
        :return: None
        """
        SINR_VALS = [-11.5, -10, -6, -2, 2, 6, 10, 14, 18, 22, 24.1, 30]
        TPUT_VALS = [4.492, 8.532, 29.956, 71.008, 126.814, 211.917, 322.393, 443.439, 575.342, 692.987, 720.702,
                     720.702]

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

        self.connect_ue_to_bs(self.parameters.imt)

        # Calculate coupling loss after beams are created
        self.coupling_loss_imt = self.calculate_coupling_loss(self.bs,
                                                              self.ue,
                                                              self.propagation_imt)
        self.scheduler()

        self.power_control()

        self.calculate_sinr()

        self.collect_results(write_to_file, snapshot_number)

    def scheduler(self):
        """
        Implements the scheluder algorithm on the UL direction
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
            sinr_vector = self.estimate_ul_sinr(bs, ue_list)

            # sort self.link[bs] in descending order of SINR
            self.link[bs] = [x for _, x in sorted(zip(sinr_vector, self.link[bs]))][::-1]
            self.ue.sinr[self.link[bs]] = np.sort(sinr_vector)[::-1]

            # Each round the SINR estimation is updated. At least 2 rounds are needed for a stable estimation.
            for i in range(self.SCHED_MAX_ALLOC_ROUNDS):

                # number of available RB for the current BS
                num_available_rbs = math.ceil(self.parameters.imt.bs_rb_load_factor * self.num_rb_per_bs[bs])

                allocated_ues = list()
                # allocation through the ue_list
                for ue in self.link[bs]:

                    # get the throughput per RB for the current UE
                    ue_tput = self.get_throughput_ul(self.ue.sinr[ue])*1e3

                    # calculate the number of RB required for the current UE
                    ue_num_rb = math.ceil(self.parameters.imt.min_ue_data_rate / ue_tput)

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

                # counting the number of allocated UEs on the given BS
                num_allocated_ues += len(allocated_ues)

                # activating the allocated UEs
                self.ue.active[self.link[bs]] = np.ones(len(self.link[bs]), dtype=bool)

                # calculating the BS's bandwidth
                self.bs.bandwidth[bs] = self.num_rb_per_bs[bs] * self.parameters.imt.rb_bandwidth

                # calculating the UE's bandwidth
                self.ue.bandwidth[self.link[bs]] = self.num_rb_per_ue[self.link[bs]] * self.parameters.imt.rb_bandwidth

        if total_associated_ues != 0:
            # calculating the outage for the current drop
            self.outage_per_drop = 1 - num_allocated_ues / total_associated_ues
        else:
            self.outage_per_drop = 0

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

    def get_throughput_ul(self, ue_sinr):
        """
        This method returns the throughput per RB in kbps for a given SINR in the UL
        """
        if ue_sinr > 30:
            ue_tput = 720.702
        elif ue_sinr < - 11.5:
            # negligible value to represent a throughput equal to zero. Cannot set to zero due to the division done in
            # the scheduler method
            ue_tput = np.power(0.1, 50)
        else:
            # throughput per RB for the given MCS
            ue_tput = self.mcs_curve(ue_sinr)

        return ue_tput

    def power_control(self):
        """
        Apply uplink power control algorithm
        """
        if self.parameters.imt.ue_tx_power_control == "OFF":
            ue_active = np.where(self.ue.active)[0]
            self.ue.tx_power[ue_active] = self.parameters.imt.ue_p_cmax * np.ones(len(ue_active))
        else:
            bs_active = np.where(self.bs.active)[0]
            for bs in bs_active:
                ue = self.link[bs]
                p_cmax = self.parameters.imt.ue_p_cmax
                m_pusch = self.num_rb_per_ue[ue]
                p_o_pusch = self.parameters.imt.ue_p_o_pusch
                alpha = self.parameters.imt.ue_alpha
                pl = self.coupling_loss_imt[bs, ue] + self.parameters.imt.bs_ohmic_loss \
                    + self.parameters.imt.ue_ohmic_loss + self.parameters.imt.ue_body_loss
                self.ue.tx_power[ue] = np.minimum(p_cmax, 10*np.log10(m_pusch) + p_o_pusch + alpha*pl)

    def calculate_sinr(self):
        """
        Calculates the uplink SINR for each BS.
        """
        # calculate uplink received power for each active BS
        bs_active = np.where(self.bs.active)[0]
        for bs in bs_active:
            ue = self.link[bs]

            self.bs.rx_power[bs] = self.ue.tx_power[ue] - \
                                   self.parameters.imt.ue_ohmic_loss - \
                                   self.parameters.imt.ue_body_loss - \
                                   self.coupling_loss_imt[bs, ue] - \
                                   self.parameters.imt.bs_ohmic_loss

            # create a list of BSs that serve the interfering UEs
            bs_interf = [b for b in bs_active if b not in [bs]]
            # eliminating BSs that don't have associated UEs
            bs_interf = [b for b in bs_interf if self.link[b]]

            # calculate intra system interference
            for bi in bs_interf:
                ui = self.link[bi]
                interference = self.ue.tx_power[ui] - self.parameters.imt.ue_ohmic_loss - \
                               self.parameters.imt.ue_body_loss - \
                               self.coupling_loss_imt[bs, ui] - self.parameters.imt.bs_ohmic_loss

                # summing all the interferences
                interference_linear = np.power(10, 0.1*interference)
                interference_linear = sum(interference_linear)
                interference = 10*np.log10(interference_linear)

                self.bs.rx_interference[bs] = 10*np.log10(np.power(10, -50.0) +  # Prevent log(0)
                                                          np.power(10, 0.1*interference))

            # calculate N
            self.bs.thermal_noise[bs] = \
                10*np.log10(self.parameters.imt.BOLTZMANN_CONSTANT*self.parameters.imt.noise_temperature*1e3) + \
                10*np.log10(self.ue.bandwidth[ue] * 1e6) + \
                self.bs.noise_figure[bs]

            # calculate I+N
            self.bs.total_interference[bs] = \
                10*np.log10(np.power(10, 0.1*self.bs.rx_interference[bs]) + \
                            np.power(10, 0.1*self.bs.thermal_noise[bs]))

            # calculate SNR and SINR
            self.bs.sinr[bs] = self.bs.rx_power[bs] - self.bs.total_interference[bs]
            self.bs.snr[bs] = self.bs.rx_power[bs] - self.bs.thermal_noise[bs]

    def collect_results(self, write_to_file: bool, snapshot_number: int):
        bs_active = np.where(self.bs.active)[0]
        for bs in bs_active:
            ue = self.link[bs]
            self.results.imt_path_loss.extend(self.path_loss_imt[bs, ue])
            self.results.imt_coupling_loss.extend(self.coupling_loss_imt[bs, ue])

            self.results.imt_bs_antenna_gain.extend(self.imt_bs_antenna_gain[bs, ue])
            self.results.imt_ue_antenna_gain.extend(self.imt_ue_antenna_gain[bs, ue])

            tput = self.calculate_imt_tput(self.bs.sinr[bs],
                                           self.parameters.imt.ul_sinr_min,
                                           self.parameters.imt.ul_sinr_max,
                                           self.parameters.imt.ul_attenuation_factor)
            self.results.imt_ul_tput.extend(tput.tolist())

            self.results.imt_ul_tx_power.extend(self.ue.tx_power[ue].tolist())
            imt_ul_tx_power_density = 10 * np.log10(np.power(10, 0.1 * self.ue.tx_power[ue]) / (
                self.ue.bandwidth[ue]))
            self.results.imt_ul_tx_power_density.extend(imt_ul_tx_power_density.tolist())
            self.results.imt_ul_sinr.extend(self.bs.sinr[bs].tolist())
            self.results.imt_ul_snr.extend(self.bs.snr[bs].tolist())

            self.results.imt_outage_per_drop.append(self.outage_per_drop)

            ue_x = [i[0] for i in self.ues_in_outage_coordinates]
            ue_y = [i[1] for i in self.ues_in_outage_coordinates]

            self.results.imt_ues_in_outage_map = list(zip(ue_x, ue_y, self.ues_in_outage_counter))

            self.results.imt_num_rb_per_ue.extend(self.num_rb_per_ue[self.link[bs]])

        if write_to_file:
            self.results.write_files(snapshot_number)
            self.notify_observers(source=__name__, results=self.results)



