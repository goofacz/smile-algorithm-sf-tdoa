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


def localize_mobile(anchors, beacons):
    max_sequence_number = numpy.max(beacons['sequence_number'])

    for sequence_number in range(1, max_sequence_number):
        current_beacons = numpy.extract(beacons['sequence_number'] == sequence_number, beacons)
        if numpy.size(current_beacons) < 3:
            pass

        

