//
// ********************************************************************
// * License and Disclaimer                                           *
// *                                                                  *
// * The  Geant4 software  is  copyright of the Copyright Holders  of *
// * the Geant4 Collaboration.  It is provided  under  the terms  and *
// * conditions of the Geant4 Software License,  included in the file *
// * LICENSE and available at  http://cern.ch/geant4/license .  These *
// * include a list of copyright holders.                             *
// *                                                                  *
// * Neither the authors of this software system, nor their employing *
// * institutes,nor the agencies providing financial support for this *
// * work  make  any representation or  warranty, express or implied, *
// * regarding  this  software system or assume any liability for its *
// * use.  Please see the license in the file  LICENSE  and URL above *
// * for the full disclaimer and the limitation of liability.         *
// *                                                                  *
// * This  code  implementation is the result of  the  scientific and *
// * technical work of the GEANT4 collaboration.                      *
// * By using,  copying,  modifying or  distributing the software (or *
// * any work based  on the software)  you  agree  to acknowledge its *
// * use  in  resulting  scientific  publications,  and indicate your *
// * acceptance of all terms of the Geant4 Software license.          *
// ********************************************************************
//
//
// --------------------------------------------------------------
//                 GEANT 4 - Brachytherapy example
// --------------------------------------------------------------
//
// Code developed by:
//  S.Guatelli and D. Cutajar
//
//
//    *******************************
//    *                             *
//    *    BrachyRunAction.cc       *
//    *                             *
//    *******************************
//
//

#include "BrachyRunAction.hh"
#include "BrachySteppingAction.hh"
#include "G4AnalysisManager.hh"
#include "G4Run.hh"
#include "G4RunManager.hh"
#include "G4UImanager.hh"
#include "G4ios.hh"
#include "G4SystemOfUnits.hh"
#include "globals.hh"
#include <chrono>
#include <sstream>
#include <iomanip>
#include <cstdlib>  // For std::getenv

// Initialize static members
G4int BrachyRunAction::fPrimaryDoseHistoID = -1;
G4int BrachyRunAction::fSecondaryDoseHistoID = -1;
G4int BrachyRunAction::fPrimaryDose2DHistoID = -1;
G4int BrachyRunAction::fSecondaryDose2DHistoID = -1;

void BrachyRunAction::BeginOfRunAction(const G4Run* aRun)
{ 
G4cout << "### Run " << aRun -> GetRunID() << " start." << G4endl;

auto analysisManager = G4AnalysisManager::Instance();

// Check if we're in scoring mode (eDep files) - don't create personal histograms
G4bool isScoringMode = (std::getenv("GEANT4_SCORING_MODE") != nullptr);

if (isScoringMode) {
    G4cout << "SCORING MODE detected - skipping personal histogram creation" << G4endl;
    G4cout << "eDep.root files will contain only official scoring mesh data (h20)" << G4endl;
    return; // Exit early, don't create personal histograms
}

// Generate unique filename with timestamp
auto now = std::chrono::system_clock::now();
auto time_t = std::chrono::system_clock::to_time_t(now);
auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
    now.time_since_epoch()) % 1000;

std::stringstream ss;
ss << "primary_" << std::put_time(std::localtime(&time_t), "%Y%m%d_%H%M%S");
ss << "_" << std::setfill('0') << std::setw(3) << ms.count() << ".root";

G4String filename = ss.str();
G4cout << "Creating PRIMARY ROOT file: " << filename << G4endl;

G4bool fileOpen = analysisManager -> OpenFile(filename);

if (! fileOpen) {
    G4cerr << "\n---> The ROOT output file has not been opened "
           << analysisManager->GetFileName() << G4endl;
  }
  
G4cout << "Using " << analysisManager->GetType() << G4endl;
analysisManager -> SetVerboseLevel(1);

// Create histogram with the energy spectrum of the photons emitted by the
// radionucldie
analysisManager -> CreateH1("h10","energy spectrum", 800, 0., 800.);

// Create histograms for primary vs secondary dose analysis
fPrimaryDoseHistoID = analysisManager -> CreateH1("radial_dose_primary", 
    "Radial Dose Distribution - Primary Particles;Radius (cm);Dose (MeV)", 
    90, 0.0, 4.5);
fSecondaryDoseHistoID = analysisManager -> CreateH1("radial_dose_secondary", 
    "Radial Dose Distribution - Secondary Particles;Radius (cm);Dose (MeV)", 
    90, 0.0, 4.5);

// Create 2D histograms for primary vs secondary dose maps
// IMPORTANT: Using SAME dimensions as scoring mesh for direct comparison
// Scoring mesh: 9.0 x 9.0 cm, 180x180 bins = 0.1 cm/bin resolution
fPrimaryDose2DHistoID = analysisManager -> CreateH2("dose_map_primary", 
    "2D Dose Map - Primary Particles;X (cm);Y (cm);Dose (MeV)", 
    180, -9.0, 9.0, 180, -9.0, 9.0);
fSecondaryDose2DHistoID = analysisManager -> CreateH2("dose_map_secondary", 
    "2D Dose Map - Secondary Particles;X (cm);Y (cm);Dose (MeV)", 
    180, -9.0, 9.0, 180, -9.0, 9.0);

G4cout << "Created dose histograms: Primary 1D ID=" << fPrimaryDoseHistoID 
       << ", Secondary 1D ID=" << fSecondaryDoseHistoID 
       << ", Primary 2D ID=" << fPrimaryDose2DHistoID 
       << ", Secondary 2D ID=" << fSecondaryDose2DHistoID << G4endl;
}

void BrachyRunAction::EndOfRunAction(const G4Run* aRun)
{ 
G4cout << "number of events = " << aRun->GetNumberOfEvent() << G4endl;

// Check if we're in scoring mode - don't process personal histograms
G4bool isScoringMode = (std::getenv("GEANT4_SCORING_MODE") != nullptr);

if (isScoringMode) {
    G4cout << "SCORING MODE - skipping personal histogram processing" << G4endl;
    return; // Exit early, let official scoring handle everything
}

// Export radial dose data if SteppingAction is available
G4cout << "BrachyRunAction::EndOfRunAction - Checking fSteppingAction pointer..." << G4endl;
if (fSteppingAction != nullptr) {
    G4cout << "BrachyRunAction: Exporting radial dose data from SteppingAction..." << G4endl;
    fSteppingAction->ExportRadialDoseToFile();
    
    G4cout << "BrachyRunAction: Filling 2D histograms with voxel data..." << G4endl;
    fSteppingAction->FillVoxelHistograms();
    
    G4cout << "BrachyRunAction: Export completed." << G4endl;
} else {
    G4cout << "BrachyRunAction: WARNING - SteppingAction not set, cannot export dose data." << G4endl;
}
 
// save histograms in primary.root
auto analysisManager = G4AnalysisManager::Instance();
analysisManager -> Write();
analysisManager -> CloseFile();
}




