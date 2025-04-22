import numpy as np
from lmfit import Model
import os

def gaussian(x: np.ndarray, amplitude: float, center: float, sigma: float) -> np.ndarray:
    """
    Single Gaussian function.
    """
    return amplitude * np.exp(-0.5 * ((x - center) / sigma) ** 2)


def double_gaussian(x: np.ndarray,
                    amp1: float, cen1: float, sigma1: float,
                    amp2: float, cen2: float, sigma2: float) -> np.ndarray:
    """
    Sum of two Gaussian functions.
    """
    return (gaussian(x, amp1, cen1, sigma1) +
            gaussian(x, amp2, cen2, sigma2))


def fit_model(x: np.ndarray,
              y: np.ndarray,
              model: str = 'double',
              x_min: float = None,
              x_max: float = None,
              initial_params: dict = None,
              ax=None):
    """
    Fit data (y vs. x) using a single or double Gaussian model.
    """
    if model == 'single':
        mod = Model(gaussian)
        params = mod.make_params(amplitude=y.max(), center=x[np.argmax(y)], sigma=(x.max() - x.min())/10)
    else:
        mod = Model(double_gaussian)
        params = mod.make_params(
            amp1=y.max()/2, cen1=x[np.argmax(y)], sigma1=(x.max()-x.min())/20,
            amp2=y.max()/2, cen2=x[np.argmax(y)], sigma2=(x.max()-x.min())/20
        )
    if initial_params:
        for name, val in initial_params.items():
            if name in params:
                params[name].set(value=val)

    for param in params.values():
        param.set(min=0)
        
    mask = np.ones_like(x, dtype=bool)
    if x_min is not None:
        mask &= (x >= x_min)
    if x_max is not None:
        mask &= (x <= x_max)
    x_fit = x[mask]
    y_fit = y[mask]
    result = mod.fit(y_fit, params, x=x_fit)
    if ax is not None:
        ax.plot(x_fit, y_fit, '.', label='Data')
        ax.plot(x_fit, result.best_fit, '-', label='Fit')
        try:
            comps = result.eval_components(x=x_fit)
            for comp in comps:
                ax.plot(x_fit, comps[comp], '--', label=comp)
        except Exception:
            pass
        ax.legend()
        ax.set_xlabel('Wavelength')
        ax.set_ylabel('Intensity')
    return result


def extract_fit_results(result, model: str = 'double') -> dict:
    """
    Extract fit parameter values and chi-square.
    """
    res = {}
    for name, par in result.params.items():
        res[name] = par.value
    res['chi_square'] = result.chisqr
    return res


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    # Create demo directory
    demo_dir = os.path.abspath('demo_fit_outputs')
    os.makedirs(demo_dir, exist_ok=True)

    # 1. Test single Gaussian fit
    x = np.linspace(-10, 10, 500)
    y_true = gaussian(x, amplitude=5, center=1, sigma=2)
    noise = np.random.normal(scale=0.2, size=x.size)
    y_noisy = y_true + noise
    fig, ax = plt.subplots()
    result_single = fit_model(x, y_noisy, model='single', ax=ax)
    plt.title('Single Gaussian Fit')
    fig.savefig(os.path.join(demo_dir, 'single_gaussian_fit.png'))
    plt.close(fig)
    print('Single fit results:', extract_fit_results(result_single))

    # 2. Test double Gaussian fit
    y_true2 = double_gaussian(x, 3, -2, 1, 4, 3, 2)
    y_noisy2 = y_true2 + np.random.normal(scale=0.3, size=x.size)
    fig2, ax2 = plt.subplots()
    result_double = fit_model(x, y_noisy2, model='double', ax=ax2)
    plt.title('Double Gaussian Fit')
    fig2.savefig(os.path.join(demo_dir, 'double_gaussian_fit.png'))
    plt.close(fig2)
    print('Double fit results:', extract_fit_results(result_double))
