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
    assert (scc.unit('speed of light in vacuum') == 'm s^-1')
    c = scc.value('speed of light in vacuum')
    c = c * 1e-12  # m/s -> m/ps

    # Filter out all sequence numbers for which mobile node received less than three beacons
    sequence_numbers, sequence_number_counts = np.unique(beacons["sequence_number"], return_counts=True)
    sequence_numbers = sequence_numbers[sequence_number_counts > 3]

    result = Results.create_array(sequence_numbers.size, position_dimensions=2)

    anchor_triples = ((0, 1, 2), (1, 2, 3))
    for i in range(sequence_numbers.size):
        sequence_number = sequence_numbers[i]

        # Extract beacons with specific sequence number
        current_beacons = beacons[np.where(beacons["sequence_number"] == sequence_number)]
        positions = []

        # Evaluate different anchors sets
        for anchor_triple in anchor_triples:
            # Compute distances between anchor pairs (first, second) and (second, third)
            anchor_distances = np.zeros(2)
            anchor_distances[0] = np.abs(np.linalg.norm(anchors[anchor_triple[1], "position_2d"] -
                                                        anchors[anchor_triple[0], "position_2d"]))
            anchor_distances[1] = np.abs(np.linalg.norm(anchors[anchor_triple[2], "position_2d"] -
                                                        anchors[anchor_triple[1], "position_2d"]))

            # Compute ToF between anchor pairs
            anchor_tx_delays = anchor_distances / c + tx_delay

            # Follow algorithm steps
            anchor_coordinates = np.zeros((3, 2))
            anchor_coordinates[0] = anchors[anchor_triple[1], "position_2d"]
            anchor_coordinates[1] = anchors[anchor_triple[0], "position_2d"]
            anchor_coordinates[2] = anchors[anchor_triple[2], "position_2d"]

            timestamps = np.full(3, float('nan'))
            timestamps[1] = current_beacons[anchor_triple[1], "begin_clock_timestamp"] - \
                            current_beacons[anchor_triple[0], "begin_clock_timestamp"] - anchor_tx_delays[0]
            timestamps[2] = current_beacons[anchor_triple[2], "begin_clock_timestamp"] - \
                            current_beacons[anchor_triple[1], "begin_clock_timestamp"] - anchor_tx_delays[1]

            distances = timestamps * c

            positions.append(_tdoa_analytical(anchor_coordinates, distances))
            result[i, "begin_true_position_3d"] = current_beacons[0, "begin_true_position_3d"]
            result[i, "end_true_position_3d"] = current_beacons[2, "end_true_position_3d"]

        # Choose better position
        # TODO Propose better solution, for now just choose position being closer to (0, 0)
        if np.abs(np.linalg.norm((0, 0) - positions[0])) < np.abs(np.linalg.norm((0, 0) - positions[1])):
            result[i,"position_2d"] = positions[0]
        else:
            result[i, "position_2d"] = positions[1]

    return result
