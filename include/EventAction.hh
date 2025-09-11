#ifndef EventAction_h
#define EventAction_h 1

#include "G4UserEventAction.hh"
#include "globals.hh"

class RunAction;

/// Event action class
///
/// It manages event-by-event information for dose scoring

class EventAction : public G4UserEventAction
{
public:
    EventAction(RunAction* runAction);
    virtual ~EventAction();

    virtual void BeginOfEventAction(const G4Event* event);
    virtual void EndOfEventAction(const G4Event* event);

    void AddEdep(G4double edep) { fEdep += edep; }
    void AddDose(G4double dose) { fDose += dose; }

private:
    RunAction* fRunAction;
    G4double fEdep;
    G4double fDose;
};

#endif
