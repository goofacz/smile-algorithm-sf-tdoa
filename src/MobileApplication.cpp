//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
//

#include "MobileApplication.h"
#include <CsvLogger.h>
#include <utilities.h>
#include "BeaconFrame_m.h"

namespace smile {
namespace algorithm {
namespace sf_tdoa {

Define_Module(MobileApplication);

void MobileApplication::initialize(int stage)
{
  IdealApplication::initialize(stage);

  if (stage == inet::INITSTAGE_APPLICATION_LAYER) {
    auto& logger = getLogger();
    const auto handle = logger.obtainHandle("mobiles");
    const auto entry = csv_logger::compose(getMacAddress(), getCurrentTruePosition());
    logger.append(handle, entry);

    std::string handleName{"mobiles_beacons"};
    beaconsLog = logger.obtainHandle(handleName);
  }
}

void MobileApplication::handleIncommingMessage(cMessage* newMessage)
{
  std::unique_ptr<cMessage>{newMessage};
}

void MobileApplication::handleRxCompletionSignal(const smile::IdealRxCompletion& completion)
{
  const auto frame = omnetpp::check_and_cast<const BeaconFrame*>(completion.getFrame());
  const auto entry =
      csv_logger::compose(getMacAddress(), completion, frame->getSequenceNumber());
  auto& logger = getLogger();
  logger.append(beaconsLog, entry);
}

}  // namespace sf_tdoa
}  // namespace algorithm
}  // namespace smile
