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

  // Reply on frame (i.a. broadcast beacon) only if it was sent by predecessor
  if (sourceAddress == predecessorAddress) {
    sendBeacon(beaconReplyDelay);
  }
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
