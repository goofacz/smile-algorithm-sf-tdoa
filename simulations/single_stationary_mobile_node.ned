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
import inet.networklayer.configurator.generic.GenericNetworkConfigurator;

network single_stationary_mobile_node
{
    parameters:
        @display("bgb=413,294");
        int mobilesNumber = default(0);

    submodules:
        radioMedium: IdealRadioMedium {
            @display("p=226,40");
        }

        visualizer: IntegratedCanvasVisualizer {
            @display("p=303,38");
        }

        configurator: GenericNetworkConfigurator {
            @display("p=69,38");
        }

        logger: Logger {
            @display("p=147,30");
            fileNamePrefix = "sf_tdoa";
            overwrite = true;
        }

        mobileNodes[mobilesNumber]: RadioNode {
            mobilityType = "StaticGridMobility";
            applicationType = "MobileApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }

        anchorNode1: RadioNode {
            @display("p=100,100");
            mobilityType = "LinearMobility";
            applicationType = "AnchorApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }

        anchorNode2: RadioNode {
            @display("p=175,100");
            mobilityType = "LinearMobility";
            applicationType = "AnchorApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }

        anchorNode3: RadioNode {
            @display("p=175,175");
            mobilityType = "LinearMobility";
            applicationType = "AnchorApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }

        anchorNode4: RadioNode {
            @display("p=100,175");
            mobilityType = "LinearMobility";
            applicationType = "AnchorApplication";
            nicDriverType = "IdealRangingNicDriver";
            nicType = "IdealWirelessNic";
            clockType = "IdealClock";
        }
}
