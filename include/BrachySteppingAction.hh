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
// Code by Susanna Guatelli
//
//
#ifndef BrachySteppingAction_h
#define BrachySteppingAction_h 1

#include "G4UserSteppingAction.hh"
#include "globals.hh"
#include <vector>

class G4Track; // Forward declaration

class BrachySteppingAction: public G4UserSteppingAction
{
public:

  explicit BrachySteppingAction();
  ~BrachySteppingAction()override=default; 
  
  void UserSteppingAction(const G4Step*) override;
  
  // Methods for radial dose analysis
  void ExportRadialDoseToFile();
  
  // Method to fill 2D histograms with accumulated voxel data
  void FillVoxelHistograms();
  
  // Access to dose arrays for external export
  const std::vector<G4double>& GetPrimaryRadialDose() const { return fPrimaryRadialDose; }
  const std::vector<G4double>& GetSecondaryRadialDose() const { return fSecondaryRadialDose; }

private:
  // Helper function to determine particle generation for proper primary/secondary classification
  G4bool IsPrimaryContribution(const G4Track* track);
  // Constants for radial binning
  static constexpr G4int fNRadialBins = 90; // 4.5 cm / 0.05 cm
  static constexpr G4double fRadialBinWidth = 0.05; // cm
  static constexpr G4double fMaxRadius = 4.5; // cm
  
  // Constants for 2D voxel binning (same as scoring mesh)
  static constexpr G4int fN2DBins = 180; // 180x180 bins
  static constexpr G4double f2DMin = -9.0; // cm
  static constexpr G4double f2DMax = 9.0; // cm
  static constexpr G4double f2DBinWidth = 0.1; // cm (18cm / 180bins)
  
  // Dose arrays separated by particle type
  std::vector<G4double> fPrimaryRadialDose;
  std::vector<G4double> fSecondaryRadialDose;
  
  // 2D voxel accumulation maps (180x180 each)
  std::vector<std::vector<G4double>> fPrimary2DMap;
  std::vector<std::vector<G4double>> fSecondary2DMap;
};
#endif
