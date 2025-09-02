#include "PrimaryGeneratorAction.hh"

#include "G4LogicalVolumeStore.hh"
#include "G4LogicalVolume.hh"
#include "G4Box.hh"
#include "G4RunManager.hh"
#include "G4ParticleGun.hh"
#include "G4ParticleTable.hh"
#include "G4ParticleDefinition.hh"
#include "G4SystemOfUnits.hh"
#include "Randomize.hh"

// Ir-192 gamma spectrum data (main lines)
const G4double PrimaryGeneratorAction::fGammaEnergies[fNGammaLines] = {
    295.96*keV, 308.45*keV, 316.51*keV, 468.07*keV, 588.58*keV,
    604.41*keV, 612.46*keV, 884.54*keV, 924.5*keV, 1061.48*keV
};

const G4double PrimaryGeneratorAction::fGammaIntensities[fNGammaLines] = {
    28.7, 29.7, 82.8, 47.8, 4.5,
    8.2, 5.3, 2.9, 1.4, 0.6
};

PrimaryGeneratorAction::PrimaryGeneratorAction()
: G4VUserPrimaryGeneratorAction(),
  fParticleGun(0), 
  fEnvelopeBox(0),
  fSourceActivity(370e9), // 370 GBq = 10 Ci (typical HDR source)
  fSourcePosition(0, 0, 0)
{
    G4int n_particle = 1;
    fParticleGun = new G4ParticleGun(n_particle);

    // Default particle kinematic
    G4ParticleTable* particleTable = G4ParticleTable::GetParticleTable();
    G4String particleName;
    G4ParticleDefinition* particle = particleTable->FindParticle(particleName="gamma");
    fParticleGun->SetParticleDefinition(particle);
    fParticleGun->SetParticleMomentumDirection(G4ThreeVector(0.,0.,1.));
    fParticleGun->SetParticleEnergy(316.51*keV); // Main Ir-192 line
}

PrimaryGeneratorAction::~PrimaryGeneratorAction()
{
    delete fParticleGun;
}

void PrimaryGeneratorAction::GeneratePrimaries(G4Event* anEvent)
{
    // This function is called at the beginning of each event

    // Sample gamma energy from Ir-192 spectrum
    G4double energy, probability;
    SampleIr192Spectrum(energy, probability);
    
    fParticleGun->SetParticleEnergy(energy);

    // Set position at source center
    fParticleGun->SetParticlePosition(fSourcePosition);

    // Sample isotropic direction
    G4ThreeVector direction = SampleIsotropicDirection();
    fParticleGun->SetParticleMomentumDirection(direction);

    fParticleGun->GeneratePrimaryVertex(anEvent);
}

void PrimaryGeneratorAction::SampleIr192Spectrum(G4double& energy, G4double& probability)
{
    // Sample from Ir-192 gamma spectrum using probability distribution
    G4double random = G4UniformRand();
    G4double cumulative = 0.0;
    G4double totalIntensity = 0.0;

    // Calculate total intensity
    for (G4int i = 0; i < fNGammaLines; ++i) {
        totalIntensity += fGammaIntensities[i];
    }

    // Sample energy based on intensities
    for (G4int i = 0; i < fNGammaLines; ++i) {
        cumulative += fGammaIntensities[i] / totalIntensity;
        if (random <= cumulative) {
            energy = fGammaEnergies[i];
            probability = fGammaIntensities[i] / totalIntensity;
            return;
        }
    }

    // Default to main line if sampling fails
    energy = 316.51*keV;
    probability = 0.828;
}

G4ThreeVector PrimaryGeneratorAction::SampleIsotropicDirection()
{
    // Sample isotropic direction using standard Monte Carlo method
    G4double cosTheta = 2.0 * G4UniformRand() - 1.0;
    G4double sinTheta = std::sqrt(1.0 - cosTheta * cosTheta);
    G4double phi = 2.0 * CLHEP::pi * G4UniformRand();
    
    G4double x = sinTheta * std::cos(phi);
    G4double y = sinTheta * std::sin(phi);
    G4double z = cosTheta;
    
    return G4ThreeVector(x, y, z);
}
