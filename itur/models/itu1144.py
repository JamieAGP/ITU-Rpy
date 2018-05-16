# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
from scipy.interpolate import griddata, RegularGridInterpolator
from scipy.ndimage.interpolation import map_coordinates

"""
Interpolation methods for the geophysical properties used to compute
propagation effects. These methods are based on those in Recommendation
ITU-R P.1144-7.

References
--------
[1] Guide to the application of the propagation methods of Radiocommunication
Study Group 3: https://www.itu.int/rec/R-REC-P.1144/en
"""


def is_regular_grid(lats_o, lons_o):
    '''

    Returns whether the grids in lats_o and lons_o are both regular grids or
    not. A grid is regular if the difference (column-wise or row-wise)
    between consecutive values is constant across the grid.


    Parameters
    -----------
    lats_o : numpy.ndarray
        Grid of latitude coordinates
    lons_o : numpy.ndarray
        Grid of longitude coordinates


    Returns
    --------
        is_regular: boolean
    '''
    Delta_lons = np.unique(np.diff(lons_o, axis=1))
    Delta_lats = np.unique(np.diff(lats_o, axis=0))

    return (Delta_lons.size == 1 and (Delta_lons != 0).all() and
            Delta_lats.size == 1 and (Delta_lats != 0).all())

###############################################################################
#                       Nearest Neighbour Interpolation                       #
###############################################################################


def nearest_2D_interpolator(lats_o, lons_o, values):
    '''
    Produces a 2D interpolator function using the nearest value interpolation
    method. If the grids are regular grids, uses the
    scipy.interpolate.RegularGridInterpolator,
    otherwise, scipy.intepolate.griddata

    Values can be interpolated from the returned function as follows:
       f = nearest_2D_interpolator(lat_origin, lon_origin, values_origin)
       interp_values = f(lat_interp, lon_interp)


    Parameters
    -----------
    lats_o: numpy.ndarray
        Latitude coordinates of the values usde by the interpolator
    lons_o: numpy.ndarray
        Longitude coordinates of the values usde by the interpolator
    values: numpy.ndarray
        Values usde by the interpolator


    Returns
    --------
    interpolator: function
        Nearest neighbour interpolator function
    '''
    # Determine if we are dealing with a regular grid
    if is_regular_grid(lats_o[2:-2, 2:-2], lons_o[2:-2, 2:-2]):
        return _nearest_2D_interpolator_reg(lats_o, lons_o, values)
    else:
        return _nearest_2D_interpolator_arb(lats_o, lons_o, values)


def _nearest_2D_interpolator_reg(lats_o, lons_o, values, lats_d, lons_d):
    f = RegularGridInterpolator((np.flipud(lats_o[:, 0]), lons_o[0, :]),
                                np.flipud(values), method='nearest',
                                bounds_error=False)
    return f


def _nearest_2D_interpolator_arb(lats_o, lons_o, values):
    return lambda x: griddata((lats_o.ravel(), lons_o.ravel()), values.ravel(),
                              (x[:, 0], x[:, 1]), 'nearest')


###############################################################################
#                            Bilinear Interpolation                           #
###############################################################################

def bilinear_2D_interpolator(lats_o, lons_o, values):
    '''
    Produces a 2D interpolator function using the bilinear interpolation
    method. If the grids are regular grids, uses the
    scipy.interpolate.RegularGridInterpolator,
    otherwise, scipy.intepolate.griddata

    Values can be interpolated from the returned function as follows:
       f = nearest_2D_interpolator(lat_origin, lon_origin, values_origin)
       interp_values = f(lat_interp, lon_interp)


    Parameters
    -----------
    lats_o: numpy.ndarray
        Latitude coordinates of the values usde by the interpolator
    lons_o: numpy.ndarray
        Longitude coordinates of the values usde by the interpolator
    values: numpy.ndarray
        Values usde by the interpolator


    Returns
    --------
    interpolator: function
        Bilinear interpolator function
    '''
    if is_regular_grid(lats_o[2:-2, 2:-2], lons_o[2:-2, 2:-2]):
        return _bilinear_2D_interpolator_reg(lats_o, lons_o, values)
    else:
        return _bilinear_2D_interpolator_arb(lats_o, lons_o, values)


def _bilinear_2D_interpolator_reg(lats_o, lons_o, values):
    f = RegularGridInterpolator((np.flipud(lats_o[:, 0]), lons_o[0, :]),
                                np.flipud(values), method='linear',
                                bounds_error=False)
    return f


def _bilinear_2D_interpolator_arb(lats_o, lons_o, values):
    return lambda x: griddata((lats_o.ravel(), lons_o.ravel()), values.ravel(),
                              (x[:, 0], x[:, 1]), 'linear')


###############################################################################
#                            Bicubic Interpolation                            #
###############################################################################

def bicubic_2D_interpolator(lats_o, lons_o, values):
    '''
    Produces a 2D interpolator function using the bicubic interpolation
    method. Uses the scipy.intepolate.griddata method.

    Values can be interpolated from the returned function as follows:
       f = nearest_2D_interpolator(lat_origin, lon_origin, values_origin)
       interp_values = f(lat_interp, lon_interp)


    Parameters
    -----------
    lats_o: numpy.ndarray
        Latitude coordinates of the values usde by the interpolator
    lons_o: numpy.ndarray
        Longitude coordinates of the values usde by the interpolator
    values: numpy.ndarray
        Values usde by the interpolator


    Returns
    --------
    interpolator: function
        Bicubic interpolator function
    '''
    if is_regular_grid(lats_o[2:-2, 2:-2], lons_o[2:-2, 2:-2]):
        return regular_bicubic_interpolator(lats_o, lons_o, values)
    else:
        return _bicubic_2D_interpolator_arb(lats_o, lons_o, values)


def _bicubic_2D_interpolator_arb(lats_o, lons_o, values):
    return lambda x: griddata((lats_o.ravel(), lons_o.ravel()),
                              values.ravel(), (x[:, 0], x[:, 1]), 'cubic')


#def _bicubic_2D_interpolator_reg(lats_o, lons_o, values, x):
#    D_lat = np.unique(np.diff(lats_o[2:-2, 2]))
#    D_lon = np.unique(np.diff(lons_o[2, 2:-2]))
#    return map_coordinates(
#        values, np.array([(x[:, 0] + lats_o.min()) / D_lat, x[:, 1] / D_lon]),
#        order=3, mode='nearest')

def regular_bicubic_interpolator(lats, lons, vals):

    lat_row = lats[1:-1, 1]
    lon_row = lons[1, 1:-1]
    I = vals

    def K(d):
        d = np.abs(d)
        return np.where(np.logical_and(d >= 0, d <= 1),
                        1.5 * d**3 - 2.5 * d**2 + 1,
                        np.where(np.logical_and(d >= 1, d <= 2),
                                 -0.5 * d**3 + 2.5 * d**2 - 4 * d + 2, 0))

    def interpolator(vect):
        lat = vect[:, 0]
        lon = vect[:, 1]

        R = np.searchsorted(lat_row, lat, 'right') - 1
        C = np.searchsorted(lon_row, lon, 'right') - 1

        diff_lats = np.diff(lat_row)[0]
        diff_lons = np.diff(lon_row)[0]

        r = (lat - lat_row[0]) / diff_lats + 1
        c = (lon - lon_row[0]) / diff_lons + 1

        RI_Rc = I[R, C] * K(c - C) + I[R, C + 1] * K(c - (C + 1)) + \
            I[R, C + 2] * K(c - (C + 2)) + I[R, C + 3] * K(c - (C + 3))
        RI_R1c = I[R + 1, C] * K(c - C) + I[R + 1, C + 1] * K(c - (C + 1)) + \
            I[R + 1, C + 2] * K(c - (C + 2)) + I[R + 1, C + 3] * K(c - (C + 3))
        RI_R2_c = I[R + 2, C] * K(c - C) + I[R + 2, C + 1] * K(c - (C + 1)) +\
            I[R + 2, C + 2] * K(c - (C + 2)) + I[R + 2, C + 3] * K(c - (C + 3))
        RI_R3_c = I[R + 3, C] * K(c - C) + I[R + 3, C + 1] * K(c - (C + 1)) +\
            I[R + 3, C + 2] * K(c - (C + 2)) + I[R + 3, C + 3] * K(c - (C + 3))

        return (RI_Rc * K(r - R) + RI_R1c * K(r - (R + 1)) +
                RI_R2_c * K(r - (R + 2)) + RI_R3_c * K(r - (R + 3)))

    return interpolator
