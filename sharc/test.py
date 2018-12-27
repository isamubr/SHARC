from sharc.propagation.propagation import Propagation

import math
import numpy as np
from sharc.propagation.propagation_free_space import PropagationFreeSpace
from sharc.propagation.propagation_clutter_loss import PropagationClutterLoss
from sharc.propagation.propagation_building_entry_loss import PropagationBuildingEntryLoss
from sharc.propagation.atmosphere import ReferenceAtmosphere
from sharc.support.enumerations import StationType
from sharc.propagation.scintillation import Scintillation
from sharc.propagation.propagation_p619 import PropagationP619
import random

if __name__ == '__main__':
    from sharc.parameters.parameters import Parameters
    import matplotlib.pyplot as plt
    import os

    params = Parameters()


    sharc_path = os.getcwd()
    param_file = os.path.join(sharc_path, "parameters", "parameters_general.ini")

    params.set_file_name(param_file)
    params.read_params()

    sat_params = params.fss_ss

    seed = 101
    random.seed(seed)
    secondary_seed = random.randint(1, 2**32 - 1)
    random_number_gen = np.random.RandomState(seed=secondary_seed)

    propagation = PropagationP619(random_number_gen)

    ##########################
    # Plot atmospheric loss
    # compare with benchmark from ITU-R P-619 Fig. 3
    frequency_MHz = 30000.
    sat_params.imt_altitude = 1000

    apparent_elevation = range(-1, 90, 2)

    loss_2_5 = np.zeros(len(apparent_elevation))
    loss_12_5 = np.zeros(len(apparent_elevation))

    print("Plotting atmospheric loss:")
    for index in range(len(apparent_elevation)):
        print("\tApparent Elevation: {} degrees".format(apparent_elevation[index]))

        surf_water_vapour_density = 2.5
        loss_2_5[index] = propagation._get_atmospheric_gasses_loss(frequency_MHz=frequency_MHz,
                                                                   apparent_elevation=apparent_elevation[index],
                                                                   sat_params=sat_params,
                                                                   surf_water_vapour_density=surf_water_vapour_density)
        surf_water_vapour_density = 12.5
        loss_12_5[index] = propagation._get_atmospheric_gasses_loss(frequency_MHz=frequency_MHz,
                                                                    apparent_elevation=apparent_elevation[index],
                                                                    sat_params=sat_params,
                                                                    surf_water_vapour_density=surf_water_vapour_density)

    plt.figure()
    plt.semilogy(apparent_elevation, loss_2_5, label='2.5 g/m^3')
    plt.semilogy(apparent_elevation, loss_12_5, label='12.5 g/m^3')

    plt.grid(True)


    plt.xlabel("apparent elevation (deg)")
    plt.ylabel("Loss (dB)")
    plt.title("Atmospheric Gasses Attenuation")
    plt.legend()

    altitude_vec = np.arange(0, 6.1, .5) * 1000
    elevation_vec = np.array([0, .5, 1, 2, 3, 5])
    attenuation = np.empty([len(altitude_vec), len(elevation_vec)])

    #################################
    # Plot beam spreading attenuation
    # compare with benchmark from ITU-R P-619 Fig. 7

    earth_to_space = False
    print("Plotting beam spreading attenuation:")

    plt.figure()
    for index in range(len(altitude_vec)):
        attenuation[index, :] = propagation._get_beam_spreading_att(elevation_vec,
                                                                    altitude_vec[index],
                                                                    earth_to_space)

    handles = plt.plot(altitude_vec / 1000, np.abs(attenuation))
    plt.xlabel("altitude (km)")
    plt.ylabel("Attenuation (dB)")
    plt.title("Beam Spreading Attenuation")

    for line_handle, elevation in zip(handles, elevation_vec):
        line_handle.set_label("{}deg".format(elevation))

    plt.legend(title="Elevation")

    plt.grid(True)


    plt.show()
