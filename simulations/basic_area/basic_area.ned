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

package smile.algorithm.sf_tdoa.simulations.basic_area;

import smile.simulations.basic_area.stationary_mobiles_grid;
import smile.Logger;

network basic_area extends stationary_mobiles_grid
{
    submodules:
        anchorsLog: Logger {            
            @display("p=102,188");
        };

        mobilesLog: Logger {            
            @display("p=142,188");
        };

        mobileFramesLog: Logger {            
            @display("p=182,188");
        };
}