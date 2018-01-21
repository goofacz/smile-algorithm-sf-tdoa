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
import sf_tdoa.simulation as simulation
import sf_tdoa.algorithm as algorithm

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process SF-TDoA ranging data.')
    parser.add_argument('logs_directory_path', type=str, nargs=1, help='Path to directory holding CSV logs')
    parser.add_argument('anchor_processing_time', type=int, nargs=1, help='Processing delay on anchors [ms]')
    arguments = parser.parse_args()
    logs_directory_path = arguments.logs_directory_path[0]
    anchor_processing_time = arguments.anchor_processing_time[0]

    anchors, mobiles = simulation.load_nodes(logs_directory_path)
    for mobile_address in mobiles.mac_addresses:
        beacons = simulation.load_beacons(logs_directory_path, mobile_address)
        positions = algorithm.localize_mobile(anchors, beacons, tx_delay=anchor_processing_time)
        pass