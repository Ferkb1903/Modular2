#include "ActionInitialization.hh"
#include "PrimaryGeneratorAction.hh"
#include "RunAction.hh"
#include "EventAction.hh"
#include "SteppingAction.hh"

ActionInitialization::ActionInitialization()
: G4VUserActionInitialization()
{}

ActionInitialization::~ActionInitialization()
{}

void ActionInitialization::BuildForMaster() const
{
    // Master thread initialization
    RunAction* runAction = new RunAction;
    SetUserAction(runAction);
}

void ActionInitialization::Build() const
{
    // Worker thread initialization
    SetUserAction(new PrimaryGeneratorAction);

    RunAction* runAction = new RunAction;
    SetUserAction(runAction);

    EventAction* eventAction = new EventAction(runAction);
    SetUserAction(eventAction);

    SteppingAction* steppingAction = new SteppingAction(eventAction);
    SetUserAction(steppingAction);
    runAction->SetSteppingAction(steppingAction);
}
