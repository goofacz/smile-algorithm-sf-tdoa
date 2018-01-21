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

import numpy
import scipy.constants
from scipy.spatial.distance import pdist
from smile.results import Results
from smile.helpers import PositionDimensions


# Algorithm based on:
# S. Van Doan and J. Vesely, "The effectivity comparison of TDOA analytical solution methods,"
# 2015 16th International Radar Symposium (IRS), Dresden, 2015, pp. 800-805.
def _tdoa_analytical(coordinates, distances):
    L = distances[1]
    R = distances[2]
    Xl = coordinates[1, 0] - coordinates[0, 0]
    Yl = coordinates[1, 1] - coordinates[0, 1]
    Xr = coordinates[2, 0] - coordinates[0, 0]
    Yr = coordinates[2, 1] - coordinates[0, 1]

    A = -2 * numpy.asanyarray(((Xl, Yl),
                               (Xr, Yr)))

    B = numpy.asanyarray(((-2 * L, L ** 2 - Xl ** 2 - Yl ** 2),
                          (2 * R, R ** 2 - Xr ** 2 - Yr ** 2)))

    tmp, _, _, _ = numpy.linalg.lstsq(A, B)
    a = tmp[0, 0] ** 2 + tmp[1, 0] ** 2 - 1
    b = 2 * (tmp[0, 0] * tmp[0, 1] + tmp[1, 0] * tmp[1, 1])
    c = tmp[0, 1] ** 2 + tmp[1, 1] ** 2

    K = numpy.max(numpy.real(numpy.roots((a, b, c))))

    X = tmp[0, 0] * K + tmp[0, 1] + coordinates[0, 0]
    Y = tmp[1, 0] * K + tmp[1, 1] + coordinates[0, 1]

    return numpy.asarray((X, Y))


def localize_mobile(anchors, beacons, tx_delay):
    tx_delay = tx_delay * 1e+9  # ms -> ps

    # Filter out all sequence numbers for which mobile node received less than three beacons
    sequence_numbers, sequence_number_counts = numpy.unique(beacons.sequence_numbers, return_counts=True)
    sequence_numbers = sequence_numbers[sequence_number_counts > 3]

    result = Results(PositionDimensions.TWO_D, sequence_numbers.size)

    for i in range(sequence_numbers.size):
        sequence_number = sequence_numbers[i]

        # Extract beacons with specific sequence number
        current_beacons = beacons[numpy.where(beacons.sequence_numbers == sequence_number)]

        # Compute distances between anchor pairs (first, second) and (second, third)
        anchor_distances = numpy.zeros(2)
        anchor_distances[0] = pdist(anchors.positions[0:2, 0:2], 'euclidean')[0]
        anchor_distances[1] = pdist(anchors.positions[1:3, 0:2], 'euclidean')[0]

        assert (scipy.constants.unit('speed of light in vacuum') == 'm s^-1')
        c = scipy.constants.value('speed of light in vacuum')
        c = c * 1e-12  # m/s -> m/ps

        # Compute ToF between anchor pairs
        anchor_tx_delays = anchor_distances / c + tx_delay

        # Follow algorithm steps
        anchor_coordinates = numpy.zeros((3, 2))
        anchor_coordinates[0] = anchors.positions[1, (0, 1)]
        anchor_coordinates[1] = anchors.positions[0, (0, 1)]
        anchor_coordinates[2] = anchors.positions[2, (0, 1)]

        timestamps = numpy.full(3, float('nan'))
        timestamps[1] = current_beacons.begin_timestamps[1, 0] - current_beacons.begin_timestamps[0, 0] - anchor_tx_delays[0]
        timestamps[2] = current_beacons.begin_timestamps[2, 0] - current_beacons.begin_timestamps[1, 0] - anchor_tx_delays[1]

        distances = timestamps * c

        result.position[i] = (*_tdoa_analytical(anchor_coordinates, distances), 0)
        result.begin_true_position[i] = current_beacons.begin_positions[0]
        result.end_true_position[i] = current_beacons.end_positions[2]

    return result
