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
from scipy.spatial.distance import pdist
from scipy.constants import physical_constants


def _tdoa_analytical(coordinates, timestamps):
    L = timestamps[1]
    R = timestamps[2]
    Xl = coordinates[1, 0] - coordinates[0, 0]
    Yl = coordinates[1, 1] - coordinates[0, 1]
    Xr = coordinates[2, 0] - coordinates[0, 0]
    Yr = coordinates[2, 1] - coordinates[0, 1]

    A = -2 * numpy.asanyarray(((Xl, Yl),
                               (Xr, Yr)))

    B = numpy.asanyarray(((-2 * L, numpy.power(L, 2) - numpy.power(Xl, 2) - numpy.power(Yl, 2)),
                           (2 * R, numpy.power(R, 2) - numpy.power(Xr, 2) - numpy.power(Yr, 2))))

    tmp, _, _, _ = numpy.linalg.lstsq(A, B)
    a = numpy.power(tmp[0,0], 2) + numpy.power(tmp[1,0], 2) - 1
    b = 2 * (tmp[0,0] * tmp[0,1] + tmp[1,0] * tmp[1,1])
    c = numpy.power(tmp[0,1], 2) + numpy.power(tmp[1,1], 2)

    K = numpy.max(numpy.real(numpy.roots((a, b, c))))

    X = tmp[0,0] * K + tmp[0,1] + coordinates[0,0]
    Y = tmp[1,0] * K + tmp[1,1] + coordinates[0,1]

    return numpy.asarray((X, Y))


def localize_mobile(anchors, beacons, tx_delay):
    sequence_numbers = numpy.unique(beacons.sequence_numbers)

    for sequence_number in sequence_numbers:
        current_beacons = beacons[numpy.where(beacons.sequence_numbers == sequence_number)]
        if numpy.size(current_beacons.sequence_numbers) < 3:
            print("Only {0} beacons with sequence number {1} were received, skipping".format(
                numpy.size(current_beacons), sequence_number))

        anchor_distances = numpy.zeros(2)
        anchor_distances[0] = pdist(anchors.positions[0:2, 0:2], 'euclidean')[0]
        anchor_distances[1] = pdist(anchors.positions[1:3, 0:2], 'euclidean')[0]

        #c = physical_constants['speed of light in vacuum'][0]
        c = 0.000299792458
        anchor_tx_delays = anchor_distances / c + tx_delay

        anchor_coordinates = numpy.zeros((3, 2))
        anchor_coordinates[0] = anchors.positions[1, (0, 1)]
        anchor_coordinates[1] = anchors.positions[0, (0, 1)]
        anchor_coordinates[2] = anchors.positions[2, (0, 1)]

        timestamps = numpy.array((float('nan'),
                                 current_beacons.begin_timestamps[1,0] - current_beacons.begin_timestamps[0,0] - anchor_tx_delays[0],
                                 current_beacons.begin_timestamps[2,0] - current_beacons.begin_timestamps[1,0] - anchor_tx_delays[1]))

        timestamps = timestamps * c

        positions = _tdoa_analytical(anchor_coordinates, timestamps)
        positions = positions * c
        pass

