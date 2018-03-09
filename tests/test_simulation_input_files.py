# -*- coding: utf-8 -*-
"""
Created on Wed Feb  7 15:28:06 2018

@author: Calil
"""

import unittest
import numpy as np
import numpy.testing as npt
import math

from sharc.simulation_downlink import SimulationDownlink
from sharc.simulation_uplink import SimulationUplink
from sharc.parameters.parameters import Parameters
from sharc.antenna.antenna_omni import AntennaOmni
from sharc.station_factory import StationFactory


class SimulationDownlinkTest(unittest.TestCase):

    def setUp(self):
        self.param = Parameters()
        self.param.set_file_name("parameters_test_input_files.ini")
        self.param.read_params()

    def test_simulation_2bs_2ue_downlink(self):

        self.simulation = SimulationDownlink(self.param)
        self.simulation.initialize()

        self.simulation.bs_power_gain = 0
        self.simulation.ue_power_gain = 0

        self.simulation.bs = StationFactory.generate_imt_base_stations(self.param.imt,
                                                                       self.param.antenna_imt,
                                                                       self.simulation.topology)
        self.simulation.bs.antenna = np.array([AntennaOmni(1), AntennaOmni(2)])
        self.simulation.bs.active = np.ones(2, dtype=bool)

        self.simulation.ue = StationFactory.generate_imt_ue(self.param.imt,
                                                            self.param.antenna_imt,
                                                            self.simulation.topology)
        # UEs positioned exactly 100m north of the BSs
        self.simulation.ue.x = np.array([669242.9, 671354.38])
        self.simulation.ue.y = np.array([7803199.9, 7803206.72])
        self.simulation.ue.antenna = np.array([AntennaOmni(10), AntennaOmni(11)])
        self.simulation.ue.active = np.ones(2, dtype=bool)

        # test connection method
        self.simulation.connect_ue_to_bs()
        self.assertEqual(self.simulation.link, {0: [0], 1: [1]})

        # We do not test the selection method here because in this specific
        # scenario we do not want to change the order of the UE's
        #self.simulation.select_ue()

        self.simulation.coupling_loss_imt = self.simulation.calculate_coupling_loss(self.simulation.bs,
                                                                                    self.simulation.ue,
                                                                                    self.simulation.propagation_imt)
        expected_coupling_loss = np.array([[91.32490-10-1, 142.0268-11-1],
                                           [150.8591-10-2, 61.05490-11-2]])
        npt.assert_allclose(self.simulation.coupling_loss_imt,
                            expected_coupling_loss,
                            atol=1e-2)

        # test scheduler and bandwidth allocation
        self.simulation.scheduler()
        bandwidth_per_ue = math.trunc((1 - 0.1)*100)
        npt.assert_allclose(self.simulation.ue.bandwidth, bandwidth_per_ue*np.ones(2), atol=1e-2)

        # there is no power control, so BS's will transmit at maximum power
        self.simulation.power_control()
        tx_power = 10
        npt.assert_allclose(self.simulation.bs.tx_power[0], np.array([tx_power]), atol=1e-2)
        npt.assert_allclose(self.simulation.bs.tx_power[1], np.array([tx_power]), atol=1e-2)

        # test method that calculates SINR
        self.simulation.calculate_sinr()

        # check UE received power
        rx_power = np.array([tx_power-3-(91.32490-10-1)-4-3, tx_power-3-(61.05490-11-2)-4-3])
        npt.assert_allclose(self.simulation.ue.rx_power, rx_power, atol=1e-2)

        # check UE received interference
        rx_interference = np.array([tx_power-3-(150.8591-10-2)-4-3,  tx_power-3-(142.0268-11-1)-4-3])
        npt.assert_allclose(self.simulation.ue.rx_interference, rx_interference, atol=1e-2)

        # check UE thermal noise
        thermal_noise = 10*np.log10(1.38064852e-23*290*bandwidth_per_ue*1e3*1e6) + 9
        npt.assert_allclose(self.simulation.ue.thermal_noise, thermal_noise, atol=1e-2)

        # check UE thermal noise + interference
        total_interference = 10*np.log10(np.power(10, 0.1*rx_interference) + np.power(10, 0.1*thermal_noise))
        npt.assert_allclose(self.simulation.ue.total_interference, total_interference, atol=1e-2)

        # check SNR
        npt.assert_allclose(self.simulation.ue.snr, rx_power - thermal_noise, atol=1e-2)

        # check SINR
        npt.assert_allclose(self.simulation.ue.sinr, rx_power - total_interference, atol=1e-2)

    def test_simulation_2bs_2ue_uplink(self):

        self.simulation = SimulationUplink(self.param)
        self.simulation.initialize()

        self.simulation.bs_power_gain = 0
        self.simulation.ue_power_gain = 0

        self.simulation.bs = StationFactory.generate_imt_base_stations(self.param.imt,
                                                                       self.param.antenna_imt,
                                                                       self.simulation.topology)
        self.simulation.bs.antenna = np.array([AntennaOmni(1), AntennaOmni(2)])
        self.simulation.bs.active = np.ones(2, dtype=bool)

        self.simulation.ue = StationFactory.generate_imt_ue(self.param.imt,
                                                            self.param.antenna_imt,
                                                            self.simulation.topology)
        # UEs positioned exactly 100m north of the BSs
        self.simulation.ue.x = np.array([669242.9, 671354.38])
        self.simulation.ue.y = np.array([7803199.9, 7803206.72])
        self.simulation.ue.antenna = np.array([AntennaOmni(10), AntennaOmni(11)])
        self.simulation.ue.active = np.ones(2, dtype=bool)

        # test connection method
        self.simulation.connect_ue_to_bs()
        self.assertEqual(self.simulation.link, {0: [0], 1: [1]})

        # We do not test the selection method here because in this specific
        # scenario we do not want to change the order of the UE's
        #self.simulation.select_ue()

        self.simulation.coupling_loss_imt = self.simulation.calculate_coupling_loss(self.simulation.bs,
                                                                                    self.simulation.ue,
                                                                                    self.simulation.propagation_imt)
        expected_coupling_loss = np.array([[91.32490-10-1, 142.0268-11-1],
                                           [150.8591-10-2, 61.05490-11-2]])
        npt.assert_allclose(self.simulation.coupling_loss_imt,
                            expected_coupling_loss,
                            atol=1e-2)

        # test scheduler and bandwidth allocation
        self.simulation.scheduler()
        bandwidth_per_ue = math.trunc((1 - 0.1)*100)
        npt.assert_allclose(self.simulation.ue.bandwidth, bandwidth_per_ue*np.ones(2), atol=1e-2)

        # there is no power control, so UE's will transmit at maximum power
        self.simulation.power_control()
        tx_power = 20
        npt.assert_allclose(self.simulation.ue.tx_power, tx_power*np.ones(2))

        # test method that calculates SINR
        self.simulation.calculate_sinr()

        # check BS received power
        rx_power = { 0: np.array([tx_power-3-4-3] - expected_coupling_loss[0,0]),
                     1: np.array([tx_power-3-4-3] - expected_coupling_loss[1,1])}
        npt.assert_allclose(self.simulation.bs.rx_power[0],
                            rx_power[0],
                            atol=1e-2)
        npt.assert_allclose(self.simulation.bs.rx_power[1],
                            rx_power[1],
                            atol=1e-2)

        # check BS received interference
        rx_interference = { 0: np.array([tx_power-3-4-3] - expected_coupling_loss[0,1]),
                            1: np.array([tx_power-3-4-3] - expected_coupling_loss[1,0])}

        npt.assert_allclose(self.simulation.bs.rx_interference[0],
                            rx_interference[0],
                            atol=1e-2)
        npt.assert_allclose(self.simulation.bs.rx_interference[1],
                            rx_interference[1],
                            atol=1e-2)

        # check BS thermal noise
        thermal_noise = 10*np.log10(1.38064852e-23*290*bandwidth_per_ue*1e3*1e6) + 7
        npt.assert_allclose(self.simulation.bs.thermal_noise,
                            thermal_noise,
                            atol=1e-2)

        # check BS thermal noise + interference
        total_interference = { 0: 10*np.log10(np.power(10, 0.1*rx_interference[0]) + np.power(10, 0.1*thermal_noise)),
                               1: 10*np.log10(np.power(10, 0.1*rx_interference[1]) + np.power(10, 0.1*thermal_noise))}
        npt.assert_allclose(self.simulation.bs.total_interference[0],
                            total_interference[0],
                            atol=1e-2)
        npt.assert_allclose(self.simulation.bs.total_interference[1],
                            total_interference[1],
                            atol=1e-2)

        # check SNR
        npt.assert_allclose(self.simulation.bs.snr[0],
                            rx_power[0] - thermal_noise,
                            atol=1e-2)
        npt.assert_allclose(self.simulation.bs.snr[1],
                            rx_power[1] - thermal_noise,
                            atol=1e-2)

        # check SINR
        npt.assert_allclose(self.simulation.bs.sinr[0],
                            rx_power[0] - total_interference[0],
                            atol=1e-2)
        npt.assert_allclose(self.simulation.bs.sinr[1],
                            rx_power[1] - total_interference[1],
                            atol=1e-2)


if __name__ == '__main__':
    unittest.main()
