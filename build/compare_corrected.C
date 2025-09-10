#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <map>
#include <utility>

void compare_corrected() {
    cout << "=== COMPARACIÓN RIGUROSA: HOMOGÉNEO vs HETEROGÉNEO ===" << endl;
    
    // Leer datos homogéneos (solo agua)
    ifstream file_homo("EnergyDeposition_Flexi_water.out");
    if (!file_homo.is_open()) {
        cout << "Error: No se pudo abrir EnergyDeposition_Flexi_water.out" << endl;
        return;
    }
    
    // Leer datos heterogéneos (agua + grasa)
    ifstream file_hetero("EnergyDeposition_Flexi_fat.out");
    if (!file_hetero.is_open()) {
        cout << "Error: No se pudo abrir EnergyDeposition_Flexi_fat.out" << endl;
        return;
    }
    
    // Mapas para almacenar datos por posición (x,y) -> energía
    map<pair<double,double>, double> energy_homo;
    map<pair<double,double>, double> energy_hetero;
    
    string line;
    
    // Leer datos homogéneos
    // Skip header lines
    while (getline(file_homo, line) && line.substr(0, 1) == "#") {
        // Skip header lines
    }
    int total_homo = 0;
    int energy_voxels_homo = 0;
    
    // Process first data line (already read)
    if (!line.empty()) {
        istringstream iss(line);
        double x, y, z, energy;
        if (iss >> x >> y >> z >> energy) {
            total_homo++;
            if (energy > 0) {
                energy_homo[make_pair(x,y)] = energy;
                energy_voxels_homo++;
            }
        }
    }
    
    // Continue reading data
    while (getline(file_homo, line)) {
        if (line.empty() || line.substr(0, 1) == "#") continue;
        istringstream iss(line);
        double x, y, z, energy;
        if (iss >> x >> y >> z >> energy) {
            total_homo++;
            if (energy > 0) {
                energy_homo[make_pair(x,y)] = energy;
                energy_voxels_homo++;
            }
        }
    }
    file_homo.close();
    
    // Leer datos heterogéneos
    // Skip header lines
    while (getline(file_hetero, line) && line.substr(0, 1) == "#") {
        // Skip header lines
    }
    int total_hetero = 0;
    int energy_voxels_hetero = 0;
    
    // Process first data line (already read)
    if (!line.empty()) {
        istringstream iss(line);
        double x, y, z, energy;
        if (iss >> x >> y >> z >> energy) {
            total_hetero++;
            if (energy > 0) {
                energy_hetero[make_pair(x,y)] = energy;
                energy_voxels_hetero++;
            }
        }
    }
    
    // Continue reading data
    while (getline(file_hetero, line)) {
        if (line.empty() || line.substr(0, 1) == "#") continue;
        istringstream iss(line);
        double x, y, z, energy;
        if (iss >> x >> y >> z >> energy) {
            total_hetero++;
            if (energy > 0) {
                energy_hetero[make_pair(x,y)] = energy;
                energy_voxels_hetero++;
            }
        }
    }
    file_hetero.close();
    
    cout << "Voxeles totales (homogéneo): " << total_homo << endl;
    cout << "Voxeles totales (heterogéneo): " << total_hetero << endl;
    cout << "Voxeles con energía (homogéneo): " << energy_voxels_homo << endl;
    cout << "Voxeles con energía (heterogéneo): " << energy_voxels_hetero << endl;
    
    // Calcular estadísticas globales
    double total_energy_homo = 0;
    double total_energy_hetero = 0;
    
    for (const auto& entry : energy_homo) {
        total_energy_homo += entry.second;
    }
    
    for (const auto& entry : energy_hetero) {
        total_energy_hetero += entry.second;
    }
    
    cout << "\nEstadísticas Globales:" << endl;
    cout << "Energía total (homogéneo): " << total_energy_homo << " MeV" << endl;
    cout << "Energía total (heterogéneo): " << total_energy_hetero << " MeV" << endl;
    
    // Encontrar voxeles coincidentes
    int coincident_voxels = 0;
    double ratio_sum = 0;
    double max_ratio = 0;
    double min_ratio = 1e6;
    
    for (const auto& entry_homo : energy_homo) {
        auto pos = entry_homo.first;
        auto it_hetero = energy_hetero.find(pos);
        if (it_hetero != energy_hetero.end()) {
            coincident_voxels++;
            double ratio = it_hetero->second / entry_homo.second;
            ratio_sum += ratio;
            if (ratio > max_ratio) max_ratio = ratio;
            if (ratio < min_ratio) min_ratio = ratio;
        }
    }
    
    cout << "Voxeles coincidentes: " << coincident_voxels << endl;
    cout << "Ratio energía total: " << (total_homo > 0 ? total_energy_hetero/total_energy_homo : 0) << endl;
    
    if (coincident_voxels > 0) {
        cout << "Ratio promedio (hetero/homo): " << ratio_sum/coincident_voxels << endl;
        cout << "Ratio máximo: " << max_ratio << endl;
        cout << "Ratio mínimo: " << min_ratio << endl;
    }
    
    // Análisis por regiones anatómicas
    cout << "\n=== ANÁLISIS POR REGIONES ANATÓMICAS ===" << endl;
    
    // Región cerca de la fuente (r < 20mm)
    double energy_homo_near = 0, energy_hetero_near = 0;
    int voxels_near = 0;
    
    // Región media (20mm < r < 50mm)
    double energy_homo_mid = 0, energy_hetero_mid = 0;
    int voxels_mid = 0;
    
    // Región lejana (r > 50mm)
    double energy_homo_far = 0, energy_hetero_far = 0;
    int voxels_far = 0;
    
    for (const auto& entry_homo : energy_homo) {
        double x = entry_homo.first.first;
        double y = entry_homo.first.second;
        double r = sqrt(x*x + y*y);
        
        auto it_hetero = energy_hetero.find(entry_homo.first);
        if (it_hetero != energy_hetero.end()) {
            if (r < 20) {
                energy_homo_near += entry_homo.second;
                energy_hetero_near += it_hetero->second;
                voxels_near++;
            } else if (r < 50) {
                energy_homo_mid += entry_homo.second;
                energy_hetero_mid += it_hetero->second;
                voxels_mid++;
            } else {
                energy_homo_far += entry_homo.second;
                energy_hetero_far += it_hetero->second;
                voxels_far++;
            }
        }
    }
    
    cout << "Región cercana (r < 20mm):" << endl;
    cout << "  Voxeles: " << voxels_near << endl;
    cout << "  Energía homo: " << energy_homo_near << " MeV" << endl;
    cout << "  Energía hetero: " << energy_hetero_near << " MeV" << endl;
    cout << "  Ratio: " << (energy_homo_near > 0 ? energy_hetero_near/energy_homo_near : 0) << endl;
    
    cout << "Región media (20-50mm):" << endl;
    cout << "  Voxeles: " << voxels_mid << endl;
    cout << "  Energía homo: " << energy_homo_mid << " MeV" << endl;
    cout << "  Energía hetero: " << energy_hetero_mid << " MeV" << endl;
    cout << "  Ratio: " << (energy_homo_mid > 0 ? energy_hetero_mid/energy_homo_mid : 0) << endl;
    
    cout << "Región lejana (r > 50mm):" << endl;
    cout << "  Voxeles: " << voxels_far << endl;
    cout << "  Energía homo: " << energy_homo_far << " MeV" << endl;
    cout << "  Energía hetero: " << energy_hetero_far << " MeV" << endl;
    cout << "  Ratio: " << (energy_homo_far > 0 ? energy_hetero_far/energy_homo_far : 0) << endl;
    
    // Crear histogramas para visualización
    TH2D* h_homo = new TH2D("h_homo", "Energía - Homogéneo (agua)", 201, -100.5, 100.5, 201, -100.5, 100.5);
    TH2D* h_hetero = new TH2D("h_hetero", "Energía - Heterogéneo (agua+grasa)", 201, -100.5, 100.5, 201, -100.5, 100.5);
    TH2D* h_ratio = new TH2D("h_ratio", "Ratio Heterogéneo/Homogéneo", 201, -100.5, 100.5, 201, -100.5, 100.5);
    
    // Llenar histogramas
    for (const auto& entry_homo : energy_homo) {
        double x = entry_homo.first.first;
        double y = entry_homo.first.second;
        h_homo->Fill(x, y, entry_homo.second);
        
        auto it_hetero = energy_hetero.find(entry_homo.first);
        if (it_hetero != energy_hetero.end()) {
            h_hetero->Fill(x, y, it_hetero->second);
            if (entry_homo.second > 0) {
                h_ratio->Fill(x, y, it_hetero->second / entry_homo.second);
            }
        }
    }
    
    // Crear canvas para mostrar resultados
    TCanvas* c1 = new TCanvas("c1", "Comparación Homogéneo vs Heterogéneo", 1800, 600);
    c1->Divide(3, 1);
    
    c1->cd(1);
    h_homo->SetTitle("Distribución Homogénea (agua)");
    h_homo->GetXaxis()->SetTitle("X (mm)");
    h_homo->GetYaxis()->SetTitle("Y (mm)");
    h_homo->Draw("colz");
    
    c1->cd(2);
    h_hetero->SetTitle("Distribución Heterogénea (agua+grasa)");
    h_hetero->GetXaxis()->SetTitle("X (mm)");
    h_hetero->GetYaxis()->SetTitle("Y (mm)");
    h_hetero->Draw("colz");
    
    c1->cd(3);
    h_ratio->SetTitle("Ratio Heterogéneo/Homogéneo");
    h_ratio->GetXaxis()->SetTitle("X (mm)");
    h_ratio->GetYaxis()->SetTitle("Y (mm)");
    h_ratio->SetMinimum(0.5);
    h_ratio->SetMaximum(1.5);
    h_ratio->Draw("colz");
    
    c1->SaveAs("comparison_homo_vs_hetero.png");
    
    cout << "\n=== RESUMEN ===" << endl;
    cout << "La comparación muestra el efecto de las heterogeneidades de grasa" << endl;
    cout << "vs el caso homogéneo de solo agua." << endl;
    cout << "Gráficos guardados como: comparison_homo_vs_hetero.png" << endl;
}
