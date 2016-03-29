#!/usr/bin/env python
import numpy as np
import collections
__all__ = ['fracPoissonErrors']


def fracPoissonErrors(num, asymmetric=True):
    """
    Approximate asymmetric Poisson errorbars as a fraction of counts
    equal to  np.sqrt(N + 0.25) \pm 0.5 / N as a simple
    replacement to sqrt(N)/N as suggested in
    http://www-cdf.fnal.gov/physics/statistics/notes/pois_eb.txt (point 4)


    Parameters
    ----------
    num : array-like, mandatory
        number counts on which the error bars are desired
    asymmetric : bool, optional, defaults to True
        if True, returns asyme

    Returns
    -------
    array-like
    """

    num = np.asarray(num)
    sig = np.sqrt(num + 1.0 / 4.)

    if asymmetric:
        return np.array([(sig - 0.5) / num, (sig + 0.5) / num] )
    else:
        return 1. / np.sqrt(num)

