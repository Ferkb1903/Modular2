#ifndef SteppingAction_h
#define SteppingAction_h 1

#include "G4UserSteppingAction.hh"
#include "globals.hh"
#include "G4ThreeVector.hh"
#include <vector>
#include <string>

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
    void ScoreDoseRadially(const G4Step* step, int primary); // 1=primaria, 0=secundaria, -1=total
    void ScoreDoseAngularly(const G4Step* step);
    void ScoreDoseAngularly(const G4Step* step, int primary); // 1=primaria, 0=secundaria, -1=total

    // Export methods
    void ExportRadialDoseToFile(const std::string& filename, bool primary) const;

private:
    EventAction* fEventAction;
    G4LogicalVolume* fScoringVolume;

    // Scoring parameters
    G4int fNRadialBins;
    G4int fNAngularBins;
    G4double fMaxRadius;

    // Dose scoring arrays (total)
    std::vector<G4double> fRadialDose;
    std::vector<std::vector<G4double>> fAngularDose;
    std::vector<G4int> fRadialCounts;
    std::vector<std::vector<G4int>> fAngularCounts;

    // Radial dose scoring (primaries and secondaries)
    std::vector<G4double> fRadialDosePrimary;
    std::vector<G4int> fRadialCountsPrimary;
    std::vector<G4double> fRadialDoseSecondary;
    std::vector<G4int> fRadialCountsSecondary;
    
    // Angular dose scoring (primaries and secondaries)
    std::vector<std::vector<G4double>> fAngularDosePrimary;
    std::vector<std::vector<G4int>> fAngularCountsPrimary;
    std::vector<std::vector<G4double>> fAngularDoseSecondary;
    std::vector<std::vector<G4int>> fAngularCountsSecondary;

    // Helper methods
    G4double CalculateRadius(const G4ThreeVector& position);
    G4double CalculateAngle(const G4ThreeVector& position);
    G4int GetRadialBin(G4double radius);
    G4int GetAngularBin(G4double angle);
};

#endif
