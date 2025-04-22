import numpy as np
import os
from datetime import datetime

def load_data(
    file_path: str,
    delimiter: str = None,
    skiprows: int = 0
) -> np.ndarray:
    """
    Load numerical data from a text or CSV file.

    Parameters
    ----------
    file_path : str
        Path to the data file.
    delimiter : str, optional
        Delimiter for parsing (default None → whitespace or comma).
    skiprows : int, optional
        Number of rows to skip at the start (default 0).

    Returns
    -------
    np.ndarray
        Loaded data array.
    """
    return np.loadtxt(file_path, delimiter=delimiter, skiprows=skiprows)
