# -*- coding: utf-8 -*-
"""
Created on Apr 05 10:37 2018

@author: Bruno Faria (bruno.faria@ektrum.com)
"""
import numpy as np
import math

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
                                                                 self.topology)

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

    def power_control(self):
        """
        Apply downlink power control algorithm
        """
        # TODO use physical data for this power control
        # Currently, the maximum transmit power of the base station is equaly
        # divided among the selected UEs
        total_power = self.parameters.imt.bs_conducted_power + self.bs_power_gain

        # calculate transmit powers to have a structure such as
        # {bs_1: [pwr_1, pwr_2,...], ...}, where bs_1 is the base station id,
        # pwr_1 is the transmit power from bs_1 to ue_1, pwr_2 is the transmit
        # power from bs_1 to ue_2, etc
        bs_active = np.where(self.bs.active)[0]
        tx_power = dict([(bs, list()) for bs in bs_active])
        self.bs.tx_power = dict([(bs, list()) for bs in bs_active])
        for bs in bs_active:
            tx_power[bs] = total_power[bs] - 10*np.log10(len(self.link[bs]))
            self.bs.tx_power[bs] = tx_power[bs]*np.ones(len(self.link[bs]))

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

                self.ue.rx_interference[ue] = 10*np.log10( \
                    np.power(10, 0.1*self.ue.rx_interference[ue]) + np.power(10, 0.1*interference))

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

