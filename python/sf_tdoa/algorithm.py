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

import numpy as np
import scipy.constants as scc
from scipy.spatial.distance import pdist

from smile.frames import Frames
from smile.nodes import Nodes
from smile.results import Results


# Algorithm based on:
# S. Van Doan and J. Vesely, "The effectivity comparison of TDOA analytical solution methods,"
# 2015 16th International Radar Symposium (IRS), Dresden, 2015, pp. 800-805.
def _tdoa_analytical(coordinates, distances):
    """
    S. Van Doan and J. Vesely, "The effectivity comparison of TDOA analytical solution methods,"
    2015 16th International Radar Symposium (IRS), Dresden, 2015, pp. 800-805.
    """
    L = distances[1]
    R = distances[2]
    Xl = coordinates[1, 0] - coordinates[0, 0]
    Yl = coordinates[1, 1] - coordinates[0, 1]
    Xr = coordinates[2, 0] - coordinates[0, 0]
    Yr = coordinates[2, 1] - coordinates[0, 1]

    A = -2 * np.asanyarray(((Xl, Yl),
                            (Xr, Yr)))

    B = np.asanyarray(((-2 * L, L ** 2 - Xl ** 2 - Yl ** 2),
                       (2 * R, R ** 2 - Xr ** 2 - Yr ** 2)))

    tmp, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
    a = tmp[0, 0] ** 2 + tmp[1, 0] ** 2 - 1
    b = 2 * (tmp[0, 0] * tmp[0, 1] + tmp[1, 0] * tmp[1, 1])
    c = tmp[0, 1] ** 2 + tmp[1, 1] ** 2

    K = np.max(np.real(np.roots((a, b, c))))

    X = tmp[0, 0] * K + tmp[0, 1] + coordinates[0, 0]
    Y = tmp[1, 0] * K + tmp[1, 1] + coordinates[0, 1]

    return np.asarray((X, Y))


def localize_mobile(anchors, beacons, tx_delay):
    """
    Process SF-TDoA simulation data for given mobile node.
    :param anchors: Simulation anchors (smile.nodes.Nodes)
    :param beacons: Beacons transmitted/received by given mobile node (smile.frames.Frames)
    :param tx_delay: Processing time on anchors (int, expressed in ms)
    :return: Array, where each row holds: approximated position (X, Y, Z), true position at the beginning of
             localization round (X, Y, Z) and true position at the end of localization round (X, Y, Z)
    """
    tx_delay = tx_delay * 1e+9  # ms -> ps

    # Filter out all sequence numbers for which mobile node received less than three beacons
    sequence_numbers, sequence_number_counts = np.unique(beacons[:, Frames.SEQUENCE_NUMBER], return_counts=True)
    sequence_numbers = sequence_numbers[sequence_number_counts > 3]

    result = Results.create_array(sequence_numbers.size, position_dimensions=2)

    for i in range(sequence_numbers.size):
        sequence_number = sequence_numbers[i]

        # Extract beacons with specific sequence number
        current_beacons = beacons[np.where(beacons[:, Frames.SEQUENCE_NUMBER] == sequence_number)]

        # Compute distances between anchor pairs (first, second) and (second, third)
        anchor_distances = np.zeros(2)
        anchor_distances[0] = pdist(anchors[0:2, Nodes.POSITION_2D], 'euclidean')[0]
        anchor_distances[1] = pdist(anchors[1:3, Nodes.POSITION_2D], 'euclidean')[0]

        assert (scc.unit('speed of light in vacuum') == 'm s^-1')
        c = scc.value('speed of light in vacuum')
        c = c * 1e-12  # m/s -> m/ps

        # Compute ToF between anchor pairs
        anchor_tx_delays = anchor_distances / c + tx_delay

        # Follow algorithm steps
        anchor_coordinates = np.zeros((3, 2))
        anchor_coordinates[0] = anchors[1, Nodes.POSITION_2D]
        anchor_coordinates[1] = anchors[0, Nodes.POSITION_2D]
        anchor_coordinates[2] = anchors[2, Nodes.POSITION_2D]

        timestamps = np.full(3, float('nan'))
        timestamps[1] = current_beacons[1, Frames.BEGIN_CLOCK_TIMESTAMP] - current_beacons[
            0, Frames.BEGIN_CLOCK_TIMESTAMP] - anchor_tx_delays[0]
        timestamps[2] = current_beacons[2, Frames.BEGIN_CLOCK_TIMESTAMP] - current_beacons[
            1, Frames.BEGIN_CLOCK_TIMESTAMP] - anchor_tx_delays[1]

        distances = timestamps * c

        result[i, Results.POSITION_2D] = _tdoa_analytical(anchor_coordinates, distances)
        result[i, Results.BEGIN_TRUE_POSITION_3D] = current_beacons[0, Frames.BEGIN_TRUE_POSITION_3D]
        result[i, Results.END_TRUE_POSITION_3D] = current_beacons[2, Frames.END_TRUE_POSITION_3D]

    return result
