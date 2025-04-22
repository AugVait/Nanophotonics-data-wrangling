#!/usr/bin/env python3
"""
main.py: Spectral data processing for a single file with file-selection dialog.
Automatically executes on run without function encapsulation.
Output directory includes file name and timestamp.
"""
import os
import numpy as np
from datetime import datetime
import tkinter as tk
from tkinter import filedialog

import io_utils
import calc_utils
import plot_utils

# === USER CONFIGURATION ===
# Directory where outputs will be saved
OUTPUT_BASE_DIR = "outputs"

# Wavelength calculation range (nm)
WAVELENGTH_MIN = 450.0
WAVELENGTH_MAX = 650.0

# Display plots interactively? (True or False)
SHOW_PLOTS = False
# === END USER CONFIGURATION ===

# === FILE SELECTION ===
try:
    root = tk.Tk()
    root.withdraw()
    FILE_PATH = filedialog.askopenfilename(
        title="Select spectral data file",
        filetypes=[("Text/CSV files", "*.txt *.csv"), ("All files", "*.*")]
    )
    root.destroy()
    if not FILE_PATH:
        raise RuntimeError("No file selected.")
except Exception as e:
    print(f"File dialog unavailable or cancelled: {e}")
    FILE_PATH = input("Enter path to spectral data file: ")
# === END FILE SELECTION ===

# Ensure base output directory exists
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)

# Derive sample name and create timestamped export folder
sample_name = os.path.splitext(os.path.basename(FILE_PATH))[0]
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
export_dir = os.path.join(OUTPUT_BASE_DIR, f"{sample_name}_{timestamp}")
os.makedirs(export_dir, exist_ok=True)
print(f"Processing '{FILE_PATH}' → outputs in {export_dir}")

# Load data
data = io_utils.load_data(FILE_PATH, delimiter="\t", skiprows=0)
# Check data shape
if data.ndim != 2 or data.shape[1] < 2:
    raise ValueError("Data must be a 2D array with at least two columns (wavelength and intensity).")

# Compute distributions
ii = calc_utils.calculate_integrated_intensity(data, (WAVELENGTH_MIN, WAVELENGTH_MAX))
wm = calc_utils.calculate_weighted_mean_emission_wavelength(data, (WAVELENGTH_MIN, WAVELENGTH_MAX))
fwhm = calc_utils.calculate_fwhm(data, (WAVELENGTH_MIN, WAVELENGTH_MAX))

# Reshape to square maps
ii_map = calc_utils.to_square(ii)
wm_map = calc_utils.to_square(wm)
fwhm_map = calc_utils.to_square(fwhm)

# Export heatmaps
plot_utils.export_square_map(
    ii_map, sample_name, export_dir,
    "Integrated Intensity", unit_label="a.u.", show=SHOW_PLOTS
)
plot_utils.export_square_map(
    wm_map, sample_name, export_dir,
    "Weighted Mean Emission Wavelength", unit_label="nm", show=SHOW_PLOTS
)
plot_utils.export_square_map(
    fwhm_map, sample_name, export_dir,
    "FWHM", unit_label="nm", show=SHOW_PLOTS
)

# Correlation matrix
data_arrays = {"Integrated Intensity": ii, "Weighted Mean": wm, "FWHM": fwhm}
plot_utils.correlation_matrix_plot_export(
    data_arrays, sample_name, export_dir, show=SHOW_PLOTS
)

# Pair plot between II and WM
plot_utils.pair_plot_with_histograms_export(
    ii, wm,
    "Integrated Intensity", " a.u.",
    "Weighted Mean Wavelength", " nm",
    sample_name, export_dir,
    show=SHOW_PLOTS
)

print("Processing complete.")
