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

from os import path
from smile.nodes import Nodes
from smile.frames import Frames
from smile.helpers import mac_address_to_string


def load_nodes(directory_path):
    """
    Loads anchors and mobile nodes for given simulation.
    :param directory_path: Path to directory holding simulation's CSV files with describing anchors and mobile nodes
    :return: Tuple of two smile.nodes.Nodes instances holding anchors and mobile nodes respectively.
    """
    anchors_file_path = path.join(directory_path, 'sf_tdoa_anchors.csv')
    mobiles_file_path = path.join(directory_path, 'sf_tdoa_mobiles.csv')
    return Nodes.load_csv(anchors_file_path), Nodes.load_csv(mobiles_file_path)


def load_mobiles_beacons(directory_path):
    """
    Loads beacons received/transmitted by all mobile nodes.
    :param directory_path: Path to directory holding simulation CSV files
    :return: instance of smile.frames.Frame
    """
    file_path = path.join(directory_path, 'sf_tdoa_mobiles_beacons.csv')
    return Frames.load_csv(file_path)
