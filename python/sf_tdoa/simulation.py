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

import importlib
import itertools
import os.path

import numpy as np
import scipy.constants as scc

import smile.algorithms.common as common
import smile.area as sarea
import smile.simulation as ss
from sf_tdoa.anchors import Anchors
from smile.filter import Filter
from smile.frames import Frames
from smile.nodes import Nodes
from smile.results import Results


class Simulation(ss.Simulation):
    def __init__(self, configuration):
        self._configuration = configuration
        self.solver_configuration = self._configuration['algorithms']['tdoa']['solver']

        solver_module = importlib.import_module(self.solver_configuration['module'])
        self._Solver = getattr(solver_module, self.solver_configuration['class'])

        area_configuration = self._configuration['area']
        area_file_path = area_configuration['file']
        self._area = sarea.Area(area_file_path)

    def run_offline(self, directory_path):
        directory_path = os.path.expanduser(directory_path)

        anchors = Anchors.load_csv(os.path.join(directory_path, 'sf_tdoa_anchors.csv'))
        mobiles = Nodes.load_csv(os.path.join(directory_path, 'sf_tdoa_mobiles.csv'))
        frames = Frames.load_csv(os.path.join(directory_path, 'sf_tdoa_mobile_frames.csv'))

        results = None
        for mobile_node in mobiles:
            mobile_results = self._localize_mobile(mobile_node, anchors, frames)
            if results is None:
                results = mobile_results
            else:
                results = Results(np.concatenate((results, mobile_results), axis=0))

        nan_results = np.where(np.isnan(results["position_2d"]).all(axis=1))
        nan_results_count = len(nan_results[0])

        print('Success localizations: {0} / {1}'.format(len(results) - nan_results_count, len(results)))

        return results, anchors

    def _localize_mobile(self, mobile_node, anchors, frames):
        # Assume that all anchors has the same reply delay
        reply_delay = np.unique(anchors["beacon_reply_delay"])
        assert (reply_delay.shape == (1,))
        reply_delay = reply_delay[0]

        assert (scc.unit('speed of light in vacuum') == 'm s^-1')
        c = scc.value('speed of light in vacuum')
        c = c * 1e-12  # m/s -> m/ps

        frame_filer = Filter()
        frame_filer.equal("node_mac_address", mobile_node["mac_address"])
        mobile_frames = frame_filer.execute(frames)

        # Filter out all sequence numbers for which mobile node received less than three beacons
        sequence_numbers, sequence_number_counts = np.unique(mobile_frames["sequence_number"], return_counts=True)
        sequence_numbers = sequence_numbers[sequence_number_counts >= 3]

        result = Results.create_array(sequence_numbers.size, position_dimensions=2)
        result["mac_address"] = mobile_node["mac_address"]

        for i in range(sequence_numbers.size):
            sequence_number = sequence_numbers[i]
            current_positions = []

            # Extract beacons with specific sequence number
            current_beacons = mobile_frames[np.where(mobile_frames["sequence_number"] == sequence_number)]

            # Set true position
            true_begin_position = current_beacons[0, "begin_true_position_3d"]
            true_end_position = current_beacons[0, "end_true_position_3d"]
            result[i, "begin_true_position_3d"] = true_begin_position
            result[i, "end_true_position_3d"] = true_end_position

            # Evaluate different anchors sets
            anchor_groups = [(0, 1, 2)]
            for anchor_indices in anchor_groups:

                # Compute distances between consecutive pairs of anchors (first, second), (second, third) etc.
                anchors_gaps = []
                for anchor_index in itertools.islice(anchor_indices, len(anchor_indices) - 1):
                    gap = np.linalg.norm(
                        anchors[(anchor_index + 1), "position_2d"] - anchors[anchor_index, "position_2d"])
                    anchors_gaps.append(gap)

                # Compute ToF between anchor pairs
                anchors_gaps = np.asarray(anchors_gaps)
                anchors_gaps = (anchors_gaps / c) + reply_delay

                # Follow algorithm steps
                anchor_coordinates = np.zeros((3, 2))
                anchor_coordinates[0] = anchors[anchor_indices[0], "position_2d"]
                anchor_coordinates[1] = anchors[anchor_indices[1], "position_2d"]
                anchor_coordinates[2] = anchors[anchor_indices[2], "position_2d"]

                timestamps = np.zeros(3)
                timestamps[0] = current_beacons[anchor_indices[0], "begin_clock_timestamp"]
                timestamps[1] = current_beacons[anchor_indices[1], "begin_clock_timestamp"]
                timestamps[2] = current_beacons[anchor_indices[2], "begin_clock_timestamp"]

                timestamps[1] -= anchors_gaps[0]
                timestamps[2] -= (anchors_gaps[0] + anchors_gaps[1])

                sorted_anchors_coordinates, sorted_timestamps = common.sort_measurements(anchor_coordinates, timestamps)

                # Compute TDoA values
                sorted_tdoa_distances = (sorted_timestamps - sorted_timestamps[0]) * c

                # Compute position
                try:
                    solver = self._Solver(sorted_anchors_coordinates, sorted_tdoa_distances, self.solver_configuration)
                    positions = solver.localize()

                    # Choose better position
                    positions = [position for position in positions if self._area.contains(position)]
                    if positions:
                        current_positions += positions
                    else:
                        current_positions.append((np.nan, np.nan))
                except ValueError:
                    current_positions.append((np.nan, np.nan))

            result[i, "position_2d"] = current_positions[0]

        return result
