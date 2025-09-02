#include "PhysicsList.hh"

#include "G4DecayPhysics.hh"
#include "G4RadioactiveDecayPhysics.hh"
#include "G4EmLivermorePhysics.hh"
#include "G4EmPenelopePhysics.hh"
#include "G4EmStandardPhysics_option4.hh"

#include "G4Gamma.hh"
#include "G4Electron.hh"
#include "G4Positron.hh"
#include "G4Proton.hh"

#include "G4UnitsTable.hh"
#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"

PhysicsList::PhysicsList()
: G4VModularPhysicsList(),
  fEmPhysicsList(nullptr),
  fDecayPhysicsList(nullptr),
  fRadioactiveDecayList(nullptr),
  fCutForGamma(0.01*mm),
  fCutForElectron(0.01*mm),
  fCutForPositron(0.01*mm),
  fCutForProton(0.01*mm)
{
    // Set verbosity level
    SetVerboseLevel(1);

    // Electromagnetic physics
    // Use Livermore low-energy physics for accurate dose calculations
    fEmPhysicsList = new G4EmLivermorePhysics(1);
    RegisterPhysics(fEmPhysicsList);

    // Decay physics
    fDecayPhysicsList = new G4DecayPhysics(1);
    RegisterPhysics(fDecayPhysicsList);

    // Radioactive decay physics
    fRadioactiveDecayList = new G4RadioactiveDecayPhysics(1);
    RegisterPhysics(fRadioactiveDecayList);
}

PhysicsList::~PhysicsList()
{
}

void PhysicsList::ConstructParticle()
{
    // Construct all particles
    G4VModularPhysicsList::ConstructParticle();
}

void PhysicsList::ConstructProcess()
{
    // Construct all processes
    G4VModularPhysicsList::ConstructProcess();
}

void PhysicsList::SetCuts()
{
    // Set production cuts for different particles
    SetCutValue(fCutForGamma, "gamma");
    SetCutValue(fCutForElectron, "e-");
    SetCutValue(fCutForPositron, "e+");
    SetCutValue(fCutForProton, "proton");

    // Set cuts for specific regions if needed
    // SetProductionCuts for specific regions can be implemented here

    if (verboseLevel > 0) {
        DumpCutValuesTable();
    }
}

void PhysicsList::SetGammaCut(G4double cut)
{
    fCutForGamma = cut;
    SetParticleCuts(fCutForGamma, G4Gamma::Gamma());
}

void PhysicsList::SetElectronCut(G4double cut)
{
    fCutForElectron = cut;
    SetParticleCuts(fCutForElectron, G4Electron::Electron());
}

void PhysicsList::SetPositronCut(G4double cut)
{
    fCutForPositron = cut;
    SetParticleCuts(fCutForPositron, G4Positron::Positron());
}

void PhysicsList::SetProtonCut(G4double cut)
{
    fCutForProton = cut;
    SetParticleCuts(fCutForProton, G4Proton::Proton());
}
