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

import numpy as np

import smile.simulation as ss
from sf_tdoa.algorithm import localize_mobile
from sf_tdoa.anchors import Anchors
from smile.frames import Frames
from smile.nodes import Nodes
from smile.results import Results


class Simulation(ss.Simulation):
    def run_offline(self, configuration, directory_path):
        directory_path = os.path.expanduser(directory_path)

        anchors = Anchors.load_csv(os.path.join(directory_path, 'sf_tdoa_anchors.csv'))
        mobiles = Nodes.load_csv(os.path.join(directory_path, 'sf_tdoa_mobiles.csv'))
        frames = Frames.load_csv(os.path.join(directory_path, 'sf_tdoa_mobile_frames.csv'))

        results = None
        for mobile_node in mobiles:
            mobile_results = localize_mobile(mobile_node, anchors, frames)
            if results is None:
                results = mobile_results
            else:
                results = Results(np.concatenate((results, mobile_results), axis=0))

        nan_results = np.where(np.isnan(results["position_2d"]).all(axis=1))
        nan_results_count = len(nan_results[0])

        print('Success localizations: {0} / {1}'.format(len(results) - nan_results_count, len(results)))

        return results, anchors
