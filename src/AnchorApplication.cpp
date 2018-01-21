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

#include "AnchorApplication.h"
#include <CsvLogger.h>
#include <utilities.h>
#include "BeaconFrame_m.h"

namespace smile {
namespace algorithm {
namespace sf_tdoa {

Define_Module(AnchorApplication);

void AnchorApplication::initialize(int stage)
{
  IdealApplication::initialize(stage);

  if (stage == inet::INITSTAGE_LOCAL) {
    beaconReplyDelay = SimTime{par("beaconReplyDelay").longValue(), SIMTIME_MS};
    predecessorAddress = inet::MACAddress{par("predecessorAddress").stringValue()};
  }

  if (stage == inet::INITSTAGE_PHYSICAL_ENVIRONMENT_2) {
    auto& logger = getLogger();
    const auto handle = logger.obtainHandle("anchors");
    const auto& nicDriver = getNicDriver();
    const auto entry = csv_logger::compose(nicDriver.getMacAddress(), getCurrentTruePosition());
    logger.append(handle, entry);
  }

  if (stage == inet::INITSTAGE_APPLICATION_LAYER) {
    // Designated (initiator) anchor sends the very first frame
    const auto initialAnchor = par("initialAnchor").boolValue();
    if (initialAnchor) {
      sendBeacon(0);
    }
  }
}

void AnchorApplication::handleIncommingMessage(cMessage* newMessage)
{
  const auto frame = dynamic_unique_ptr_cast<BeaconFrame>(std::unique_ptr<cMessage>{newMessage});
  const auto& sourceAddress = frame->getSrc();
  const auto& destinationAddress = frame->getDest();

  // Reply only on broadcast frames sent by our predecessor
  if (!(sourceAddress == predecessorAddress && destinationAddress == inet::MACAddress::BROADCAST_ADDRESS)) {
    return;
  }

  if (desiredTxClockTime < clockTime()) {
    throw cRuntimeError{"cannot schedule frame transmission in past"};
  }

  const auto delay = desiredTxClockTime - clockTime();
  sendBeacon(delay);
}

void AnchorApplication::handleRxCompletionSignal(const IdealRxCompletion& completion)
{
  desiredTxClockTime = completion.getOperationBeginClockTimestamp() + beaconReplyDelay;
}

void AnchorApplication::sendBeacon(const SimTime& delay)
{
  auto frame = createFrame<BeaconFrame>(inet::MACAddress::BROADCAST_ADDRESS);
  frame->setSequenceNumber(sequenceNumber);
  frame->setBitLength(10);
  sendDelayed(frame.release(), delay, "out");

  // Bump sequence number for next frame
  sequenceNumber++;
}

}  // namespace sf_tdoa
}  // namespace algorithm
}  // namespace smile
