# Spectral Analysis Utilities

This repository contains **Python modules** and **scripts** for processing hyperspectral data collected using the WITec Alpha 300S instrument.

This toolkit enables rapid post-processing of hyperspectral datasets by computing spatial maps, average spectra, and per-pixel model fits with different functions. Results are visualized as plots and exported as tables. In contrast to WITec software, every process is transparent and easily customizable.

## Recommended Setup

Use a Python-aware IDE (e.g., VS Code, IDLE) for syntax highlighting, code navigation, and debugging. 
CLI is not supported as you will need to input multiple parameters directly in the code. Spyder also appears to be incompatible with TKinter, so my advice is to avoid using it.

Ensure your working directory is the project root so imports resolve correctly.

### Install Dependencies

```bash
pip install numpy pandas matplotlib lmfit tqdm tkinter
```


## Scripts Overview

Three main workflows are provided as standalone scripts. Configure each at the top, then run:

| Script            | Description                                                                                      |
|-------------------|--------------------------------------------------------------------------------------------------|
| **main_basic.py** | Compute per-pixel maps (integrated intensity, mean wavelength, FWHM) and export heatmaps, pair plots, and corr matrix. |
| **main_fit1.py**  | Average all spectra into one curve, fit with a chosen distribution, and save both the raw & fitted plots.     |
| **main_fit2.py**  | "Mass fit": fit every pixel’s spectrum, save parameter table, spatial maps, distribution stats, and correlation matrix. Typically **main_fit1.py** is performed first so as to ascertain the correct initial parameters. Always make sure that both fitting scripts use the same **model**.|

## Configuration

At the top of each script, edit the **USER CONFIGURATION** block:

- `OUTPUT_BASE_DIR`: directory for all outputs.
- `WAVELENGTH_MIN`, `WAVELENGTH_MAX`: spectral range (nm) for calculations or fits.
- `MODEL`: For now the choices are `'single'`, `'double'` or `'asymmetric'` gaussian.
- `INITIAL_PARAMS`: optional dict of initial fit guesses (or `None` for defaults).
- `SHOW_PLOTS`: `True` to display plots interactively.

## Usage Example

0. Export data from WITec software, using the `Export` -> `Table` option, taking care it is background subtracted. 
1. Open the script in your IDE and configure the USER CONFIGURATION block.
2. Run.
3. A file‐selection dialog appears (or input path at prompt). Select your data file.
4. Outputs are saved in `OUTPUT_BASE_DIR/<filename>_<timestamp>/`:
   - **PNG/PDF** plots for heatmaps, spectra, distributions, and correlation matrices
   - **CSV** tables for fit parameters

## Fitting Models

The analysis scripts support multiple spectral fitting models for handling different emission lineshapes. You can select the desired model using the `MODEL` variable in the **USER CONFIGURATION** section of `main_fit1.py` or `main_fit2.py`.

### Available Models

---

### `MODEL = "single"`

Fits a **single symmetric Gaussian** function:

$$
f(x) = A \cdot \exp\left(-\frac{(x - \mu)^2}{2\sigma^2}\right)
$$


- **Parameters:**
  - `amplitude` \( A \): peak height
  - `center` \( \mu \): peak location
  - `sigma` \( \sigma \): standard deviation (width of the peak)

- **Use Case:** 
  - Clean, symmetric emission peaks
  - Simple and fast to compute

---

### `MODEL = "double"`

Fits the sum of two symmetric Gaussians:

$$
f(x) = A_1 \cdot \exp\left(-\frac{(x - \mu_1)^2}{2\sigma_1^2}\right) + A_2 \cdot \exp\left(-\frac{(x - \mu_2)^2}{2\sigma_2^2}\right)
$$

- **Parameters:**
  - `amp1`, `cen1`, `sigma1`: for the first peak
  - `amp2`, `cen2`, `sigma2`: for the second peak

- **Use Case:**
  - Overlapping peaks
  - Multi-emitter samples
  - Spectral shoulders

---

### `MODEL = "asymmetric"`

Fits an **asymmetric Gaussian** with separate FWHMs for each side of the peak:

$$
f(x) = A \cdot \exp\left(-\frac{(x - \mu)^2}{2\sigma(x)^2}\right)
$$

where

$$
\sigma(x) =
\begin{cases}
\sigma_\text{low}, & \text{if } x < \mu \\
\sigma_\text{high}, & \text{if } x \geq \mu
\end{cases}
$$


- **Parameters:**
  - `amp` \( A \): amplitude of the peak
  - `cen` \( \mu \): peak center
  - `fwhm_low`: width on the low-energy side
  - `fwhm_high`: width on the high-energy side

- **Use Case:**
  - Skewed emission lines
  - Inhomogeneous broadening

---
The conversion from full width at half maximum (FWHM) to standard deviation is:

$$
\sigma = \frac{\text{FWHM}}{2\sqrt{2 \ln 2}}
$$
## Module Reference

### `io_utils.py`
- `load_data(file_path, delimiter=None, skiprows=0) -> np.ndarray`

### `calc_utils.py`
- `calculate_integrated_intensity(data, (min, max))`
- `calculate_weighted_mean_emission_wavelength(data, (min, max))`
- `calculate_fwhm(data, (min, max))`
- `to_square(array_1d)`
- `convert_wavelength_to_energy_jacobian(wavelength, intensity, hc=1240.0)`

### `fit_utils.py`
- `fit_model(x, y, model, x_min, x_max, initial_params, ax)`
- `extract_fit_results(result, model) -> dict`

### `plot_utils.py`
- `spectra_plot_export(data, sample_name, output_path, x_limits=(400,800), show=True)`
- `export_square_map(map_data, sample_name, output_dir, parameter_name, unit_label, physical_size_um, show)`
- `pair_plot_with_histograms_export(datX, datY, X_label, X_units, Y_label, Y_units, sample_field_name, output_dir, show)`
- `correlation_matrix_plot_export(data_arrays, sample_name, output_dir, show)`

---

Enhancements, bug reports, and contributions are welcome—feel free to open issues or pull requests.

