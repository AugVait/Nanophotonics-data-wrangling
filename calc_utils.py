import numpy as np
from typing import Tuple


def calculate_integrated_intensity(
    data: np.ndarray,
    wavelength_range: Tuple[float, float]
) -> np.ndarray:
    """
    Compute integrated intensity over a wavelength range for each spectrum in `data`.
    """
    wavelengths = data[:, 0]
    intensities = data[:, 1:]
    mask = (wavelengths >= wavelength_range[0]) & (wavelengths <= wavelength_range[1])
    integrated = intensities[mask, :].sum(axis=0)
    return integrated


def calculate_weighted_mean_emission_wavelength(
    data: np.ndarray,
    wavelength_range: Tuple[float, float]
) -> np.ndarray:
    """
    Compute weighted mean emission wavelength within a range for each spectrum.
    """
    wavelengths = data[:, 0]
    intensities = data[:, 1:]
    mask = (wavelengths >= wavelength_range[0]) & (wavelengths <= wavelength_range[1])
    wl = wavelengths[mask]
    intens = intensities[mask, :]
    weighted_means = (wl[:, None] * intens).sum(axis=0) / intens.sum(axis=0)
    return weighted_means


def calculate_fwhm(
    data: np.ndarray,
    wavelength_range: Tuple[float, float]
) -> np.ndarray:
    """
    Compute Full-Width at Half-Maximum (FWHM) for each spectrum in the range.
    """
    wavelengths = data[:, 0]
    intensities = data[:, 1:]
    mask = (wavelengths >= wavelength_range[0]) & (wavelengths <= wavelength_range[1])
    wl = wavelengths[mask]
    intens = intensities[mask, :]
    fwhm_list = []
    for col in range(intens.shape[1]):
        y = intens[:, col]
        half = y.max() / 2.0
        idx = np.where(y >= half)[0]
        if idx.size:
            fwhm_val = wl[idx[-1]] - wl[idx[0]]
        else:
            fwhm_val = 0.0
        fwhm_list.append(fwhm_val)
    return np.array(fwhm_list)


def to_square(
    array_1d: np.ndarray
) -> np.ndarray:
    """
    Reshape a 1D array to a square 2D array if length is a perfect square.
    """
    length = array_1d.size
    side = int(np.sqrt(length))
    if side * side != length:
        raise ValueError(f"Array length {length} is not a perfect square.")
    return array_1d.reshape(side, side)

def convert_wavelength_to_energy_jacobian(
    wavelength: np.ndarray,
    intensity: np.ndarray,
    hc: float = 1240.0
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert a spectrum from wavelength-domain to energy-domain using Jacobian correction.

    Parameters
    ----------
    wavelength : np.ndarray
        Wavelength array in nm.
    intensity : np.ndarray
        Intensity array per nm corresponding to wavelength.
    hc : float, optional
        Planck constant times speed of light in eV·nm (default 1240.0).

    Returns
    -------
    energy : np.ndarray
        Energy array in eV, sorted ascending.
    intensity_e : np.ndarray
        Converted intensity per eV.
    """
    # Compute energy from wavelength
    energy = hc / wavelength
    # Jacobian factor |dλ/dE| = wavelength^2 / hc
    jacobian = (wavelength ** 2) / hc
    intensity_e = intensity * jacobian
    # Sort by energy
    idx = np.argsort(energy)
    return energy[idx], intensity_e[idx]


if __name__ == "__main__":
    # Demo generating a 5x5 distribution
    demo_range = (450, 650)
    x = np.linspace(400, 700, 301)
    # Create 25 synthetic spectra (two peaks + noise)
    intensities = [
        np.exp(-0.5 * ((x - 550) / 20) ** 2)
        + np.exp(-0.5 * ((x - 500) / 15) ** 2)
        + np.random.normal(scale=0.05, size=x.size)
        for _ in range(25)
    ]
    data = np.column_stack((x, *intensities))  # shape (301, 26)

    ii = calculate_integrated_intensity(data, demo_range)
    wm = calculate_weighted_mean_emission_wavelength(data, demo_range)
    fwhm = calculate_fwhm(data, demo_range)

    print('Integrated Intensities (length 25):', ii)
    print('Weighted Means (length 25):', wm)
    print('FWHM values (length 25):', fwhm)

    # Reshape to 5x5
    ii_square = to_square(ii)
    wm_square = to_square(wm)
    fwhm_square = to_square(fwhm)

    print('II square shape:', ii_square.shape)
    print('WM square shape:', wm_square.shape)
    print('FWHM square shape:', fwhm_square.shape)
