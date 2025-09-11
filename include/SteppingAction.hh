#ifndef SteppingAction_h
#define SteppingAction_h 1

#include "G4UserSteppingAction.hh"
#include "globals.hh"
#include "G4ThreeVector.hh"
#include <vector>

class EventAction;
class G4LogicalVolume;

/// Stepping action class
/// 
/// Collects energy deposition step-by-step and converts to dose
/// Implements dose scoring for TG-43 validation and heterogeneous analysis

class SteppingAction : public G4UserSteppingAction
{
public:
    SteppingAction(EventAction* eventAction);
    virtual ~SteppingAction();

    virtual void UserSteppingAction(const G4Step*);

    // Dose scoring methods
    void ScoreDoseInVoxel(const G4Step* step);
    void ScoreDoseRadially(const G4Step* step);
    void ScoreDoseAngularly(const G4Step* step);

private:
    EventAction* fEventAction;
    G4LogicalVolume* fScoringVolume;

    // Scoring parameters
    G4int fNRadialBins;
    G4int fNAngularBins;
    G4double fMaxRadius;
    
    // Dose scoring arrays
    std::vector<G4double> fRadialDose;
    std::vector<std::vector<G4double>> fAngularDose;
    std::vector<G4int> fRadialCounts;
    std::vector<std::vector<G4int>> fAngularCounts;

    // Helper methods
    G4double CalculateRadius(const G4ThreeVector& position);
    G4double CalculateAngle(const G4ThreeVector& position);
    G4int GetRadialBin(G4double radius);
    G4int GetAngularBin(G4double angle);
};

#endif
