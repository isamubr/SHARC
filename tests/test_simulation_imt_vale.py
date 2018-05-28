# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 15:28:06 2018

@author: Calil
"""

import unittest
import numpy as np
import numpy.testing as npt
from shapely.geometry import Polygon
import os

from sharc.simulation_imt_vale_downlink import SimulationImtValeDownlink
from sharc.simulation_imt_vale_uplink import SimulationImtValeUplink
from sharc.parameters.parameters import Parameters
from sharc.antenna.antenna_omni import AntennaOmni
from sharc.station_factory import StationFactory
from sharc.propagation.propagation_factory import PropagationFactory


class SimulationImtValeTest(unittest.TestCase):

    def setUp(self):
        self.our_path = os.path.dirname(__file__)
        self.param = Parameters()
        self.param.set_file_name(os.path.join(self.our_path, "parameters_general_test_imt_vale.ini"))
        self.param.read_params()
        self.param.imt.ue_polygons = [Polygon([(669240, 7803180),
                                               (669240, 7803200),
                                               (669260, 7803200),
                                               (669260, 7803180)]),
                                      Polygon([(671340, 7803200),
                                               (671340, 7803220),
                                               (671360, 7803220),
                                               (671360, 7803200)])]
        self.random_number_gen = np.random.RandomState(seed=101)

        # Test values
        self.bs_antenna_gain = [1, 2]
        self.ue_antenna_gain = [10, 11]
        self.path_loss_matrix = np.array([[91.32490, 142.0268],
                                          [150.8591, 61.05490]])

        self.antenna_again_matrix = np.array([[self.ue_antenna_gain[0] + self.bs_antenna_gain[0],
                                               self.ue_antenna_gain[1] + self.bs_antenna_gain[0]],
                                              [self.ue_antenna_gain[0] + self.bs_antenna_gain[1],
                                               self.ue_antenna_gain[1] + self.bs_antenna_gain[1]]])

        self.expected_coupling_loss = self.path_loss_matrix - self.antenna_again_matrix

    def test_simulation_2bs_2ue_downlink(self):

        self.simulation = SimulationImtValeDownlink(self.param)
        self.simulation.initialize()

        self.simulation.bs_power_gain = 0
        self.simulation.ue_power_gain = 0

        self.simulation.propagation_imt = PropagationFactory.create_propagation(self.param.imt.channel_model,
                                                                                self.param,
                                                                                self.random_number_gen)

        self.simulation.bs = StationFactory.generate_imt_vale_base_stations(self.param.imt,
                                                                            self.param.antenna_imt,
                                                                            self.simulation.topology,
                                                                            self.random_number_gen)

        self.simulation.bs.antenna = np.array([AntennaOmni(self.bs_antenna_gain[0]),
                                               AntennaOmni(self.bs_antenna_gain[1])])

        self.simulation.bs.active = np.ones(2, dtype=bool)

        self.simulation.ue = StationFactory.generate_imt_ue_vale_outdoor(self.param.imt,
                                                                         self.param.antenna_imt,
                                                                         self.random_number_gen,
                                                                         self.simulation.topology)

        # UEs positioned exactly 100m north of the BSs
        self.simulation.ue.x = np.array([669242.9, 671354.38])
        self.simulation.ue.y = np.array([7803199.9, 7803206.72])
        self.simulation.ue.antenna = np.array([AntennaOmni(self.ue_antenna_gain[0]),
                                               AntennaOmni(self.ue_antenna_gain[1])])
        self.simulation.ue.active = np.ones(2, dtype=bool)

        # test connection method
        self.simulation.connect_ue_to_bs(self.param.imt)
        self.assertEqual(self.simulation.link, {0: [0], 1: [1]})

        # We do not test the selection method here because in this specific
        # scenario we do not want to change the order of the UE's
        #self.simulation.select_ue()

        self.simulation.coupling_loss_imt = self.simulation.calculate_coupling_loss(self.simulation.bs,
                                                                                    self.simulation.ue,
                                                                                    self.simulation.propagation_imt)

        npt.assert_allclose(self.simulation.coupling_loss_imt,
                            self.expected_coupling_loss,
                            atol=1e-2)

        # test scheduler and bandwidth allocation
        self.simulation.scheduler()

        # One RB per UE allocated
        bandwidth_per_ue = np.ones(2) * self.simulation.parameters.imt.rb_bandwidth
        npt.assert_allclose(self.simulation.ue.bandwidth, bandwidth_per_ue*np.ones(2), atol=1e-2)

        # there is no power control, so BS's will transmit at maximum power
        self.simulation.power_control()
        tx_power = self.param.imt.bs_conducted_power
        npt.assert_allclose(self.simulation.bs.tx_power[0], np.array(tx_power[0]), atol=1e-2)
        npt.assert_allclose(self.simulation.bs.tx_power[1], np.array(tx_power[1]), atol=1e-2)

        # test method that calculates SINR
        self.simulation.calculate_sinr()

        # check UE received power
        rx_power = np.array([tx_power[0] -
                             self.simulation.parameters.imt.bs_ohmic_loss -
                             self.expected_coupling_loss[0, 0] -
                             self.simulation.parameters.imt.ue_body_loss -
                             self.simulation.parameters.imt.ue_ohmic_loss,
                             tx_power[1] -
                             self.simulation.parameters.imt.bs_ohmic_loss -
                             self.expected_coupling_loss[1, 1] -
                             self.simulation.parameters.imt.ue_body_loss -
                             self.simulation.parameters.imt.ue_ohmic_loss])

        npt.assert_allclose(self.simulation.ue.rx_power, rx_power, atol=1e-2)

        # check UE received interference
        # rx_interference = np.array([tx_power[1]-3-(150.8591-10-2)-4-3,  tx_power[0]-3-(142.0268-11-1)-4-3])
        rx_interference = np.array([tx_power[1] -
                                    self.simulation.parameters.imt.bs_ohmic_loss -
                                    self.expected_coupling_loss[1, 0] -
                                    self.simulation.parameters.imt.ue_body_loss -
                                    self.simulation.parameters.imt.ue_ohmic_loss,
                                    tx_power[0] -
                                    self.simulation.parameters.imt.bs_ohmic_loss -
                                    self.expected_coupling_loss[0, 1] -
                                    self.simulation.parameters.imt.ue_body_loss -
                                    self.simulation.parameters.imt.ue_ohmic_loss])

        npt.assert_allclose(self.simulation.ue.rx_interference, rx_interference, atol=1e-2)

        # check UE thermal noise
        thermal_noise = np.array([10*np.log10(1.38064852e-23*290*bandwidth_per_ue[ue]*1e3*1e6) + 9
                         for ue in range(self.simulation.ue.num_stations)])
        npt.assert_allclose(self.simulation.ue.thermal_noise, thermal_noise, atol=1e-2)

        # check UE thermal noise + interference
        total_interference = 10*np.log10(np.power(10, 0.1*rx_interference) +
                                         np.power(10, 0.1*thermal_noise))
        npt.assert_allclose(self.simulation.ue.total_interference, total_interference, atol=1e-2)

        # check SNR
        npt.assert_allclose(self.simulation.ue.snr, rx_power - thermal_noise, atol=1e-2)

        # check SINR
        npt.assert_allclose(self.simulation.ue.sinr, rx_power - total_interference, atol=1e-2)

    def test_simulation_2bs_2ue_uplink(self):

        self.simulation = SimulationImtValeUplink(self.param)
        self.simulation.initialize()

        self.simulation.bs_power_gain = 0
        self.simulation.ue_power_gain = 0

        self.simulation.bs = StationFactory.generate_imt_vale_base_stations(self.param.imt,
                                                                            self.param.antenna_imt,
                                                                            self.simulation.topology,
                                                                            self.random_number_gen)

        self.simulation.bs.antenna = np.array([AntennaOmni(self.ue_antenna_gain[0]),
                                               AntennaOmni(self.ue_antenna_gain[1])])

        self.simulation.bs.active = np.ones(2, dtype=bool)

        self.simulation.ue = StationFactory.generate_imt_ue_vale_outdoor(self.param.imt,
                                                                         self.param.antenna_imt,
                                                                         self.random_number_gen,
                                                                         self.simulation.topology)

        self.simulation.propagation_imt = PropagationFactory.create_propagation(self.param.imt.channel_model,
                                                                                self.param,
                                                                                self.random_number_gen)

        # UEs positioned exactly 100m north of the BSs
        self.simulation.ue.x = np.array([669242.9, 671354.38])
        self.simulation.ue.y = np.array([7803199.9, 7803206.72])

        self.simulation.ue.antenna = np.array([AntennaOmni(self.bs_antenna_gain[0]),
                                               AntennaOmni(self.bs_antenna_gain[1])])

        self.simulation.ue.active = np.ones(2, dtype=bool)

        # test connection method
        self.simulation.connect_ue_to_bs(self.param.imt)
        self.assertEqual(self.simulation.link, {0: [0], 1: [1]})

        # We do not test the selection method here because in this specific
        # scenario we do not want to change the order of the UE's
        #self.simulation.select_ue()

        self.simulation.coupling_loss_imt = self.simulation.calculate_coupling_loss(self.simulation.bs,
                                                                                    self.simulation.ue,
                                                                                    self.simulation.propagation_imt)
        npt.assert_allclose(self.simulation.coupling_loss_imt,
                            self.expected_coupling_loss,
                            atol=1e-2)

        # test scheduler and bandwidth allocation
        self.simulation.scheduler()

        bandwidth_per_ue = [4.5, 4.5]

        npt.assert_allclose(self.simulation.ue.bandwidth, bandwidth_per_ue, atol=1e-2)

        # there is no power control, so UE's will transmit at maximum power
        self.simulation.power_control()
        tx_power = np.ones(self.simulation.parameters.imt.num_ue) * self.simulation.parameters.imt.ue_p_cmax
        npt.assert_allclose(self.simulation.ue.tx_power, tx_power*np.ones(2))

        # test method that calculates SINR
        self.simulation.calculate_sinr()

        # check BS received power
        rx_power = np.array([tx_power[0] -
                             self.simulation.parameters.imt.bs_ohmic_loss -
                             self.expected_coupling_loss[0, 0] -
                             self.simulation.parameters.imt.ue_body_loss -
                             self.simulation.parameters.imt.ue_ohmic_loss,
                             tx_power[1] -
                             self.simulation.parameters.imt.bs_ohmic_loss -
                             self.expected_coupling_loss[1, 1] -
                             self.simulation.parameters.imt.ue_body_loss -
                             self.simulation.parameters.imt.ue_ohmic_loss])

        npt.assert_allclose(self.simulation.bs.rx_power[0], rx_power[0], atol=1e-2)
        npt.assert_allclose(self.simulation.bs.rx_power[1], rx_power[1], atol=1e-2)

        # # check BS received interference
        rx_interference = np.array([tx_power[0] -
                                    self.simulation.parameters.imt.bs_ohmic_loss -
                                    self.expected_coupling_loss[0, 1] -
                                    self.simulation.parameters.imt.ue_body_loss -
                                    self.simulation.parameters.imt.ue_ohmic_loss,
                                    tx_power[1] -
                                    self.simulation.parameters.imt.bs_ohmic_loss -
                                    self.expected_coupling_loss[1, 0] -
                                    self.simulation.parameters.imt.ue_body_loss -
                                    self.simulation.parameters.imt.ue_ohmic_loss])

        npt.assert_allclose(self.simulation.bs.rx_interference[0], rx_interference[0], atol=1e-2)
        npt.assert_allclose(self.simulation.bs.rx_interference[1], rx_interference[1], atol=1e-2)

        # check BS thermal noise
        thermal_noise = [10*np.log10(self.simulation.parameters.imt.BOLTZMANN_CONSTANT *
                                     self.simulation.parameters.imt.noise_temperature*1e3) +
                         10*np.log10(self.simulation.ue.bandwidth[ue]*1e6) +
                         self.simulation.bs.noise_figure[0]
                         for ue in range(self.simulation.ue.num_stations)]

        npt.assert_allclose(self.simulation.bs.thermal_noise[0], thermal_noise[0], atol=1e-2)
        npt.assert_allclose(self.simulation.bs.thermal_noise[1], thermal_noise[1], atol=1e-2)

        # check BS thermal noise + interference
        total_interference = np.array(
            [10*np.log10(np.power(10, 0.1*rx_interference[0]) +
                         np.power(10, 0.1*thermal_noise[0])),
                         10*np.log10(np.power(10, 0.1*rx_interference[1]) +
                                     np.power(10, 0.1*thermal_noise[1]))])

        npt.assert_allclose(self.simulation.bs.total_interference[0], total_interference[0], atol=1e-2)
        npt.assert_allclose(self.simulation.bs.total_interference[1], total_interference[1], atol=1e-2)

        # check SNR
        npt.assert_allclose(self.simulation.bs.snr[0], rx_power[0] - thermal_noise[0], atol=1e-2)
        npt.assert_allclose(self.simulation.bs.snr[1], rx_power[1] - thermal_noise[1], atol=1e-2)

        # check SINR
        npt.assert_allclose(self.simulation.bs.sinr[0], rx_power[0] - total_interference[0], atol=1e-2)
        npt.assert_allclose(self.simulation.bs.sinr[1], rx_power[1] - total_interference[1], atol=1e-2)


if __name__ == '__main__':
    unittest.main()
