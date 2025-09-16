#include "SteppingAction.hh"
#include "EventAction.hh"
#include "DetectorConstruction.hh"

#include "G4Step.hh"
#include "G4Event.hh"
#include "G4RunManager.hh"
#include "G4LogicalVolume.hh"
#include "G4SystemOfUnits.hh"
#include <fstream>
#include <iomanip>

SteppingAction::SteppingAction(EventAction* eventAction)
: G4UserSteppingAction(),
  fEventAction(eventAction),
  fScoringVolume(0),
  fNRadialBins(100),
  fNAngularBins(18),
  fMaxRadius(15.0*cm)
{
    // Initialize dose scoring arrays (total)
    fRadialDose.resize(fNRadialBins, 0.0);
    fRadialCounts.resize(fNRadialBins, 0);
    fAngularDose.resize(fNRadialBins);
    fAngularCounts.resize(fNRadialBins);
    // Primaries
    fRadialDosePrimary.resize(fNRadialBins, 0.0);
    fRadialCountsPrimary.resize(fNRadialBins, 0);
    fAngularDosePrimary.resize(fNRadialBins);
    fAngularCountsPrimary.resize(fNRadialBins);
    // Secondaries
    fRadialDoseSecondary.resize(fNRadialBins, 0.0);
    fRadialCountsSecondary.resize(fNRadialBins, 0);
    fAngularDoseSecondary.resize(fNRadialBins);
    fAngularCountsSecondary.resize(fNRadialBins);
    for (G4int i = 0; i < fNRadialBins; ++i) {
        fAngularDose[i].resize(fNAngularBins, 0.0);
        fAngularCounts[i].resize(fNAngularBins, 0);
        fAngularDosePrimary[i].resize(fNAngularBins, 0.0);
        fAngularCountsPrimary[i].resize(fNAngularBins, 0);
        fAngularDoseSecondary[i].resize(fNAngularBins, 0.0);
        fAngularCountsSecondary[i].resize(fNAngularBins, 0);
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

    // Distinguish primary vs secondary
    G4int parentID = step->GetTrack()->GetParentID();

    // Dose scoring for TG-43 analysis
    ScoreDoseInVoxel(step);
    ScoreDoseRadially(step);
    ScoreDoseAngularly(step);

    // Scoring for primaries and secondaries
    if (parentID == 0) {
        ScoreDoseRadially(step, true);
        ScoreDoseAngularly(step, true);
    } else {
        ScoreDoseRadially(step, false);
        ScoreDoseAngularly(step, false);
    }
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
    ScoreDoseRadially(step, -1);
}

void SteppingAction::ScoreDoseRadially(const G4Step* step, int primary)
{
    // primary: 1=primary, 0=secondary, -1=total
    G4double edep = step->GetTotalEnergyDeposit();
    if (edep <= 0.) return;

    G4ThreeVector position = step->GetPreStepPoint()->GetPosition();
    G4double radius = CalculateRadius(position);
    G4int bin = GetRadialBin(radius);
    if (bin >= 0 && bin < fNRadialBins) {
        G4double density = step->GetPreStepPoint()->GetMaterial()->GetDensity();
        G4double volume = step->GetStepLength() * 1.0*mm*mm;
        G4double mass = density * volume;
        if (mass > 0.) {
            G4double dose = edep / mass;
            if (primary == 1) {
                fRadialDosePrimary[bin] += dose;
                fRadialCountsPrimary[bin]++;
            } else if (primary == 0) {
                fRadialDoseSecondary[bin] += dose;
                fRadialCountsSecondary[bin]++;
            } else {
                fRadialDose[bin] += dose;
                fRadialCounts[bin]++;
            }
        }
    }
}

void SteppingAction::ScoreDoseAngularly(const G4Step* step)
{
    ScoreDoseAngularly(step, -1);
}

void SteppingAction::ScoreDoseAngularly(const G4Step* step, int primary)
{
    // primary: 1=primary, 0=secondary, -1=total
    G4double edep = step->GetTotalEnergyDeposit();
    if (edep <= 0.) return;

    G4ThreeVector position = step->GetPreStepPoint()->GetPosition();
    G4double radius = CalculateRadius(position);
    G4double angle = CalculateAngle(position);
    G4int rBin = GetRadialBin(radius);
    G4int aBin = GetAngularBin(angle);
    if (rBin >= 0 && rBin < fNRadialBins && aBin >= 0 && aBin < fNAngularBins) {
        G4double density = step->GetPreStepPoint()->GetMaterial()->GetDensity();
        G4double volume = step->GetStepLength() * 1.0*mm*mm;
        G4double mass = density * volume;
        if (mass > 0.) {
            G4double dose = edep / mass;
            if (primary == 1) {
                fAngularDosePrimary[rBin][aBin] += dose;
                fAngularCountsPrimary[rBin][aBin]++;
            } else if (primary == 0) {
                fAngularDoseSecondary[rBin][aBin] += dose;
                fAngularCountsSecondary[rBin][aBin]++;
            } else {
                fAngularDose[rBin][aBin] += dose;
                fAngularCounts[rBin][aBin]++;
            }
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

void SteppingAction::ExportRadialDoseToFile(const std::string& filename, bool primary) const
{
    std::ofstream out(filename);
    out << "# r_bin(cm)\tdose(Gy)\tcounts" << std::endl;
    for (G4int i = 0; i < fNRadialBins; ++i) {
        double r = (i + 0.5) * fMaxRadius / fNRadialBins / CLHEP::cm;
        double dose = 0.0;
        int counts = 0;
        if (primary) {
            dose = fRadialDosePrimary[i];
            counts = fRadialCountsPrimary[i];
        } else {
            dose = fRadialDoseSecondary[i];
            counts = fRadialCountsSecondary[i];
        }
        out << std::fixed << std::setprecision(4) << r << "\t" << dose << "\t" << counts << std::endl;
    }
    out.close();
}
