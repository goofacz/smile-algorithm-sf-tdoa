#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see http:#www.gnu.org/licenses/.
#

import argparse
import numpy as np
import sf_tdoa.simulation as simulation
import sf_tdoa.algorithm as algorithm
import smile.analysis as sa
from smile.nodes import Nodes
from smile.frames import Frames
from smile.results import Results

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process SF-TDoA ranging data.')
    parser.add_argument('logs_directory_path', type=str, nargs=1, help='Path to directory holding CSV logs')
    parser.add_argument('anchor_processing_time', type=int, nargs=1, help='Processing delay on anchors [ms]')
    arguments = parser.parse_args()
    logs_directory_path = arguments.logs_directory_path[0]
    anchor_processing_time = arguments.anchor_processing_time[0]

    anchors, mobiles = simulation.load_nodes(logs_directory_path)
    mobiles_beacons = simulation.load_mobiles_beacons(logs_directory_path)
    simulation_results = None
    for mobile_address in mobiles[:, Nodes.MAC_ADDRESS]:
        beacons = mobiles_beacons[mobiles_beacons[:, Frames.NODE_MAC_ADDRESS] == mobile_address]
        mobile_results = algorithm.localize_mobile(anchors, beacons, tx_delay=anchor_processing_time)
        mobile_results[:, Results.MAC_ADDRESS] = mobile_address

        if simulation_results is None:
            simulation_results = mobile_results
        else:
            simulation_results = np.append(simulation_results, mobile_results, axis=0)

    unique_results = sa.obtain_unique_results(simulation_results)
    sa.absolute_position_error_surface(unique_results)
    sa.absolute_position_error_histogram(unique_results)