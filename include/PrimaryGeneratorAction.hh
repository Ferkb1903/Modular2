#ifndef PrimaryGeneratorAction_h
#define PrimaryGeneratorAction_h 1

#include "G4VUserPrimaryGeneratorAction.hh"
#include "G4ParticleGun.hh"
#include "globals.hh"

class G4ParticleGun;
class G4Event;
class G4Box;

/// Primary generator action class for Ir-192 HDR source
/// 
/// Simulates the radioactive decay of Ir-192 source with:
/// - Main gamma lines: 317 keV (81%), 468 keV (47%), 296 keV (29%), etc.
/// - Beta particles from radioactive decay
/// - Proper angular distribution and source geometry

class PrimaryGeneratorAction : public G4VUserPrimaryGeneratorAction
{
public:
    PrimaryGeneratorAction();
    virtual ~PrimaryGeneratorAction();

    // method from the base class
    virtual void GeneratePrimaries(G4Event*);

    // method to access particle gun
    const G4ParticleGun* GetParticleGun() const { return fParticleGun; }

    // Methods to set source parameters
    void SetSourceActivity(G4double activity) { fSourceActivity = activity; }
    void SetSourcePosition(G4ThreeVector pos) { fSourcePosition = pos; }

private:
    void SampleIr192Spectrum(G4double& energy, G4double& probability);
    G4ThreeVector SampleIsotropicDirection();

    G4ParticleGun* fParticleGun;
    G4Box* fEnvelopeBox;

    // Source parameters
    G4double fSourceActivity;  // In Bq
    G4ThreeVector fSourcePosition;

    // Ir-192 decay data
    static const G4int fNGammaLines = 10;
    static const G4double fGammaEnergies[fNGammaLines];
    static const G4double fGammaIntensities[fNGammaLines];
};

#endif
