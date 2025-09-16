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
//  Author: Susanna Guatelli
//
#ifndef BrachyRunAction_h
#define BrachyRunAction_h 1

#include "G4UserRunAction.hh"
#include "G4RunManager.hh"
#include "globals.hh"

class BrachyRunMessenger;
class BrachySteppingAction;
class G4Run;

class BrachyRunAction : public G4UserRunAction
{
public:
  explicit BrachyRunAction()=default;
  ~BrachyRunAction() override =default;

public:
  void BeginOfRunAction(const G4Run*) override;
  void EndOfRunAction(const G4Run*) override;
  
  // Method to set SteppingAction reference for data export
  void SetSteppingAction(BrachySteppingAction* steppingAction) { fSteppingAction = steppingAction; }
  
  // Static methods to get histogram IDs (set during BeginOfRunAction)
  static G4int GetPrimaryDoseHistoID() { return fPrimaryDoseHistoID; }
  static G4int GetSecondaryDoseHistoID() { return fSecondaryDoseHistoID; }
  static G4int GetPrimaryDose2DHistoID() { return fPrimaryDose2DHistoID; }
  static G4int GetSecondaryDose2DHistoID() { return fSecondaryDose2DHistoID; }

private:
  BrachySteppingAction* fSteppingAction = nullptr;
  
  // Static histogram IDs for primary/secondary dose (1D and 2D)
  static G4int fPrimaryDoseHistoID;
  static G4int fSecondaryDoseHistoID;
  static G4int fPrimaryDose2DHistoID;
  static G4int fSecondaryDose2DHistoID;
};
#endif



