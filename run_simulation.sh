#!/bin/bash

# Build and run script for HDR Brachytherapy simulation

echo "HDR Brachytherapy Monte Carlo Simulation"
echo "======================================="

# Create build directory if it doesn't exist
if [ ! -d "build" ]; then
    mkdir build
fi

cd build

# Configure with CMake
echo "Configuring with CMake..."
cmake ..

# Build the project
echo "Building project..."
make -j$(nproc)

if [ $? -eq 0 ]; then
    echo "Build successful!"
    
    # Run TG-43 validation
    echo ""
    echo "Running TG-43 validation simulation..."
    ./hdr_brachy ../macros/run_tg43.mac
    
    # Run heterogeneous simulation  
    echo ""
    echo "Running heterogeneous phantom simulation..."
    ./hdr_brachy ../macros/run_heterogeneous.mac
    
    echo ""
    echo "Simulations complete! Check output/ directory for results."
    echo "Run 'python3 ../analysis/analyze_results.py' to analyze data."
    
else
    echo "Build failed!"
    exit 1
fi
