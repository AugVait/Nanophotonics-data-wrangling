import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
from mpl_toolkits.axes_grid1 import make_axes_locatable


def set_plot_style(
    style: str = 'default',
    font_family: str = 'sans-serif',
    font_size: int = 12,
    tick_direction: str = 'in',
    grid: bool = False
) -> None:
    """
    Configure a consistent plotting theme across all functions.
    """
    plt.style.use(style)
    plt.rcParams.update({
        'font.family': font_family,
        'font.size': font_size,
        'axes.titlesize': font_size * 1.2,
        'axes.labelsize': font_size,
        'xtick.direction': tick_direction,
        'ytick.direction': tick_direction,
        'grid.color': '0.9',
        'grid.linestyle': '--',
        'grid.linewidth': 0.5,
        'axes.grid': grid
    })

# Apply default style upon import
set_plot_style()


def spectra_plot_export(
    data: np.ndarray, 
    sample_name: str, 
    output_path: str, 
    x_limits: tuple = (400, 800), 
    show: bool = True
) -> None:
    """
    Generate, display, and save a spectra plot for the given data with optional x-axis limits.
    """
    plt.figure()
    plt.plot(data[:, 0], data[:, 1])
    plt.title(f"Spectrum: {sample_name}")
    plt.xlabel("Wavelength (nm)")
    plt.ylabel("Intensity (a.u.)")
    plt.xlim(x_limits)
    plt.tight_layout()
    plt.savefig(output_path)
    if show:
        plt.show()
    plt.close()


def export_square_map(
    map_data: np.ndarray,
    sample_name: str,
    output_dir: str,
    parameter_name: str,
    cmap: str = 'viridis',
    unit_label: str = '',
    physical_size_um: float = 10.0,
    show: bool = True
) -> np.ndarray:
    """
    Generalized export of a square 2D map as PDF and PNG.
    """
    if map_data.ndim != 2 or map_data.shape[0] != map_data.shape[1]:
        raise ValueError('map_data must be a 2D square array.')
    mean_val = np.mean(map_data)
    std_val = np.std(map_data)
    vmin = max(0, mean_val - 2 * std_val)
    vmax = mean_val + 2 * std_val
    size = map_data.shape[0]
    ticks = np.linspace(0, size - 1, num=5)
    tick_labels = np.linspace(0, physical_size_um, num=5)
    fig, ax = plt.subplots(figsize=(6, 6))
    cax = ax.imshow(map_data, cmap=cmap, vmin=vmin, vmax=vmax, origin='lower')

    title_text = f'{parameter_name} map of {sample_name}'
    if len(title_text) > 24:
        title_text = f'{parameter_name} map\nof {sample_name}'
    ax.set_title(title_text)
    cbar = fig.colorbar(cax)
    if unit_label:
        cbar.set_label(unit_label)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{x:.1f}" for x in tick_labels])
    ax.set_yticks(ticks)
    ax.set_yticklabels([f"{x:.1f}" for x in tick_labels])
    ax.set_xlabel('Micrometers (µm)')
    ax.set_ylabel('Micrometers (µm)')
    for spine in ax.spines.values():
        spine.set_visible(True)
    os.makedirs(output_dir, exist_ok=True)
    base = os.path.join(output_dir, f"{sample_name}_{parameter_name.replace(' ', '_').lower()}_map")
    for ext in ('.pdf', '.png'):
        fig.savefig(base + ext)
    if show:
        plt.show()
    plt.close(fig)
    return map_data


def pair_plot_with_histograms_export(
    datX: np.ndarray,
    datY: np.ndarray,
    X_label: str,
    X_units: str,
    Y_label: str,
    Y_units: str,
    sample_field_name: str,
    output_dir: str,
    show: bool = True
) -> None:
    """
    Generate a pair plot with 2D histogram and marginals.
    """
    # Define bins based on mean ± 4·std
    x_bins = np.linspace(datX.mean() - 4 * datX.std(), datX.mean() + 4 * datX.std(), 200)
    y_bins = np.linspace(datY.mean() - 4 * datY.std(), datY.mean() + 4 * datY.std(), 200)

    # Compute 2D histogram
    H, y_edges, x_edges = np.histogram2d(datY, datX, bins=[y_bins, x_bins])
    H = np.log10(H + 1e-6)

    # Main 2D density plot
    fig, ax2D = plt.subplots(figsize=(7, 6))
    ax2D.pcolormesh(x_edges, y_edges, H, cmap='plasma')

    # Marginal histograms sharing axes
    divider = make_axes_locatable(ax2D)
    axHistX = divider.append_axes('top', size='20%', pad=0.1, sharex=ax2D)
    axHistY = divider.append_axes('right', size='20%', pad=0.1, sharey=ax2D)

    # Plot histograms; scale matches main plot via shared axes
    axHistX.hist(datX, bins=x_bins, color='firebrick')
    axHistY.hist(datY, bins=y_bins, color='royalblue', orientation='horizontal')

    # Remove labels and ticks for marginals
    axHistX.set_xticks([])
    axHistX.set_yticks([])
    axHistY.set_xticks([])
    axHistY.set_yticks([])

    # Axis labels and limits
    ax2D.set_xlabel(f"{X_label}{X_units}")
    ax2D.set_ylabel(f"{Y_label}{Y_units}")
    x_lim = [max(0, datX.mean() - 4 * datX.std()), datX.mean() + 4 * datX.std()]
    y_lim = [max(0, datY.mean() - 4 * datY.std()), datY.mean() + 4 * datY.std()]
    ax2D.set_xlim(x_lim)
    ax2D.set_ylim(y_lim)

    # Save outputs
    os.makedirs(output_dir, exist_ok=True)
    fig.tight_layout(pad=0.5)
    fig.savefig(os.path.join(output_dir, f"{sample_field_name}_pair_plot.pdf"))
    fig.savefig(os.path.join(output_dir, f"{sample_field_name}_pair_plot.png"))
    if show:
        plt.show()
    plt.close(fig)


def correlation_matrix_plot_export(
    data_arrays: dict,
    sample_name: str,
    output_dir: str,
    show: bool = True
) -> None:
    """
    Generate a correlation matrix plot for named data arrays.
    """
    if not data_arrays or not isinstance(data_arrays, dict):
        raise ValueError('data_arrays must be a non-empty dict of 1D arrays')
    lengths = [arr.shape[0] for arr in data_arrays.values()]
    if any(not isinstance(arr, np.ndarray) or arr.ndim != 1 for arr in data_arrays.values()) or len(set(lengths)) != 1:
        raise ValueError('All values in data_arrays must be 1D numpy arrays of equal length')
    df = pd.DataFrame(data_arrays)
    corr_mat = df.corr()

    # Plot with fixed limits
    fig, ax = plt.subplots(figsize=(6, 5))
    cax = ax.matshow(corr_mat, cmap='coolwarm', vmin=-1, vmax=1)
    fig.colorbar(cax)
    labels = corr_mat.columns.tolist()
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='left')
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    for (i, j), val in np.ndenumerate(corr_mat.values):
        ax.text(j, i, f'{val:.2f}', ha='center', va='center')
    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(os.path.join(output_dir, f"{sample_name}_correlation_matrix.pdf"))
    fig.savefig(os.path.join(output_dir, f"{sample_name}_correlation_matrix.png"))
    if show:
        plt.show()
    plt.close(fig)


if __name__ == "__main__":
    # Demo usage remains unchanged
    demo_dir = os.path.abspath('demo_outputs')
    os.makedirs(demo_dir, exist_ok=True)

    x = np.linspace(400, 700, 300)
    y = np.exp(-0.5 * ((x - 550) / 20)**2)
    spectra_plot_export(np.column_stack((x, y)), 'demo_spectrum', os.path.join(demo_dir, 'spectrum_demo.png'))

    square = np.random.rand(50, 50)
    export_square_map(square, 'demo_map', demo_dir, 'Random Data', unit_label='a.u.')

    arr1 = np.random.normal(size=1000)
    arr2 = arr1 * 0.5 + np.random.normal(scale=0.1, size=1000)
    pair_plot_with_histograms_export(arr1, arr2, 'X', ' units', 'Y', ' units', 'demo_pair', demo_dir)

    data_dict = {'A': arr1, 'B': arr2, 'C': np.random.rand(1000)}
    correlation_matrix_plot_export(data_dict, 'demo_corr', demo_dir)
