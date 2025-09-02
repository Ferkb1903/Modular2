#ifndef DetectorConstruction_h
#define DetectorConstruction_h 1

#include "G4VUserDetectorConstruction.hh"
#include "G4VPhysicalVolume.hh"
#include "G4LogicalVolume.hh"
#include "G4Material.hh"
#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"

class G4Box;
class G4Tubs;
class G4Sphere;
class G4LogicalVolume;
class G4VPhysicalVolume;
class G4Material;
class G4UniformMagField;
class G4GlobalMagFieldMessenger;

/// Detector construction class to define materials and geometry.
/// It constructs:
/// - Water phantom for TG-43 validation
/// - Heterogeneous phantom with bone, air, muscle, and fat regions
/// - HDR Ir-192 source (GammaMed Plus or MicroSelectron geometry)
/// - Applicators (titanium/plastic cylinders)
/// - OAR volumes (bladder and rectum as ellipsoids)

class DetectorConstruction : public G4VUserDetectorConstruction
{
public:
    DetectorConstruction();
    virtual ~DetectorConstruction();

    virtual G4VPhysicalVolume* Construct();
    virtual void ConstructSDandField();

    // Get methods for volumes
    const G4VPhysicalVolume* GetWaterPhantom() const { return fWaterPhantom; }
    const G4VPhysicalVolume* GetSource() const { return fSource; }
    const G4VPhysicalVolume* GetBladder() const { return fBladder; }
    const G4VPhysicalVolume* GetRectum() const { return fRectum; }

    // Geometry selection methods
    void SetTG43Geometry(G4bool flag) { fTG43Mode = flag; }
    void SetHeterogeneousGeometry(G4bool flag) { fHeterogeneousMode = flag; }
    void SetApplicatorGeometry(G4bool flag) { fApplicatorMode = flag; }

    // Material getters
    G4Material* GetWaterMaterial() const { return fWater; }
    G4Material* GetAirMaterial() const { return fAir; }
    G4Material* GetBoneMaterial() const { return fBone; }

private:
    // Methods
    void DefineMaterials();
    G4VPhysicalVolume* ConstructTG43Phantom();
    G4VPhysicalVolume* ConstructHeterogeneousPhantom();
    void ConstructIr192Source();
    void ConstructApplicator();
    void ConstructOARs();

    // Data members
    G4LogicalVolume* fLogicWorld;
    G4VPhysicalVolume* fPhysWorld;
    G4VPhysicalVolume* fWaterPhantom;
    G4VPhysicalVolume* fSource;
    G4VPhysicalVolume* fBladder;
    G4VPhysicalVolume* fRectum;

    // Materials
    G4Material* fWater;
    G4Material* fAir;
    G4Material* fBone;
    G4Material* fMuscle;
    G4Material* fFat;
    G4Material* fIridium;
    G4Material* fSteel;
    G4Material* fTitanium;
    G4Material* fPlastic;

    // Geometry flags
    G4bool fTG43Mode;
    G4bool fHeterogeneousMode;
    G4bool fApplicatorMode;

    // Dimensions
    G4double fWorldSize;
    G4double fPhantomSize;
    G4double fSourceLength;
    G4double fSourceRadius;

    G4GlobalMagFieldMessenger* fMagFieldMessenger;

    G4bool fCheckOverlaps;
};

#endif
