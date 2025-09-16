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
// Author: Susanna Guatelli (guatelli@ge.infn.it)
//
#include "BrachySteppingAction.hh"
#include "BrachyRunAction.hh"
#include "G4AnalysisManager.hh"
#include "G4ios.hh"
#include "G4SteppingManager.hh"
#include "G4Step.hh"
#include "G4Track.hh"
#include "G4StepPoint.hh"
#include "G4ParticleDefinition.hh"
#include "G4VPhysicalVolume.hh"
#include "G4TrackStatus.hh"
#include "G4ParticleDefinition.hh"
#include "G4Gamma.hh"
#include <cstdlib>  // For std::getenv
#include "G4SystemOfUnits.hh"
#include "G4EventManager.hh"
#include "G4TrackingManager.hh"
#include <fstream>
#include <iomanip>
#include <chrono>
#include <sstream>

BrachySteppingAction::BrachySteppingAction()
: G4UserSteppingAction(),
  fPrimaryRadialDose(fNRadialBins, 0.0),
  fSecondaryRadialDose(fNRadialBins, 0.0),
  fPrimary2DMap(fN2DBins, std::vector<G4double>(fN2DBins, 0.0)),
  fSecondary2DMap(fN2DBins, std::vector<G4double>(fN2DBins, 0.0))
{
    G4cout << "BrachySteppingAction: Initialized with " << fNRadialBins 
           << " radial bins, bin width " << fRadialBinWidth << " cm" << G4endl;
    G4cout << "BrachySteppingAction: Initialized 2D maps " << fN2DBins 
           << "x" << fN2DBins << " bins, range " << f2DMin << " to " << f2DMax << " cm" << G4endl;
}

void BrachySteppingAction::UserSteppingAction(const G4Step* aStep)
{

// Retrieve the spectrum of photons emitted in the Radioactive Decay
// and store it in a 1D histogram

  G4SteppingManager*  steppingManager = fpSteppingManager;
  G4Track* theTrack = aStep-> GetTrack();

  // NEW: Primary vs Secondary particle dose separation - BEFORE any filtering
  // Get energy deposition for EVERY step
  G4double energyDeposit = aStep->GetTotalEnergyDeposit();
  if (energyDeposit > 0) {
      // Check if we're in scoring mode - don't accumulate personal data
      G4bool isScoringMode = (std::getenv("GEANT4_SCORING_MODE") != nullptr);
      
      if (!isScoringMode) {
          // Get position
          G4StepPoint* prePoint = aStep->GetPreStepPoint();
          G4ThreeVector position = prePoint->GetPosition();
      
      // Get parent ID to distinguish primary vs secondary particles
      G4int parentID = theTrack->GetParentID();
      
      // ACCUMULATE in 2D voxel maps (same range as scoring mesh: -9 to +9 cm)
      // Convert position to bin indices
      G4double x_cm = position.x() / cm;
      G4double y_cm = position.y() / cm;
      G4double z_cm = position.z() / cm;
      
      // Apply SAME Z filter as scoring mesh: boxSize Z = 0.25 cm means ±0.125 cm
      // This ensures we count exactly the same region as the official scoring mesh
      if (z_cm >= -0.125 && z_cm <= 0.125) {
          // Check if within 2D range
          if (x_cm >= f2DMin && x_cm < f2DMax && y_cm >= f2DMin && y_cm < f2DMax) {
              // Calculate bin indices
              G4int x_bin = static_cast<G4int>((x_cm - f2DMin) / f2DBinWidth);
              G4int y_bin = static_cast<G4int>((y_cm - f2DMin) / f2DBinWidth);
              
              // Ensure we don't go out of bounds
              if (x_bin >= 0 && x_bin < fN2DBins && y_bin >= 0 && y_bin < fN2DBins) {
                  // Use physics-based classification instead of simple parentID check
                  if (IsPrimaryContribution(theTrack)) {
                      // Primary contribution - accumulate in primary map
                      fPrimary2DMap[x_bin][y_bin] += energyDeposit / MeV;
                  } else {
                      // Secondary contribution - accumulate in secondary map
                      fSecondary2DMap[x_bin][y_bin] += energyDeposit / MeV;
                  }
              }
          }
      }
      
          // Also accumulate radial dose (apply same Z filter for consistency)
          if (z_cm >= -0.125 && z_cm <= 0.125) {
              G4double radius = sqrt(x_cm*x_cm + y_cm*y_cm);
              if (radius <= fMaxRadius) {
                  G4int radialBin = static_cast<G4int>(radius / fRadialBinWidth);
                  if (radialBin < fNRadialBins) {
                      // Use physics-based classification for radial dose too
                      if (IsPrimaryContribution(theTrack)) {
                          fPrimaryRadialDose[radialBin] += energyDeposit / MeV;
                      } else {
                          fSecondaryRadialDose[radialBin] += energyDeposit / MeV;
                      }
                  }
              }
          }
      } // End of !isScoringMode check
  }

  // check if it is alive (for secondary particle counting)
  if(theTrack-> GetTrackStatus() == fAlive) {return;}
   
  // Retrieve the secondary particles
  G4TrackVector* fSecondary = steppingManager -> GetfSecondary();
     
   for(size_t lp1=0;lp1<(*fSecondary).size(); lp1++)
   { 
     // Retrieve particle
     const G4ParticleDefinition* particleName = (*fSecondary)[lp1] -> GetDefinition();     

     if (particleName == G4Gamma::Definition())
     {
      G4String process = (*fSecondary)[lp1]-> GetCreatorProcess()-> GetProcessName();  
      
      // Retrieve the process originating it
      // G4cout << "creator process " << process << G4endl;
        if (process == "RadioactiveDecay")
         {
          G4double energy = (*fSecondary)[lp1]  -> GetKineticEnergy();   
          G4AnalysisManager* analysisManager = G4AnalysisManager::Instance();
           // Fill histogram with energy spectrum of the photons emitted in the 
           // radioactive decay
           analysisManager -> FillH1(0, energy/keV);
         }
      }
   }
}

void BrachySteppingAction::ExportRadialDoseToFile()
{
    G4cout << "=== Primary vs Secondary Dose Analysis Summary ===" << G4endl;
    G4cout << "Primary dose histograms filled in ROOT file" << G4endl;
    G4cout << "Secondary dose histograms filled in ROOT file" << G4endl;
    
    // Calculate totals from our arrays for summary
    G4double totalPrimaryDose = 0.0;
    G4double totalSecondaryDose = 0.0;
    
    for (G4int i = 0; i < fNRadialBins; ++i) {
        totalPrimaryDose += fPrimaryRadialDose[i];
        totalSecondaryDose += fSecondaryRadialDose[i];
    }
    
    G4cout << "Total Primary Dose: " << totalPrimaryDose << " MeV" << G4endl;
    G4cout << "Total Secondary Dose: " << totalSecondaryDose << " MeV" << G4endl;
    G4cout << "Primary/Secondary Ratio: " << (totalSecondaryDose > 0 ? totalPrimaryDose/totalSecondaryDose : 0) << G4endl;
    G4cout << "=================================================" << G4endl;
}

void BrachySteppingAction::FillVoxelHistograms()
{
    G4cout << "BrachySteppingAction: Filling 2D histograms with accumulated voxel data..." << G4endl;
    
    // Check if we're in scoring mode - don't fill personal histograms
    G4bool isScoringMode = (std::getenv("GEANT4_SCORING_MODE") != nullptr);
    
    if (isScoringMode) {
        G4cout << "SCORING MODE - skipping personal histogram filling" << G4endl;
        return; // Exit early
    }
    
    G4AnalysisManager* analysisManager = G4AnalysisManager::Instance();
    
    G4int primaryVoxelsWithData = 0;
    G4int secondaryVoxelsWithData = 0;
    G4double totalPrimary2D = 0.0;
    G4double totalSecondary2D = 0.0;
    
    // Fill histograms with accumulated voxel data
    for (G4int i = 0; i < fN2DBins; ++i) {
        for (G4int j = 0; j < fN2DBins; ++j) {
            // Calculate bin center positions
            G4double x_center = f2DMin + (i + 0.5) * f2DBinWidth;
            G4double y_center = f2DMin + (j + 0.5) * f2DBinWidth;
            
            // Fill primary histogram if there's accumulated energy
            if (fPrimary2DMap[i][j] > 0.0) {
                if (BrachyRunAction::GetPrimaryDose2DHistoID() >= 0) {
                    analysisManager->FillH2(BrachyRunAction::GetPrimaryDose2DHistoID(), 
                                           x_center, y_center, fPrimary2DMap[i][j]);
                }
                primaryVoxelsWithData++;
                totalPrimary2D += fPrimary2DMap[i][j];
            }
            
            // Fill secondary histogram if there's accumulated energy
            if (fSecondary2DMap[i][j] > 0.0) {
                if (BrachyRunAction::GetSecondaryDose2DHistoID() >= 0) {
                    analysisManager->FillH2(BrachyRunAction::GetSecondaryDose2DHistoID(), 
                                           x_center, y_center, fSecondary2DMap[i][j]);
                }
                secondaryVoxelsWithData++;
                totalSecondary2D += fSecondary2DMap[i][j];
            }
        }
    }
    
    G4cout << "2D Voxel Summary:" << G4endl;
    G4cout << "  Primary voxels with data: " << primaryVoxelsWithData << G4endl;
    G4cout << "  Secondary voxels with data: " << secondaryVoxelsWithData << G4endl;
    G4cout << "  Total primary 2D dose: " << totalPrimary2D << " MeV" << G4endl;
    G4cout << "  Total secondary 2D dose: " << totalSecondary2D << " MeV" << G4endl;
    G4cout << "  Total 2D dose: " << (totalPrimary2D + totalSecondary2D) << " MeV" << G4endl;
}

G4bool BrachySteppingAction::IsPrimaryContribution(const G4Track* track) 
{
    // Physics-based classification for HDR brachytherapy:
    // PRIMARY = Source photons + immediate Compton/photoelectric electrons
    // SECONDARY = Multiple scattered photons and their products
    
    G4int parentID = track->GetParentID();
    
    // Generation 0: Photons directly from radioactive source
    if (parentID == 0) {
        return true;
    }
    
    // Generation 1: Immediate products of source photons
    // These include Compton electrons and photoelectrons that deposit most dose
    if (parentID == 1) {
        // Check if parent was a source photon by examining process
        const G4VProcess* creatorProcess = track->GetCreatorProcess();
        if (creatorProcess) {
            G4String processName = creatorProcess->GetProcessName();
            
            // Primary interactions: Compton scattering and photoelectric effect
            if (processName == "compt" || processName == "phot" || 
                processName == "conv" || processName == "Rayl") {
                return true;
            }
        }
        // If we can't determine the process, be conservative and consider it primary
        return true;
    }
    
    // Conservative approach for generation 2: only very immediate products
    // Most dose in brachytherapy comes from first-generation interactions
    if (parentID <= 5) {
        const G4VProcess* creatorProcess = track->GetCreatorProcess();
        if (creatorProcess) {
            G4String processName = creatorProcess->GetProcessName();
            // Only include if it's a direct EM process, not multiple scattering
            if (processName == "compt" || processName == "phot") {
                return true;
            }
        }
    }
    
    // Everything else is secondary (multiple scattering, tertiary interactions)
    return false;
}
