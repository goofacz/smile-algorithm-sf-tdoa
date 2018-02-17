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

import smile.algorithms.tdoa as tdoa
from smile.results import Results


def localize_mobile(anchors, beacons):
    # Assume that all anchors has the same reply delay
    reply_delay = np.unique(anchors["beacon_reply_delay"])
    assert (reply_delay.shape == (1,))
    reply_delay = reply_delay[0]

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
            anchor_tx_delays = anchor_distances / c + reply_delay

            # Follow algorithm steps
            anchor_coordinates = np.zeros((3, 2))
            anchor_coordinates[0] = anchors[anchor_triple[1], "position_2d"]
            anchor_coordinates[1] = anchors[anchor_triple[0], "position_2d"]
            anchor_coordinates[2] = anchors[anchor_triple[2], "position_2d"]

            timestamp_differences = np.full(3, float('nan'))
            timestamp_differences[1] = current_beacons[anchor_triple[1], "begin_clock_timestamp"] - \
                                       current_beacons[anchor_triple[0], "begin_clock_timestamp"] - anchor_tx_delays[0]
            timestamp_differences[2] = current_beacons[anchor_triple[2], "begin_clock_timestamp"] - \
                                       current_beacons[anchor_triple[1], "begin_clock_timestamp"] - anchor_tx_delays[1]

            # Compute position
            position = tdoa.doan_vesely(anchor_coordinates, timestamp_differences)

            positions.append(position)
            result[i, "begin_true_position_3d"] = current_beacons[0, "begin_true_position_3d"]
            result[i, "end_true_position_3d"] = current_beacons[2, "end_true_position_3d"]

        # Choose better position
        # TODO Propose better solution, for now just choose position being closer to (0, 0)
        if np.abs(np.linalg.norm((0, 0) - positions[0])) < np.abs(np.linalg.norm((0, 0) - positions[1])):
            result[i, "position_2d"] = positions[0]
        else:
            result[i, "position_2d"] = positions[1]

    return result
