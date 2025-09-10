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
/*
// Code developed by:
// S.Guatelli, susanna@uow.edu.au
//
Original code from geant4/examples/extended/runAndEvent/RE03, by M. Asai
*/

#include "BrachyUserScoreWriter.hh"
#include "G4AnalysisManager.hh"
#include "G4MultiFunctionalDetector.hh"
#include "G4SDParticleFilter.hh"
#include "G4VPrimitiveScorer.hh"
#include "G4VScoringMesh.hh"
#include "G4SystemOfUnits.hh" 
#include <map>
#include <fstream>
#include <chrono>
#include <sstream>
#include <iomanip>
// The default output is
// voxelX, voxelY, voxelZ, edep
// The BrachyUserScoreWriter allows to change the format of the output file.
// in the specific case:
// xx (mm)  yy(mm) zz(mm) edep(keV)
// The same information is stored in a ntuple, in the 
// brachytherapy.root file

BrachyUserScoreWriter::BrachyUserScoreWriter():
G4VScoreWriter() 
{
}

BrachyUserScoreWriter::~BrachyUserScoreWriter() 
{;}

void BrachyUserScoreWriter::DumpQuantityToFile(const G4String & psName,
                                               const G4String & fileName, 
                                               const G4String & option) 
{
using MeshScoreMap = G4VScoringMesh::MeshScoreMap;

if(verboseLevel > 0) 
  {G4cout << "BrachyUserScorer-defined DumpQuantityToFile() method is invoked."
  << G4endl; 
  }

// change the option string into lowercase to the case-insensitive.
G4String opt = option;
std::transform(opt.begin(), opt.end(), opt.begin(), (int (*)(int))(tolower));

// confirm the option
if(opt.size() == 0) opt = "csv";

// open the file
std::ofstream ofile(fileName);
  
if(!ofile) 
{
   G4cerr << "ERROR : DumpToFile : File open error -> " << fileName << G4endl;
   return;
}
  ofile << "# mesh name: " << fScoringMesh->GetWorldName() << G4endl;

// retrieve the map
MeshScoreMap fSMap = fScoringMesh -> GetScoreMap();
 
auto msMapItr = fSMap.find(psName);
  
if(msMapItr == fSMap.end()) 
  {
   G4cerr << "ERROR : DumpToFile : Unknown quantity, \""<< psName 
   << "\"." << G4endl;
   return;
  }

auto score = msMapItr-> second-> GetMap(); 
  
ofile << "# primitive scorer name: " << msMapItr -> first << G4endl;
//
// Write quantity in the ASCII output file and in brachytherapy.root
//
ofile << std::setprecision(16); // for double value with 8 bytes
 
auto analysisManager = G4AnalysisManager::Instance();

// Generate unique filename based on timestamp and mesh name
auto now = std::chrono::system_clock::now();
auto time_t = std::chrono::system_clock::to_time_t(now);
auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(
    now.time_since_epoch()) % 1000;

std::stringstream ss;
ss << std::put_time(std::localtime(&time_t), "%Y%m%d_%H%M%S");
ss << "_" << std::setfill('0') << std::setw(3) << ms.count();
ss << "_" << msMapItr->first << ".root";

G4String filename = ss.str();
G4cout << "Creating ROOT file: " << filename << G4endl;

G4bool fileOpen = analysisManager -> OpenFile(filename);
 if (! fileOpen) {
    G4cerr << "\n---> The ROOT output file has not been opened "
           << analysisManager->GetFileName() << G4endl;
  }
  
G4cout << "Using " << analysisManager -> GetType() << G4endl;
analysisManager -> SetVerboseLevel(1);
analysisManager -> SetActivation(true);

// Create histograms dynamically based on mesh configuration
G4ThreeVector meshSize = fScoringMesh->GetSize();
G4double xMin = -meshSize.x();
G4double xMax = meshSize.x();
G4double yMin = -meshSize.y(); 
G4double yMax = meshSize.y();
G4int nBinsX = fNMeshSegments[0];
G4int nBinsY = fNMeshSegments[1];

G4int histo2= analysisManager-> CreateH2("h20","edep2Dxy", 
                                        nBinsX, xMin, xMax, 
                                        nBinsY, yMin, yMax);

// Histo 0 with the energy spectrum will not be saved 
// in brachytherapy.root
analysisManager->SetH1Activation(0, false);
analysisManager->SetH2Activation(histo2, true);
  
for(int x = 0; x < fNMeshSegments[0]; x++) {
   for(int y = 0; y < fNMeshSegments[1]; y++) {
     for(int z = 0; z < fNMeshSegments[2]; z++){
        G4int numberOfVoxel_x = fNMeshSegments[0];
        G4int numberOfVoxel_y = fNMeshSegments[1];
        G4int numberOfVoxel_z =fNMeshSegments[2];
        // Calculate voxel width dynamically based on mesh configuration
        // Get the mesh size from the scoring mesh
        G4ThreeVector meshSize = fScoringMesh->GetSize();
        G4double voxelWidth_x = (2.0 * meshSize.x()) / numberOfVoxel_x;  // Calculate actual voxel width in X
        G4double voxelWidth_y = (2.0 * meshSize.y()) / numberOfVoxel_y;  // Calculate actual voxel width in Y
        G4double voxelWidth_z = (2.0 * meshSize.z()) / numberOfVoxel_z;  // Calculate actual voxel width in Z
        //
        G4double xx = ( - numberOfVoxel_x + 1+ 2*x )* voxelWidth_x/2;
        G4double yy = ( - numberOfVoxel_y + 1+ 2*y )* voxelWidth_y/2;
        G4double zz = ( - numberOfVoxel_z + 1+ 2*z )* voxelWidth_z/2;
        G4int idx = GetIndex(x, y, z);
        std::map<G4int, G4StatDouble*>::iterator value = score -> find(idx);
        
       if (value != score -> end()) 
        {
         // Print in the ASCII output file the information
 
         ofile << xx << "  " << yy << "  " << zz <<"  " 
               <<(value->second->sum_wx())/keV << G4endl;
        
        // Save the same information in the ROOT output file
   
    if(zz> -0.125 *CLHEP::mm && zz < 0.125/mm) 
         analysisManager->FillH2(histo2, xx, yy, (value->second->sum_wx())/keV);
}}}} 

ofile << std::setprecision(6);

// Close the output ASCII file
ofile.close();

// Close the output ROOT file
analysisManager -> Write();
analysisManager -> CloseFile();
}
