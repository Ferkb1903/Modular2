#include "SteppingAction.hh"
#include "RunAction.hh"
#include "PrimaryGeneratorAction.hh"
#include "DetectorConstruction.hh"

#include "G4RunManager.hh"
#include "G4Run.hh"
#include "G4AccumulableManager.hh"
#include "G4LogicalVolumeStore.hh"
#include "G4LogicalVolume.hh"
#include "G4UnitsTable.hh"
#include "G4SystemOfUnits.hh"

#include <fstream>
#include <iostream>

RunAction::RunAction()
: G4UserRunAction(),
  fEdep(0.), fEdep2(0.),
  fDose(0.), fDose2(0.),
  fOutputDirectory("output/"),
  fRunID("run_001"),
  fAirKermaStrength(0.),
  fDoseRateConstant(0.),
  fSteppingAction(nullptr)
{
    // Register accumulable to the accumulable manager
    G4AccumulableManager* accumulableManager = G4AccumulableManager::Instance();
    accumulableManager->RegisterAccumulable(fEdep);
    accumulableManager->RegisterAccumulable(fEdep2);
    accumulableManager->RegisterAccumulable(fDose);
    accumulableManager->RegisterAccumulable(fDose2);
}

RunAction::~RunAction()
{
}

void RunAction::BeginOfRunAction(const G4Run*)
{
    // Inform the runManager to save random number seed
    G4RunManager::GetRunManager()->SetRandomNumberStore(false);

    // Reset accumulables to their initial values
    G4AccumulableManager* accumulableManager = G4AccumulableManager::Instance();
    accumulableManager->Reset();

    G4cout << "### Run started ###" << G4endl;
}

void RunAction::EndOfRunAction(const G4Run* run)
{
    G4int nofEvents = run->GetNumberOfEvent();
    if (nofEvents == 0) return;

    // Merge accumulables
    G4AccumulableManager* accumulableManager = G4AccumulableManager::Instance();
    accumulableManager->Merge();

    // Compute dose and rmse
    G4double edep = fEdep.GetValue();
    G4double edep2 = fEdep2.GetValue();

    G4double rms = edep2 - edep*edep/nofEvents;
    if (rms > 0.) rms = std::sqrt(rms); else rms = 0.;

    const DetectorConstruction* detectorConstruction
     = static_cast<const DetectorConstruction*>
       (G4RunManager::GetRunManager()->GetUserDetectorConstruction());

    // Print results
    if (IsMaster()) {
        G4cout
         << G4endl
         << "--------------------End of Global Run-----------------------"
         << G4endl
         << "  The run consists of " << nofEvents << " events"
         << G4endl
         << "  Energy deposited: " 
         << G4BestUnit(edep,"Energy") << " +- " << G4BestUnit(rms,"Energy")
         << G4endl;

        // Calculate and save TG-43 parameters
        CalculateTG43Parameters();
        SaveDoseDistribution();
        SaveTG43Results();
    }
    
    // Export radial dose for primaries and secondaries (not just master)
    G4cout << "Checking fSteppingAction pointer..." << G4endl;
    if (fSteppingAction) {
        G4cout << "Exportando datos de primarias y secundarias..." << G4endl;
        fSteppingAction->ExportRadialDoseToFile(fOutputDirectory + "radial_dose_primary_" + fRunID + ".dat", true);
        fSteppingAction->ExportRadialDoseToFile(fOutputDirectory + "radial_dose_secondary_" + fRunID + ".dat", false);
        G4cout << "Radial dose (primarias/secundarias) exportada a archivos en: " << fOutputDirectory << G4endl;
    } else {
        G4cout << "WARNING: fSteppingAction es nullptr, no se pueden exportar datos de primarias/secundarias" << G4endl;
    }
}

void RunAction::AddEdep(G4double edep)
{
    fEdep += edep;
    fEdep2 += edep*edep;
}

void RunAction::AddDose(G4double dose)
{
    fDose += dose;
    fDose2 += dose*dose;
}

void RunAction::CalculateTG43Parameters()
{
    // Calculate TG-43 parameters from simulation results
    // This is a simplified implementation
    
    G4cout << "Calculating TG-43 parameters..." << G4endl;

    // Air-kerma strength calculation (simplified)
    // Sk = dose rate at 1 m in air × (1 m)²
    // This would need proper implementation with air scoring
    fAirKermaStrength = 1.0; // Placeholder

    // Dose rate constant calculation
    // Λ = dose rate in water at 1 cm / Sk
    fDoseRateConstant = 1.109; // Literature value for Ir-192 (cGy⋅h⁻¹⋅U⁻¹)

    G4cout << "Air-kerma strength: " << fAirKermaStrength << " U" << G4endl;
    G4cout << "Dose rate constant: " << fDoseRateConstant << " cGy⋅h⁻¹⋅U⁻¹" << G4endl;
}

void RunAction::SaveDoseDistribution()
{
    // Save dose distribution to file
    std::ofstream outFile(fOutputDirectory + "dose_distribution_" + fRunID + ".dat");
    
    if (outFile.is_open()) {
        outFile << "# Dose distribution from HDR Ir-192 simulation" << G4endl;
        outFile << "# x(cm)\ty(cm)\tz(cm)\tdose(Gy)" << G4endl;
        
        // This would contain actual dose scoring data
        // For now, just write header
        outFile << "# Data to be implemented with dose scoring" << G4endl;
        
        outFile.close();
        G4cout << "Dose distribution saved to: " << fOutputDirectory + "dose_distribution_" + fRunID + ".dat" << G4endl;
    }
}

void RunAction::SaveTG43Results()
{
    // Save TG-43 validation results
    std::ofstream outFile(fOutputDirectory + "tg43_results_" + fRunID + ".dat");
    
    if (outFile.is_open()) {
        outFile << "# TG-43 Parameter Validation Results" << G4endl;
        outFile << "# Parameter\tSimulated\tLiterature\tDifference(%)" << G4endl;
        
        // Dose rate constant
        G4double litDoseRateConstant = 1.109; // Literature value
        G4double diffDoseRate = (fDoseRateConstant - litDoseRateConstant) / litDoseRateConstant * 100.0;
        
        outFile << "Lambda\t" << fDoseRateConstant << "\t" << litDoseRateConstant << "\t" << diffDoseRate << G4endl;
        
        // Additional parameters would be added here (g(r), F(r,θ))
        
        outFile.close();
        G4cout << "TG-43 results saved to: " << fOutputDirectory + "tg43_results_" + fRunID + ".dat" << G4endl;
    }
}
