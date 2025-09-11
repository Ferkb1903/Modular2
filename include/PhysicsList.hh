#ifndef PhysicsList_h
#define PhysicsList_h 1

#include "G4VModularPhysicsList.hh"
#include "globals.hh"

class G4VPhysicsConstructor;

/// Physics list for HDR brachytherapy simulation
/// Uses low-energy electromagnetic physics for accurate dose calculations
/// around Ir-192 source (photon energies from ~60 keV to ~1.3 MeV)

class PhysicsList: public G4VModularPhysicsList
{
public:
    PhysicsList();
    virtual ~PhysicsList();

    virtual void SetCuts();
    virtual void ConstructParticle();
    virtual void ConstructProcess();

    // Set production cuts
    void SetGammaCut(G4double cut);
    void SetElectronCut(G4double cut);
    void SetPositronCut(G4double cut);
    void SetProtonCut(G4double cut);

private:
    G4VPhysicsConstructor* fEmPhysicsList;
    G4VPhysicsConstructor* fDecayPhysicsList;
    G4VPhysicsConstructor* fRadioactiveDecayList;

    G4double fCutForGamma;
    G4double fCutForElectron;
    G4double fCutForPositron;
    G4double fCutForProton;
};

#endif
