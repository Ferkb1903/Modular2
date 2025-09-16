#ifndef RunAction_h
#define RunAction_h 1

#include "G4UserRunAction.hh"
#include "G4Accumulable.hh"
#include "globals.hh"

class G4Run;
class SteppingAction;

/// Run action class
///
/// In EndOfRunAction(), it calculates the dose for TG-43 parameters
/// and saves results to files for analysis

class RunAction : public G4UserRunAction
{
public:
    RunAction();
    virtual ~RunAction();

    virtual void BeginOfRunAction(const G4Run*);
    virtual void EndOfRunAction(const G4Run*);

    void AddEdep(G4double edep);
    void AddDose(G4double dose);

    // SteppingAction management
    void SetSteppingAction(SteppingAction* steppingAction) { fSteppingAction = steppingAction; }
    void CalculateTG43Parameters();
    // TG-43 parameter calculation methods
    void SaveDoseDistribution();
    void SaveTG43Results();

private:
    G4Accumulable<G4double> fEdep;
    G4Accumulable<G4double> fEdep2;
    G4Accumulable<G4double> fDose;
    G4Accumulable<G4double> fDose2;

    // Output file management
    G4String fOutputDirectory;
    G4String fRunID;

    // TG-43 parameters
    G4double fAirKermaStrength;  // Sk in U (μGy⋅m²/h)
    G4double fDoseRateConstant;  // Λ in cGy⋅h⁻¹⋅U⁻¹
    
    // Pointer to SteppingAction for data export
    SteppingAction* fSteppingAction;
};

#endif
