//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
// 

package smile.algorithm.sf_tdoa.simulations;

import smile.RadioNode;
import smile.Logger;
import smile.IdealClock;
import smile.IdealRangingNicDriver;
import smile.algorithm.sf_tdoa.MobileApplication;
import smile.algorithm.sf_tdoa.AnchorApplication;
import inet.mobility.single.LinearMobility;
import inet.physicallayer.idealradio.IdealRadioMedium;
import inet.visualizer.integrated.IntegratedCanvasVisualizer;

network single_stationary_mobile_node
{
    submodules:
        radioMedium: IdealRadioMedium {
            @display("p=148,40");
        }

        visualizer: IntegratedCanvasVisualizer {
            @display("p=225,38");
        }

        logger: Logger {
            @display("p=69,30");
            fileNamePrefix = "ss_twr";
            overwrite = true;
        }

        mobileNode: RadioNode {
            @display("p=108,187");
            mobilityType = "LinearMobility";
            applicationType = "MobileApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }

        anchorNode1: RadioNode {
            @display("p=89,132");
            mobilityType = "LinearMobility";
            applicationType = "AnchorApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }

        anchorNode2: RadioNode {
            @display("p=194,132");
            mobilityType = "LinearMobility";
            applicationType = "AnchorApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }

        anchorNode3: RadioNode {
            @display("p=194,245");
            mobilityType = "LinearMobility";
            applicationType = "AnchorApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }

        anchorNode4: RadioNode {
            @display("p=89,245");
            mobilityType = "LinearMobility";
            applicationType = "AnchorApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }
}
