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
// Code developed by:
//  S.Guatelli, A. Le
//
//    *********************************
//    *                               *
//    *    BrachyDetectorMessenger.cc *
//    *                               *
//    *********************************
//
//
#include "BrachyDetectorMessenger.hh"
#include "BrachyDetectorConstruction.hh"
#include "G4UIdirectory.hh"
#include "G4UIcmdWithAString.hh"
#include "G4UIcmdWithABool.hh"
#include "G4UIcmdWith3VectorAndUnit.hh"

BrachyDetectorMessenger::BrachyDetectorMessenger(BrachyDetectorConstruction* detector): fDetector(detector)
{ 
  fDetectorDir = new G4UIdirectory("/phantom/");
  fDetectorDir -> SetGuidance(" phantom control.");
      
  fPhantomMaterialCmd = new G4UIcmdWithAString("/phantom/selectMaterial",this);
  fPhantomMaterialCmd -> SetGuidance("Select Material of the phantom.");
  fPhantomMaterialCmd -> SetParameterName("choice",false);
  fPhantomMaterialCmd -> AvailableForStates(G4State_Idle);
  
  fSourceCmd = new G4UIcmdWithAString("/source/switch",this);
  fSourceCmd -> SetGuidance("Assign the selected geometry to G4RunManager."); 
  fSourceCmd -> SetParameterName("choice",true);
  fSourceCmd -> SetDefaultValue(" ");
  fSourceCmd -> SetCandidates("TG186 Flexi Iodine Leipzig Oncura");
  fSourceCmd -> AvailableForStates(G4State_PreInit,G4State_Idle); 

  // Commands for heterogeneities
  fEnableHeterogeneityCmd = new G4UIcmdWithABool("/phantom/enableHeterogeneities",this);
  fEnableHeterogeneityCmd -> SetGuidance("Enable or disable heterogeneities in phantom.");
  fEnableHeterogeneityCmd -> SetParameterName("enable",false);
  fEnableHeterogeneityCmd -> AvailableForStates(G4State_PreInit,G4State_Idle);

  fHeterogeneityTypeCmd = new G4UIcmdWithAString("/phantom/setHeterogeneityType",this);
  fHeterogeneityTypeCmd -> SetGuidance("Set the type of heterogeneity material.");
  fHeterogeneityTypeCmd -> SetParameterName("type",false);
  fHeterogeneityTypeCmd -> SetCandidates("bone muscle fat lung");
  fHeterogeneityTypeCmd -> AvailableForStates(G4State_PreInit,G4State_Idle);

  fHeterogeneitySizeCmd = new G4UIcmdWith3VectorAndUnit("/phantom/setHeterogeneitySize",this);
  fHeterogeneitySizeCmd -> SetGuidance("Set the size (half-dimensions) of heterogeneity cube.");
  fHeterogeneitySizeCmd -> SetParameterName("sizeX","sizeY","sizeZ",false);
  fHeterogeneitySizeCmd -> SetDefaultUnit("cm");
  fHeterogeneitySizeCmd -> AvailableForStates(G4State_PreInit,G4State_Idle);

  fHeterogeneityCenterCmd = new G4UIcmdWith3VectorAndUnit("/phantom/setHeterogeneityCenter",this);
  fHeterogeneityCenterCmd -> SetGuidance("Set the center position of heterogeneity cube.");
  fHeterogeneityCenterCmd -> SetParameterName("centerX","centerY","centerZ",false);
  fHeterogeneityCenterCmd -> SetDefaultUnit("cm");
  fHeterogeneityCenterCmd -> AvailableForStates(G4State_PreInit,G4State_Idle); 
 }

BrachyDetectorMessenger::~BrachyDetectorMessenger()
{
  delete fSourceCmd;
  delete fPhantomMaterialCmd; 
  delete fEnableHeterogeneityCmd;
  delete fHeterogeneityTypeCmd;
  delete fHeterogeneitySizeCmd;
  delete fHeterogeneityCenterCmd;
  delete fDetectorDir;
}

void BrachyDetectorMessenger::SetNewValue(G4UIcommand* command,G4String newValue)
{ 
  // Change the material of the phantom
  if( command == fPhantomMaterialCmd )
   { fDetector -> SetPhantomMaterial(newValue);}

  // Switch the source in the phantom
  if( command == fSourceCmd )
   {
    if(newValue=="Iodine" || newValue=="TG186"|| newValue=="Leipzig" || newValue== "Flexi" || newValue== "Oncura")
     { 
       fDetector -> SelectBrachytherapicSeed(newValue); 
       fDetector -> SwitchBrachytherapicSeed();
      }
   }

  // Enable/disable heterogeneities
  if( command == fEnableHeterogeneityCmd )
   { 
     G4bool enable = fEnableHeterogeneityCmd->GetNewBoolValue(newValue);
     fDetector -> EnableHeterogeneities(enable);
   }

  // Set heterogeneity type
  if( command == fHeterogeneityTypeCmd )
   { fDetector -> SetHeterogeneityType(newValue);}

  // Set heterogeneity size
  if( command == fHeterogeneitySizeCmd )
   { 
     G4ThreeVector size = fHeterogeneitySizeCmd->GetNew3VectorValue(newValue);
     fDetector -> SetHeterogeneitySize(size);
   }

  // Set heterogeneity center
  if( command == fHeterogeneityCenterCmd )
   { 
     G4ThreeVector center = fHeterogeneityCenterCmd->GetNew3VectorValue(newValue);
     fDetector -> SetHeterogeneityCenter(center);
   }
}

