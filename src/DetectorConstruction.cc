#include "DetectorConstruction.hh"

#include "G4RunManager.hh"
#include "G4NistManager.hh"
#include "G4Box.hh"
#include "G4Tubs.hh"
#include "G4Sphere.hh"
#include "G4Ellipsoid.hh"
#include "G4LogicalVolume.hh"
#include "G4PVPlacement.hh"
#include "G4SystemOfUnits.hh"
#include "G4PhysicalConstants.hh"
#include "G4VisAttributes.hh"
#include "G4Colour.hh"
#include "G4GlobalMagFieldMessenger.hh"
#include "G4AutoDelete.hh"

DetectorConstruction::DetectorConstruction()
: G4VUserDetectorConstruction(),
  fLogicWorld(nullptr), fPhysWorld(nullptr),
  fWaterPhantom(nullptr), fSource(nullptr),
  fBladder(nullptr), fRectum(nullptr),
  fTG43Mode(true), fHeterogeneousMode(false), fApplicatorMode(false),
  fWorldSize(1.0*m), fPhantomSize(30.0*cm),
  fSourceLength(4.6*mm), fSourceRadius(0.3*mm),
  fMagFieldMessenger(nullptr), fCheckOverlaps(true)
{
}

DetectorConstruction::~DetectorConstruction()
{
}

G4VPhysicalVolume* DetectorConstruction::Construct()
{
    // Define materials
    DefineMaterials();

    // Use heterogeneous phantom (more realistic for HDR brachytherapy)
    G4cout << "Constructing heterogeneous phantom for HDR brachytherapy simulation..." << G4endl;
    return ConstructHeterogeneousPhantom();
}

void DetectorConstruction::DefineMaterials()
{
    G4NistManager* nist = G4NistManager::Instance();

    // Water (NIST material)
    fWater = nist->FindOrBuildMaterial("G4_WATER");

    // Air (NIST material)
    fAir = nist->FindOrBuildMaterial("G4_AIR");

    // Bone (NIST material - cortical bone)
    fBone = nist->FindOrBuildMaterial("G4_BONE_CORTICAL_ICRP");

    // Muscle (NIST material - skeletal muscle)
    fMuscle = nist->FindOrBuildMaterial("G4_MUSCLE_SKELETAL_ICRP");

    // Fat (NIST material - adipose tissue)
    fFat = nist->FindOrBuildMaterial("G4_ADIPOSE_TISSUE_ICRP");

    // Iridium for source
    fIridium = nist->FindOrBuildMaterial("G4_Ir");

    // Stainless steel for encapsulation
    fSteel = nist->FindOrBuildMaterial("G4_STAINLESS-STEEL");

    // Titanium for applicator
    fTitanium = nist->FindOrBuildMaterial("G4_Ti");

    // Plastic (PMMA) for applicator
    fPlastic = nist->FindOrBuildMaterial("G4_PLEXIGLASS");

    // Print materials
    G4cout << *(G4Material::GetMaterialTable()) << G4endl;
}

G4VPhysicalVolume* DetectorConstruction::ConstructTG43Phantom()
{
    // World volume - Air
    G4Box* solidWorld = new G4Box("World", 0.5*fWorldSize, 0.5*fWorldSize, 0.5*fWorldSize);
    fLogicWorld = new G4LogicalVolume(solidWorld, fAir, "World");
    fPhysWorld = new G4PVPlacement(0,                     // no rotation
                                   G4ThreeVector(),       // at (0,0,0)
                                   fLogicWorld,           // its logical volume
                                   "World",               // its name
                                   0,                     // its mother volume
                                   false,                 // no boolean operation
                                   0,                     // copy number
                                   fCheckOverlaps);       // overlaps checking

    // Water phantom for TG-43 validation
    G4Box* solidPhantom = new G4Box("WaterPhantom", 
                                    0.5*fPhantomSize, 0.5*fPhantomSize, 0.5*fPhantomSize);
    G4LogicalVolume* logicPhantom = new G4LogicalVolume(solidPhantom, fWater, "WaterPhantom");
    fWaterPhantom = new G4PVPlacement(0,                    // no rotation
                                      G4ThreeVector(),      // at (0,0,0)
                                      logicPhantom,         // its logical volume
                                      "WaterPhantom",       // its name
                                      fLogicWorld,          // its mother volume
                                      false,                // no boolean operation
                                      0,                    // copy number
                                      fCheckOverlaps);      // overlaps checking

    // Ir-192 HDR source (simplified cylindrical geometry)
    ConstructIr192Source();

    // Set visualization attributes
    G4VisAttributes* worldVisAtt = new G4VisAttributes(G4Colour(1.0, 1.0, 1.0, 0.1));
    worldVisAtt->SetVisibility(false);
    fLogicWorld->SetVisAttributes(worldVisAtt);

    G4VisAttributes* phantomVisAtt = new G4VisAttributes(G4Colour(0.0, 0.0, 1.0, 0.3));
    logicPhantom->SetVisAttributes(phantomVisAtt);

    return fPhysWorld;
}

void DetectorConstruction::ConstructIr192Source()
{
    // HDR Ir-192 source - simplified geometry based on GammaMed Plus
    // Active core: Ir-192 cylinder
    G4Tubs* solidSourceCore = new G4Tubs("SourceCore",
                                         0.0*mm,           // inner radius
                                         fSourceRadius,    // outer radius
                                         0.5*fSourceLength, // half length
                                         0.*deg,           // starting angle
                                         360.*deg);        // spanning angle

    G4LogicalVolume* logicSourceCore = new G4LogicalVolume(solidSourceCore, fIridium, "SourceCore");

    fSource = new G4PVPlacement(0,                        // no rotation
                                G4ThreeVector(0, 0, 0),   // at center
                                logicSourceCore,          // its logical volume
                                "SourceCore",             // its name
                                fLogicWorld,              // its mother volume
                                false,                    // no boolean operation
                                0,                        // copy number
                                fCheckOverlaps);          // overlaps checking

    // Encapsulation (simplified - stainless steel cylinder)
    G4double encapThickness = 0.1*mm;
    G4Tubs* solidEncap = new G4Tubs("SourceEncap",
                                    fSourceRadius,                    // inner radius
                                    fSourceRadius + encapThickness,  // outer radius
                                    0.5*(fSourceLength + 2*encapThickness), // half length
                                    0.*deg,                          // starting angle
                                    360.*deg);                       // spanning angle

    G4LogicalVolume* logicEncap = new G4LogicalVolume(solidEncap, fSteel, "SourceEncap");

    new G4PVPlacement(0,                        // no rotation
                      G4ThreeVector(0, 0, 0),   // at center
                      logicEncap,               // its logical volume
                      "SourceEncap",            // its name
                      fLogicWorld,              // its mother volume
                      false,                    // no boolean operation
                      0,                        // copy number
                      fCheckOverlaps);          // overlaps checking

    // Set visualization attributes
    G4VisAttributes* sourceVisAtt = new G4VisAttributes(G4Colour(1.0, 1.0, 0.0, 0.8));
    logicSourceCore->SetVisAttributes(sourceVisAtt);

    G4VisAttributes* encapVisAtt = new G4VisAttributes(G4Colour(0.5, 0.5, 0.5, 0.8));
    logicEncap->SetVisAttributes(encapVisAtt);
}

G4VPhysicalVolume* DetectorConstruction::ConstructHeterogeneousPhantom()
{
    // Create heterogeneous phantom with realistic anatomy
    G4cout << "Constructing heterogeneous phantom..." << G4endl;

    // World volume
    G4Box* solidWorld = new G4Box("World", 15*cm, 15*cm, 15*cm);
    G4LogicalVolume* logicWorld = new G4LogicalVolume(solidWorld, fAir, "World");
    G4VPhysicalVolume* physWorld = new G4PVPlacement(0, G4ThreeVector(), logicWorld, "World", 0, false, 0);

    // Main phantom body - muscle tissue base
    G4Box* solidPhantom = new G4Box("Phantom", 10*cm, 10*cm, 10*cm);
    G4LogicalVolume* logicPhantom = new G4LogicalVolume(solidPhantom, fMuscle, "Phantom");
    new G4PVPlacement(0, G4ThreeVector(), logicPhantom, "Phantom", logicWorld, false, 0);

    // Fat layer (subcutaneous)
    G4Box* solidFatLayer = new G4Box("FatLayer", 9.5*cm, 9.5*cm, 1.5*cm);
    G4LogicalVolume* logicFatLayer = new G4LogicalVolume(solidFatLayer, fFat, "FatLayer");
    new G4PVPlacement(0, G4ThreeVector(0, 0, 8.5*cm), logicFatLayer, "FatLayer", logicWorld, false, 0);

    // Bone structure - vertebral column simulation
    G4Box* solidBoneVertebra = new G4Box("BoneVertebra", 2*cm, 2*cm, 6*cm);
    G4LogicalVolume* logicBoneVertebra = new G4LogicalVolume(solidBoneVertebra, fBone, "BoneVertebra");
    new G4PVPlacement(0, G4ThreeVector(0, -6*cm, 0), logicBoneVertebra, "BoneVertebra", logicWorld, false, 0);

    // Rib bones
    G4LogicalVolume* logicRib = nullptr;
    for(int i = -2; i <= 2; i++) {
        G4Box* solidRib = new G4Box("Rib", 6*cm, 0.5*cm, 0.5*cm);
        logicRib = new G4LogicalVolume(solidRib, fBone, "Rib");
        new G4PVPlacement(0, G4ThreeVector(0, -3*cm, i*2.5*cm), logicRib, "Rib", logicWorld, false, i+10);
    }

    // Air cavities - lung simulation
    G4Ellipsoid* solidLungL = new G4Ellipsoid("LungL", 3*cm, 4*cm, 6*cm);
    G4LogicalVolume* logicLungL = new G4LogicalVolume(solidLungL, fAir, "LungL");
    new G4PVPlacement(0, G4ThreeVector(-4*cm, 2*cm, 2*cm), logicLungL, "LungL", logicWorld, false, 0);

    G4Ellipsoid* solidLungR = new G4Ellipsoid("LungR", 3*cm, 4*cm, 6*cm);
    G4LogicalVolume* logicLungR = new G4LogicalVolume(solidLungR, fAir, "LungR");
    new G4PVPlacement(0, G4ThreeVector(4*cm, 2*cm, 2*cm), logicLungR, "LungR", logicWorld, false, 1);

    // Critical organs at risk (OARs)
    // Spinal cord (water equivalent)
    G4Tubs* solidSpinalCord = new G4Tubs("SpinalCord", 0, 0.5*cm, 6*cm, 0, 2*M_PI);
    G4LogicalVolume* logicSpinalCord = new G4LogicalVolume(solidSpinalCord, fWater, "SpinalCord");
    new G4PVPlacement(0, G4ThreeVector(0, -6*cm, 0), logicSpinalCord, "SpinalCord", logicWorld, false, 0);

    // Tumor region (higher density tissue)
    G4Sphere* solidTumor = new G4Sphere("Tumor", 0, 2*cm, 0, 2*M_PI, 0, M_PI);
    G4LogicalVolume* logicTumor = new G4LogicalVolume(solidTumor, fMuscle, "Tumor");
    new G4PVPlacement(0, G4ThreeVector(0, 0, 0), logicTumor, "Tumor", logicWorld, false, 0);

    // Set visualization attributes
    G4VisAttributes* muscleVisAtt = new G4VisAttributes(G4Colour(1.0, 0.6, 0.6, 0.8));
    logicPhantom->SetVisAttributes(muscleVisAtt);

    G4VisAttributes* fatVisAtt = new G4VisAttributes(G4Colour(1.0, 1.0, 0.6, 0.8));
    logicFatLayer->SetVisAttributes(fatVisAtt);

    G4VisAttributes* boneVisAtt = new G4VisAttributes(G4Colour(0.9, 0.9, 0.9, 0.9));
    logicBoneVertebra->SetVisAttributes(boneVisAtt);
    logicRib->SetVisAttributes(boneVisAtt);

    G4VisAttributes* airVisAtt = new G4VisAttributes(G4Colour(0.7, 0.9, 1.0, 0.3));
    logicLungL->SetVisAttributes(airVisAtt);
    logicLungR->SetVisAttributes(airVisAtt);

    G4VisAttributes* cordVisAtt = new G4VisAttributes(G4Colour(0.0, 1.0, 0.0, 0.8));
    logicSpinalCord->SetVisAttributes(cordVisAtt);

    G4VisAttributes* tumorVisAtt = new G4VisAttributes(G4Colour(1.0, 0.0, 0.0, 0.9));
    logicTumor->SetVisAttributes(tumorVisAtt);

    // Position HDR source at center of tumor
    ConstructIr192Source();

    return physWorld;
}

void DetectorConstruction::ConstructApplicator()
{
    // Applicator construction (titanium or plastic cylinder)
    if (!fApplicatorMode) return;

    G4double applicatorInnerRadius = 2.0*mm;
    G4double applicatorOuterRadius = 3.0*mm;
    G4double applicatorLength = 20.0*mm;

    G4Tubs* solidApplicator = new G4Tubs("Applicator",
                                         applicatorInnerRadius,
                                         applicatorOuterRadius,
                                         0.5*applicatorLength,
                                         0.*deg,
                                         360.*deg);

    G4LogicalVolume* logicApplicator = new G4LogicalVolume(solidApplicator, fTitanium, "Applicator");

    new G4PVPlacement(0,                        // no rotation
                      G4ThreeVector(0, 0, 0),   // at center
                      logicApplicator,          // its logical volume
                      "Applicator",             // its name
                      fLogicWorld,              // its mother volume
                      false,                    // no boolean operation
                      0,                        // copy number
                      fCheckOverlaps);          // overlaps checking
}

void DetectorConstruction::ConstructOARs()
{
    // Construct Organs at Risk (bladder and rectum as ellipsoids)
    
    // Bladder - ellipsoid at 2 cm from source
    G4double bladderA = 2.0*cm;   // semi-axis a
    G4double bladderB = 1.5*cm;   // semi-axis b  
    G4double bladderC = 1.5*cm;   // semi-axis c

    G4Ellipsoid* solidBladder = new G4Ellipsoid("Bladder", bladderA, bladderB, bladderC);
    G4LogicalVolume* logicBladder = new G4LogicalVolume(solidBladder, fMuscle, "Bladder");

    fBladder = new G4PVPlacement(0,                              // no rotation
                                 G4ThreeVector(0, 2.5*cm, 0),   // position
                                 logicBladder,                   // its logical volume
                                 "Bladder",                      // its name
                                 fLogicWorld,                    // its mother volume
                                 false,                          // no boolean operation
                                 0,                              // copy number
                                 fCheckOverlaps);                // overlaps checking

    // Rectum - ellipsoid at 2 cm from source (posterior)
    G4double rectumA = 1.5*cm;
    G4double rectumB = 1.0*cm;
    G4double rectumC = 3.0*cm;

    G4Ellipsoid* solidRectum = new G4Ellipsoid("Rectum", rectumA, rectumB, rectumC);
    G4LogicalVolume* logicRectum = new G4LogicalVolume(solidRectum, fMuscle, "Rectum");

    fRectum = new G4PVPlacement(0,                               // no rotation
                                G4ThreeVector(0, -2.5*cm, 0),   // position
                                logicRectum,                     // its logical volume
                                "Rectum",                        // its name
                                fLogicWorld,                     // its mother volume
                                false,                           // no boolean operation
                                0,                               // copy number
                                fCheckOverlaps);                 // overlaps checking

    // Set visualization attributes
    G4VisAttributes* bladderVisAtt = new G4VisAttributes(G4Colour(1.0, 0.0, 0.0, 0.5));
    logicBladder->SetVisAttributes(bladderVisAtt);

    G4VisAttributes* rectumVisAtt = new G4VisAttributes(G4Colour(0.0, 1.0, 0.0, 0.5));
    logicRectum->SetVisAttributes(rectumVisAtt);
}

void DetectorConstruction::ConstructSDandField()
{
    // Sensitive detectors and field setup would go here
    // This includes dose scoring volumes and magnetic field if needed

    // Create global magnetic field messenger
    // Uniform magnetic field is then created automatically if
    // the field value is not zero.
    G4ThreeVector fieldValue;
    fMagFieldMessenger = new G4GlobalMagFieldMessenger(fieldValue);
    fMagFieldMessenger->SetVerboseLevel(1);

    // Register the field messenger for deleting
    G4AutoDelete::Register(fMagFieldMessenger);
}
