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


def localize_mobile(anchors, beacons):
    max_sequence_number = int(numpy.max(beacons.sequence_numbers))

    for sequence_number in range(1, max_sequence_number + 1):
        current_beacons = numpy.extract(beacons.sequence_numbers == sequence_number, beacons.sequence_numbers)
        if numpy.size(current_beacons) < 3:
            print("Only {0} beacons with sequence number {1} were received, skipping".format(
                numpy.size(current_beacons), sequence_number))

        anchor_distances = numpy.asarray((pdist(anchors.positions[0:2, 0:2], 'euclidean'),
                                          pdist(anchors.positions[1:3, 0:2], 'euclidean')))
        pass
