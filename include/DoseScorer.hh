#ifndef DoseScorer_h
#define DoseScorer_h 1

#include "G4VPrimitivScorer.hh"
#include "G4THitsMap.hh"
#include "globals.hh"

/// Dose scorer for 3D dose distribution
/// Calculates dose in water-equivalent units for TG-43 validation
/// and heterogeneous tissue analysis

class DoseScorer : public G4VPrimitiveScorer
{
public:
    DoseScorer(G4String name, G4int depth = 0);
    virtual ~DoseScorer();

    virtual G4bool ProcessHits(G4Step*, G4TouchableHistory*);
    virtual void Initialize(G4HCofThisEvent*);
    virtual void EndOfEvent(G4HCofThisEvent*);
    virtual void clear();

    // Analysis methods
    void CalculateRadialDose();
    void CalculateAngularDose();
    void ExportDoseDistribution(const G4String& filename);
    void ExportTG43Parameters(const G4String& filename);

    // TG-43 parameter getters
    G4double GetDoseRateConstant() const { return fDoseRateConstant; }
    std::vector<G4double> GetRadialDoseFunction() const { return fRadialDoseFunction; }
    std::vector<std::vector<G4double>> GetAnisotropyFunction() const { return fAnisotropyFunction; }

private:
    G4THitsMap<G4double>* fEvtMap;
    
    // TG-43 parameters
    G4double fDoseRateConstant;  // Λ (cGy⋅h⁻¹⋅U⁻¹)
    std::vector<G4double> fRadialDoseFunction;  // g(r)
    std::vector<std::vector<G4double>> fAnisotropyFunction;  // F(r,θ)

    // Scoring grid parameters
    G4int fNRadialBins;
    G4int fNAngularBins;
    G4double fMinRadius;
    G4double fMaxRadius;
    G4double fRadialBinWidth;
    G4double fAngularBinWidth;

    // Helper methods
    G4int GetRadialIndex(G4double radius);
    G4int GetAngularIndex(G4double theta);
    G4double GetVoxelVolume(G4int copyNo);
    G4double GetVoxelMass(G4int copyNo);
};

#endif
