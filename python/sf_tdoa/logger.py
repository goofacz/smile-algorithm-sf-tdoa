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

import os.path
import smile.csv_reader as csv_reader


def __compose_path(directory_path, prefix, suffix):
    return os.path.join(directory_path, '{0}{1}'.format(prefix, suffix))


def load_nodes(directory_path, file_name_prefix='sf_tdoa_'):
    anchors_file_path = __compose_path(directory_path, file_name_prefix, 'anchors.csv')
    mobiles_file_path = __compose_path(directory_path, file_name_prefix, 'mobiles.csv')
    return csv_reader.load_anchors(anchors_file_path), csv_reader.load_mobiles(mobiles_file_path)


def load_beacons(directory_path, mac_address):
    beacons_file_path = __compose_path(directory_path, "sf_tdoa_mobile_", '{0}.csv'.format(str(mac_address)))
    return csv_reader.load_frames(beacons_file_path)
