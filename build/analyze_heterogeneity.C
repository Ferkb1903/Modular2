#include "TFile.h"
#include "TH2D.h"
#include "TCanvas.h"
#include "TStyle.h"
#include "TProfile.h"
#include "TLegend.h"
#include "TMath.h"
#include <iostream>

void analyze_heterogeneity() {
    // Configurar estilo
    gStyle->SetOptStat(0);
    gStyle->SetPalette(1);
    
    // Abrir archivo ROOT
    TFile *file = new TFile("brachytherapy.root", "READ");
    if (!file || file->IsZombie()) {
        std::cout << "Error: No se puede abrir brachytherapy.root" << std::endl;
        return;
    }
    
    // Obtener histograma 2D
    TH2D *h2d = (TH2D*)file->Get("h20");
    if (!h2d) {
        std::cout << "Error: No se encuentra el histograma h20" << std::endl;
        return;
    }
    
    std::cout << "=== Análisis de Heterogeneidad ===" << std::endl;
    std::cout << "Total de entradas: " << h2d->GetEntries() << std::endl;
    std::cout << "Suma total de energía: " << h2d->Integral() << " MeV" << std::endl;
    
    // Información del scoring mesh
    int nx = h2d->GetNbinsX();  // 801
    int ny = h2d->GetNbinsY();  // 801
    double xmin = h2d->GetXaxis()->GetXmin();  // -10.0125 cm
    double xmax = h2d->GetXaxis()->GetXmax();  // +10.0125 cm
    double ymin = h2d->GetYaxis()->GetXmin();  // -10.0125 cm
    double ymax = h2d->GetYaxis()->GetXmax();  // +10.0125 cm
    
    std::cout << "Dimensiones del mesh: " << nx << " x " << ny << std::endl;
    std::cout << "Rango X: " << xmin << " a " << xmax << " cm" << std::endl;
    std::cout << "Rango Y: " << ymin << " a " << ymax << " cm" << std::endl;
    
    // Canvas principal
    TCanvas *c1 = new TCanvas("c1", "Distribución Espacial de Energía", 1200, 800);
    c1->Divide(2, 2);
    
    // 1. Mapa 2D completo
    c1->cd(1);
    h2d->SetTitle("Deposición de Energía (vista completa)");
    h2d->GetXaxis()->SetTitle("X (cm)");
    h2d->GetYaxis()->SetTitle("Y (cm)");
    h2d->Draw("COLZ");
    
    // 2. Zoom en región central (fuente + heterogeneidad)
    c1->cd(2);
    TH2D *h2d_zoom = (TH2D*)h2d->Clone("h2d_zoom");
    h2d_zoom->SetTitle("Deposición de Energía (zoom central)");
    h2d_zoom->GetXaxis()->SetRangeUser(-8, 8);
    h2d_zoom->GetYaxis()->SetRangeUser(-2, 12);
    h2d_zoom->Draw("COLZ");
    
    // Agregar líneas para mostrar la región de heterogeneidad
    TLine *line1 = new TLine(-3, 3, 3, 3);  // Límite inferior del cubo
    TLine *line2 = new TLine(-3, 9, 3, 9);  // Límite superior del cubo
    TLine *line3 = new TLine(-3, 3, -3, 9); // Límite izquierdo del cubo
    TLine *line4 = new TLine(3, 3, 3, 9);   // Límite derecho del cubo
    line1->SetLineColor(kRed); line1->SetLineWidth(2);
    line2->SetLineColor(kRed); line2->SetLineWidth(2);
    line3->SetLineColor(kRed); line3->SetLineWidth(2);
    line4->SetLineColor(kRed); line4->SetLineWidth(2);
    line1->Draw("same"); line2->Draw("same"); line3->Draw("same"); line4->Draw("same");
    
    // Marcar la posición de la fuente
    TMarker *source = new TMarker(0, 0, 29);
    source->SetMarkerColor(kYellow);
    source->SetMarkerSize(2);
    source->Draw("same");
    
    // 3. Perfil en Y (corte vertical en X=0)
    c1->cd(3);
    TProfile *prof_y = h2d->ProfileY("prof_y");
    prof_y->SetTitle("Perfil de Energía vs Y (X=0)");
    prof_y->GetXaxis()->SetTitle("Y (cm)");
    prof_y->GetYaxis()->SetTitle("Energía promedio (MeV)");
    prof_y->SetLineColor(kBlue);
    prof_y->SetLineWidth(2);
    prof_y->Draw();
    
    // Agregar líneas para mostrar las fronteras de la heterogeneidad
    TLine *het_bottom = new TLine(3, prof_y->GetMinimum(), 3, prof_y->GetMaximum());
    TLine *het_top = new TLine(9, prof_y->GetMinimum(), 9, prof_y->GetMaximum());
    het_bottom->SetLineColor(kRed); het_bottom->SetLineWidth(2); het_bottom->SetLineStyle(2);
    het_top->SetLineColor(kRed); het_top->SetLineWidth(2); het_top->SetLineStyle(2);
    het_bottom->Draw("same"); het_top->Draw("same");
    
    // 4. Perfil en X (corte horizontal en Y=6, centro de la heterogeneidad)
    c1->cd(4);
    TProfile *prof_x = h2d->ProfileX("prof_x");
    prof_x->SetTitle("Perfil de Energía vs X (Y=6 cm, centro heterogeneidad)");
    prof_x->GetXaxis()->SetTitle("X (cm)");
    prof_x->GetYaxis()->SetTitle("Energía promedio (MeV)");
    prof_x->SetLineColor(kGreen);
    prof_x->SetLineWidth(2);
    prof_x->Draw();
    
    // Agregar líneas para mostrar las fronteras laterales de la heterogeneidad
    TLine *het_left = new TLine(-3, prof_x->GetMinimum(), -3, prof_x->GetMaximum());
    TLine *het_right = new TLine(3, prof_x->GetMinimum(), 3, prof_x->GetMaximum());
    het_left->SetLineColor(kRed); het_left->SetLineWidth(2); het_left->SetLineStyle(2);
    het_right->SetLineColor(kRed); het_right->SetLineWidth(2); het_right->SetLineStyle(2);
    het_left->Draw("same"); het_right->Draw("same");
    
    // Análisis cuantitativo
    std::cout << "\n=== Análisis por Regiones ===" << std::endl;
    
    // Región de agua (Y < 3 cm)
    double energy_water = 0;
    int bins_water = 0;
    
    // Región de heterogeneidad (3 < Y < 9 cm, -3 < X < 3 cm)
    double energy_hetero = 0;
    int bins_hetero = 0;
    
    // Región de agua arriba de heterogeneidad (Y > 9 cm)
    double energy_water_above = 0;
    int bins_water_above = 0;
    
    for (int i = 1; i <= nx; i++) {
        for (int j = 1; j <= ny; j++) {
            double x = h2d->GetXaxis()->GetBinCenter(i);
            double y = h2d->GetYaxis()->GetBinCenter(j);
            double energy = h2d->GetBinContent(i, j);
            
            if (energy > 0) {  // Solo contar bins con deposición
                if (y < 3) {
                    energy_water += energy;
                    bins_water++;
                } else if (y > 9) {
                    energy_water_above += energy;
                    bins_water_above++;
                } else if (y >= 3 && y <= 9 && x >= -3 && x <= 3) {
                    energy_hetero += energy;
                    bins_hetero++;
                }
            }
        }
    }
    
    std::cout << "Región de agua (Y < 3 cm):" << std::endl;
    std::cout << "  Energía total: " << energy_water << " MeV" << std::endl;
    std::cout << "  Bins activos: " << bins_water << std::endl;
    std::cout << "  Energía promedio: " << (bins_water > 0 ? energy_water/bins_water : 0) << " MeV/bin" << std::endl;
    
    std::cout << "\nRegión de heterogeneidad (hueso cortical):" << std::endl;
    std::cout << "  Energía total: " << energy_hetero << " MeV" << std::endl;
    std::cout << "  Bins activos: " << bins_hetero << std::endl;
    std::cout << "  Energía promedio: " << (bins_hetero > 0 ? energy_hetero/bins_hetero : 0) << " MeV/bin" << std::endl;
    
    std::cout << "\nRegión de agua (Y > 9 cm):" << std::endl;
    std::cout << "  Energía total: " << energy_water_above << " MeV" << std::endl;
    std::cout << "  Bins activos: " << bins_water_above << std::endl;
    std::cout << "  Energía promedio: " << (bins_water_above > 0 ? energy_water_above/bins_water_above : 0) << " MeV/bin" << std::endl;
    
    c1->SaveAs("heterogeneity_analysis.png");
    std::cout << "\nGráfico guardado como heterogeneity_analysis.png" << std::endl;
    
    file->Close();
    
    {
        TFile* file = TFile::Open("brachytherapy.root");
        if (!file) {
            cout << "Error: No se pudo abrir brachytherapy.root" << endl;
            return;
        }
        
        TH3D* h3d = (TH3D*)file->Get("eDep");
        if (!h3d) {
            cout << "Error: No se encontró el histograma eDep" << endl;
            return;
        }
        
        cout << "=== Análisis de Distribución de Energía (sin centro) ===" << endl;
        
        // Crear histograma 2D excluyendo el centro
        TH2D* h2d_filtered = new TH2D("h2d_filtered", "Distribución de Energía (sin centro);X (cm);Y (cm)", 
                                      801, -10.0125, 10.0125, 801, -10.0125, 10.0125);
        
        // Definir región central a excluir (±2 cm del centro)
        double exclude_radius = 2.0; // cm
        double max_value_allowed = 10.0; // MeV, límite superior
        
        int excluded_bins = 0;
        int total_bins = 0;
        double total_energy_excluded = 0;
        double total_energy_included = 0;
        
        // Llenar el histograma filtrado
        for (int i = 1; i <= h3d->GetNbinsX(); i++) {
            for (int j = 1; j <= h3d->GetNbinsY(); j++) {
                for (int k = 1; k <= h3d->GetNbinsZ(); k++) {
                    double x = h3d->GetXaxis()->GetBinCenter(i);
                    double y = h3d->GetYaxis()->GetBinCenter(j);
                    double energy = h3d->GetBinContent(i, j, k);
                    
                    if (energy > 0) {
                        total_bins++;
                        double distance = sqrt(x*x + y*y);
                        
                        // Excluir centro o valores muy altos
                        if (distance < exclude_radius || energy > max_value_allowed) {
                            excluded_bins++;
                            total_energy_excluded += energy;
                        } else {
                            h2d_filtered->Fill(x, y, energy);
                            total_energy_included += energy;
                        }
                    }
                }
            }
        }
        
        cout << "Bins totales con energía: " << total_bins << endl;
        cout << "Bins excluidos (centro + altos): " << excluded_bins << endl;
        cout << "Energía excluida: " << total_energy_excluded << " MeV" << endl;
        cout << "Energía incluida: " << total_energy_included << " MeV" << endl;
        cout << "Porcentaje excluido: " << (100.0 * excluded_bins / total_bins) << "%" << endl;
        
        // Crear canvas y dibujar
        TCanvas* c1 = new TCanvas("c1", "Distribución de Energía Filtrada", 1000, 800);
        c1->SetRightMargin(0.15);
        
        h2d_filtered->SetStats(0);
        h2d_filtered->Draw("COLZ");
        
        // Mejorar la paleta de colores
        gStyle->SetPalette(kRainBow);
        
        // Agregar líneas para mostrar la heterogeneidad
        TLine* het_bottom = new TLine(-3, 3, 3, 3);
        het_bottom->SetLineColor(kWhite);
        het_bottom->SetLineWidth(2);
        het_bottom->Draw();
        
        TLine* het_top = new TLine(-3, 9, 3, 9);
        het_top->SetLineColor(kWhite);
        het_top->SetLineWidth(2);
        het_top->Draw();
        
        TLine* het_left = new TLine(-3, 3, -3, 9);
        het_left->SetLineColor(kWhite);
        het_left->SetLineWidth(2);
        het_left->Draw();
        
        TLine* het_right = new TLine(3, 3, 3, 9);
        het_right->SetLineColor(kWhite);
        het_right->SetLineWidth(2);
        het_right->Draw();
        
        // Agregar texto explicativo
        TLatex* text = new TLatex();
        text->SetTextColor(kWhite);
        text->SetTextSize(0.03);
        text->DrawLatex(-2.5, 6, "Heterogeneidad");
        text->DrawLatex(-2, 5.5, "(Hueso)");
        
        // Círculo para mostrar región excluida
        TEllipse* excluded_circle = new TEllipse(0, 0, exclude_radius, exclude_radius);
        excluded_circle->SetFillStyle(0);
        excluded_circle->SetLineColor(kRed);
        excluded_circle->SetLineWidth(2);
        excluded_circle->SetLineStyle(2);
        excluded_circle->Draw();
        
        text->SetTextColor(kRed);
        text->DrawLatex(-1.5, -1.5, "Región excluida");
        
        c1->SaveAs("energy_distribution_filtered.png");
        cout << "Imagen guardada como: energy_distribution_filtered.png" << endl;
        
        // Análisis por regiones (sin centro)
        cout << "\n=== Análisis por Regiones (sin centro) ===" << endl;
        
        double energy_water_lower = 0, bins_water_lower = 0;
        double energy_heterogeneity = 0, bins_heterogeneity = 0;
        double energy_water_upper = 0, bins_water_upper = 0;
        
        for (int i = 1; i <= h2d_filtered->GetNbinsX(); i++) {
            for (int j = 1; j <= h2d_filtered->GetNbinsY(); j++) {
                double x = h2d_filtered->GetXaxis()->GetBinCenter(i);
                double y = h2d_filtered->GetYaxis()->GetBinCenter(j);
                double energy = h2d_filtered->GetBinContent(i, j);
                
                if (energy > 0 && abs(x) < 3) { // Solo dentro del ancho de la heterogeneidad
                    if (y < 3) {
                        energy_water_lower += energy;
                        bins_water_lower++;
                    } else if (y >= 3 && y <= 9) {
                        energy_heterogeneity += energy;
                        bins_heterogeneity++;
                    } else if (y > 9) {
                        energy_water_upper += energy;
                        bins_water_upper++;
                    }
                }
            }
        }
        
        cout << "Agua inferior (Y < 3): " << energy_water_lower/bins_water_lower << " MeV/bin promedio (" << bins_water_lower << " bins)" << endl;
        cout << "Heterogeneidad (3-9): " << energy_heterogeneity/bins_heterogeneity << " MeV/bin promedio (" << bins_heterogeneity << " bins)" << endl;
        cout << "Agua superior (Y > 9): " << energy_water_upper/bins_water_upper << " MeV/bin promedio (" << bins_water_upper << " bins)" << endl;
        
        if (energy_water_lower/bins_water_lower > 0) {
            double reduction = 1.0 - (energy_heterogeneity/bins_heterogeneity) / (energy_water_lower/bins_water_lower);
            cout << "Reducción por heterogeneidad: " << reduction*100 << "%" << endl;
        }
        
        file->Close();
    }
}
