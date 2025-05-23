import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from tqdm import tqdm
import gc

import io_utils
import calc_utils
import fit_utils
import plot_utils
print("Importing libraries...")
# === USER CONFIGURATION ===
# Base folder where outputs will be saved
OUTPUT_BASE_DIR = "mass_fit_outputs"

# Wavelength fitting window (nm)
WAVELENGTH_MIN = 800.0
WAVELENGTH_MAX = 1300.0

# Choose 'single', 'double' or 'asymmetric' Gaussian
MODEL = "asymmetric"

# Initial fit parameters as a dict, e.g.:

# For single: {'amplitude': 1.0, 'center': 550.0, 'sigma': 20.0}
# For double: {
#    'amp1': 1.0, 'cen1': 540.0, 'sigma1': 15.0,
#    'amp2': 0.5, 'cen2': 580.0, 'sigma2': 25.0 }
# For asymetric: {
#    'amp': 100.0,'cen': 550.0,
#    'fwhm_low': 10.0, 'fwhm_high': 20.0 }

# Set to None to use default guesses
# INITIAL_PARAMS = None

INITIAL_PARAMS = {
    'amp': 100.0,'cen': 1100.0,
    'fwhm_low': 10.0, 'fwhm_high': 20.0 }
 
# Display plots interactively?
SHOW_PLOTS = False
# === END USER CONFIGURATION ===
print("User configuration complete.")
# Print user configuration
print("=== USER CONFIGURATION ===")
print(f"Output Base Directory: {OUTPUT_BASE_DIR}")
print(f"Wavelength Fitting Window: {WAVELENGTH_MIN} nm to {WAVELENGTH_MAX} nm")
print(f"Model: {MODEL}")
print(f"Initial Fit Parameters: {INITIAL_PARAMS}")
print(f"Display Plots Interactively: {SHOW_PLOTS}")
print("=== END USER CONFIGURATION ===")
# === FILE SELECTION ===
try:
    import tkinter as tk
    from tkinter import filedialog

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
    print(f"Dialog failed: {e}")
    FILE_PATH = input("Enter path to spectral data file: ")
# === END FILE SELECTION ===
print("File selection complete.")
# Prepare output directory
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
sample_name = os.path.splitext(os.path.basename(FILE_PATH))[0]
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
export_dir = os.path.join(OUTPUT_BASE_DIR, f"{sample_name}_massfit_{timestamp}")
os.makedirs(export_dir, exist_ok=True)
print(f"Processing '{FILE_PATH}' → outputs in {export_dir}")

# Load data
# Expect data[:,0]=wavelength, data[:,1:]=intensities per pixel
data = io_utils.load_data(FILE_PATH)
wavelengths = data[:, 0]
intensities = data[:, 1:]

# Compute integrated intensity, weighted mean wavelength, and FWHM per pixel
ii = calc_utils.calculate_integrated_intensity(data, (WAVELENGTH_MIN, WAVELENGTH_MAX))
wm = calc_utils.calculate_weighted_mean_emission_wavelength(data, (WAVELENGTH_MIN, WAVELENGTH_MAX))
fwhm_arr = calc_utils.calculate_fwhm(data, (WAVELENGTH_MIN, WAVELENGTH_MAX))

# Fit each spectrum and record parameters with progress bar
df_results = []
n_pixels = intensities.shape[1]
for i in tqdm(range(n_pixels), desc="Fitting spectra", unit="pixel"):
    y = intensities[:, i]
    try:
        res = fit_utils.fit_model(
            wavelengths,
            y,
            model=MODEL,
            x_min=WAVELENGTH_MIN,
            x_max=WAVELENGTH_MAX,
            initial_params=INITIAL_PARAMS,
            ax=None
        )
        params = fit_utils.extract_fit_results(res, model=MODEL)
        del res  # Free memory
    except Exception as e:
        print(f"Fit failed for pixel {i}: {e}")
        keys = INITIAL_PARAMS.keys() if INITIAL_PARAMS else []
        params = {key: np.nan for key in keys}
        params['chi_square'] = np.nan
    df_results.append(params)
    if i % 100 == 0:
        gc.collect()

# Convert to DataFrame and append intensity metrics
df = pd.DataFrame(df_results)
df['Integrated Intensity'] = ii
df['Weighted Mean'] = wm
df['FWHM'] = fwhm_arr

# Save results table
csv_path = os.path.join(export_dir, f"{sample_name}_massfit_results.csv")
df.to_csv(csv_path, index=False)
print(f"Saved fit results to {csv_path}")

# Generate spatial parameter maps and compute moments
moments = {}
for column in df.columns:
    # Skip chi_square in spatial maps if desired
    values = df[column].values
    try:
        # reshape to square
        param_map = calc_utils.to_square(values)
        # export map
        plot_utils.export_square_map(
            param_map,
            sample_name,
            export_dir,
            parameter_name=column,
            unit_label="" ,
            show=SHOW_PLOTS
        )
    except Exception:
        # cannot reshape non-square data (e.g., chi_square if fits failed)
        continue
    # Compute stat moments
    mean = np.nanmean(values)
    std = np.nanstd(values)
    moments[column] = {'mean': mean, 'std': std}
    print(f"{column}: mean={mean:.4f}, std={std:.4f}")

# Correlation matrix of all fit params plus intensity metrics
cm_data = {col: df[col].values for col in df.columns}
plot_utils.correlation_matrix_plot_export(
    cm_data,
    f"{sample_name}_param_correlation",
    export_dir,
    show=SHOW_PLOTS
)

print("Mass fit analysis complete.")
