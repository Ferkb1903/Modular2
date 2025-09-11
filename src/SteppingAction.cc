#include "SteppingAction.hh"
#include "EventAction.hh"
#include "DetectorConstruction.hh"

#include "G4Step.hh"
#include "G4Event.hh"
#include "G4RunManager.hh"
#include "G4LogicalVolume.hh"
#include "G4SystemOfUnits.hh"

SteppingAction::SteppingAction(EventAction* eventAction)
: G4UserSteppingAction(),
  fEventAction(eventAction),
  fScoringVolume(0),
  fNRadialBins(100),
  fNAngularBins(18),
  fMaxRadius(15.0*cm)
{
    // Initialize dose scoring arrays
    fRadialDose.resize(fNRadialBins, 0.0);
    fRadialCounts.resize(fNRadialBins, 0);
    
    fAngularDose.resize(fNRadialBins);
    fAngularCounts.resize(fNRadialBins);
    for (G4int i = 0; i < fNRadialBins; ++i) {
        fAngularDose[i].resize(fNAngularBins, 0.0);
        fAngularCounts[i].resize(fNAngularBins, 0);
    }
}

SteppingAction::~SteppingAction()
{
}

void SteppingAction::UserSteppingAction(const G4Step* step)
{
    if (!fScoringVolume) {
        const DetectorConstruction* detectorConstruction
          = static_cast<const DetectorConstruction*>
            (G4RunManager::GetRunManager()->GetUserDetectorConstruction());
        fScoringVolume = detectorConstruction->GetWaterPhantom()->GetLogicalVolume();
    }

    // get volume of the current step
    G4LogicalVolume* volume 
      = step->GetPreStepPoint()->GetTouchableHandle()
        ->GetVolume()->GetLogicalVolume();
      
    // check if we are in scoring volume
    if (volume != fScoringVolume) return;

    // collect energy deposited in this step
    G4double edepStep = step->GetTotalEnergyDeposit();
    fEventAction->AddEdep(edepStep);

    // Dose scoring for TG-43 analysis
    ScoreDoseInVoxel(step);
    ScoreDoseRadially(step);
    ScoreDoseAngularly(step);
}

void SteppingAction::ScoreDoseInVoxel(const G4Step* step)
{
    // Score dose in voxel for 3D dose distribution
    G4double edep = step->GetTotalEnergyDeposit();
    if (edep <= 0.) return;

    // Get step position
    G4ThreeVector position = step->GetPreStepPoint()->GetPosition();
    
    // Get mass of the voxel (simplified - assumes uniform density)
    G4double density = step->GetPreStepPoint()->GetMaterial()->GetDensity();
    G4double stepLength = step->GetStepLength();
    G4double mass = density * stepLength * 1.0*mm*mm; // Approximate cross-sectional area
    
    if (mass > 0.) {
        G4double dose = edep / mass;
        fEventAction->AddDose(dose);
    }
}

void SteppingAction::ScoreDoseRadially(const G4Step* step)
{
    // Score dose as function of radius for g(r) calculation
    G4double edep = step->GetTotalEnergyDeposit();
    if (edep <= 0.) return;

    G4ThreeVector position = step->GetPreStepPoint()->GetPosition();
    G4double radius = CalculateRadius(position);
    
    G4int bin = GetRadialBin(radius);
    if (bin >= 0 && bin < fNRadialBins) {
        // Get mass for dose calculation
        G4double density = step->GetPreStepPoint()->GetMaterial()->GetDensity();
        G4double volume = step->GetStepLength() * 1.0*mm*mm; // Simplified volume
        G4double mass = density * volume;
        
        if (mass > 0.) {
            G4double dose = edep / mass;
            fRadialDose[bin] += dose;
            fRadialCounts[bin]++;
        }
    }
}

void SteppingAction::ScoreDoseAngularly(const G4Step* step)
{
    // Score dose as function of angle for F(r,θ) calculation
    G4double edep = step->GetTotalEnergyDeposit();
    if (edep <= 0.) return;

    G4ThreeVector position = step->GetPreStepPoint()->GetPosition();
    G4double radius = CalculateRadius(position);
    G4double angle = CalculateAngle(position);
    
    G4int rBin = GetRadialBin(radius);
    G4int aBin = GetAngularBin(angle);
    
    if (rBin >= 0 && rBin < fNRadialBins && aBin >= 0 && aBin < fNAngularBins) {
        // Get mass for dose calculation
        G4double density = step->GetPreStepPoint()->GetMaterial()->GetDensity();
        G4double volume = step->GetStepLength() * 1.0*mm*mm; // Simplified volume
        G4double mass = density * volume;
        
        if (mass > 0.) {
            G4double dose = edep / mass;
            fAngularDose[rBin][aBin] += dose;
            fAngularCounts[rBin][aBin]++;
        }
    }
}

G4double SteppingAction::CalculateRadius(const G4ThreeVector& position)
{
    // Calculate distance from source center (assumed at origin)
    return position.mag();
}

G4double SteppingAction::CalculateAngle(const G4ThreeVector& position)
{
    // Calculate polar angle θ from z-axis (source longitudinal axis)
    if (position.mag() == 0.) return 0.;
    return position.theta();
}

G4int SteppingAction::GetRadialBin(G4double radius)
{
    // Convert radius to bin index
    if (radius < 0. || radius > fMaxRadius) return -1;
    return static_cast<G4int>(radius / fMaxRadius * fNRadialBins);
}

G4int SteppingAction::GetAngularBin(G4double angle)
{
    // Convert angle (0 to π) to bin index
    if (angle < 0. || angle > CLHEP::pi) return -1;
    return static_cast<G4int>(angle / CLHEP::pi * fNAngularBins);
}
