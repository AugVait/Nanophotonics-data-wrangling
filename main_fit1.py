import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

import io_utils
import fit_utils
import plot_utils

# === USER CONFIGURATION ===
# Base folder where outputs will be saved
OUTPUT_BASE_DIR = "fit_outputs"

# Wavelength fitting window (nm)
WAVELENGTH_MIN = 450.0
WAVELENGTH_MAX = 650.0

# Choose 'single' or 'double' Gaussian
MODEL = "double"

# Initial fit parameters as a dict, e.g.:
# For single: {'amplitude': 1.0, 'center': 550.0, 'sigma': 20.0}
# For double: {
#    'amp1': 1.0, 'cen1': 540.0, 'sigma1': 15.0,
#    'amp2': 0.5, 'cen2': 580.0, 'sigma2': 25.0
# }
# Set to None to use default guesses
# INITIAL_PARAMS = None
INITIAL_PARAMS = {
    'amp1': 8.0, 'cen1': 460.0, 'sigma1': 15.0,
    'amp2': 5, 'cen2': 550.0, 'sigma2': 25.0
 }

# Display plots interactively?
SHOW_PLOTS = False
# === END USER CONFIGURATION ===

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

# Prepare output folder
os.makedirs(OUTPUT_BASE_DIR, exist_ok=True)
sample_name = os.path.splitext(os.path.basename(FILE_PATH))[0]
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
export_dir = os.path.join(OUTPUT_BASE_DIR, f"{sample_name}_fit_{timestamp}")
os.makedirs(export_dir, exist_ok=True)
print(f"Processing '{FILE_PATH}' → outputs in {export_dir}")

# 1) Load data: shape (n_wl, n_pixels+1)
data = io_utils.load_data(FILE_PATH)

# 2) Compute average spectrum
wavelengths = data[:, 0]
intensities = data[:, 1:]
avg_intensity = intensities.mean(axis=1)

# 3) Plot & save raw average
avg_spec = np.column_stack((wavelengths, avg_intensity))
raw_plot = os.path.join(export_dir, f"{sample_name}_average_spectrum.png")
plot_utils.spectra_plot_export(avg_spec, sample_name + " (avg)", raw_plot, show=SHOW_PLOTS)

# 4) Fit the average spectrum
fig, ax = plt.subplots(figsize=(6, 4))
fit_result = fit_utils.fit_model(
    wavelengths,
    avg_intensity,
    model=MODEL,
    x_min=WAVELENGTH_MIN,
    x_max=WAVELENGTH_MAX,
    initial_params=INITIAL_PARAMS,
    ax=ax
)
ax.set_title(f"{sample_name}: avg spectrum fit")
fit_plot = os.path.join(export_dir, f"{sample_name}_average_spectrum_fit.png")
fig.tight_layout()
fig.savefig(fit_plot, dpi=300, bbox_inches="tight")
if SHOW_PLOTS:
    plt.show()
plt.close(fig)

# 5) Extract & report parameters
params = fit_utils.extract_fit_results(fit_result, model=MODEL)
print("Fit parameters for average spectrum:")
for p, v in params.items():
    print(f"  {p}: {v:.4f}")

print("Fit complete.")
