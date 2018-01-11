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

namespace smile {
namespace algorithm {
namespace sf_tdoa {

Define_Module(AnchorApplication);

void AnchorApplication::initialize(int stage)
{
  // TODO
}

void AnchorApplication::handleIncommingMessage(cMessage* newMessage)
{
  // TODO
}

void AnchorApplication::handleTxCompletionSignal(const smile::IdealTxCompletion& completion)
{
  // TODO
}

void AnchorApplication::handleRxCompletionSignal(const smile::IdealRxCompletion& completion)
{
  // TODO
}

}  // namespace sf_tdoa
}  // namespace algorithm
}  // namespace smile
