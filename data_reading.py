# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 11:08:37 2024

@author: wclaey6


This code provides tools to read dicom data into Python
"""

import os

import pydicom

import numpy as np
import pandas as pd


def get_rescaled_data(dcm):
    """
    Read pixel data and apply rescaling if needed.
    Includes MIM rescaling, Siemens rescaling
    
    Parameters
    ----------
    dcm : pydicom FileDataset
        The dicom file to be read.

    Returns
    -------
    vol : numpy array of float
        Containing the rescaled pixel data.
    
    """
    vol         = dcm.pixel_array 

    # try to find a rescale factor
    try:
        rescale = dcm.RescaleSlope
        intercept = dcm.RescaleIntercept
        
    except:
        try:
            # Siemens rescale
            rescale = 1 / dcm[0x0033,0x1038].value
            intercept = 0
            
        except:    
            try:    # MIM rescale
                field = dcm[0x0040,0x9096][0]
                rescale = 1/field[0x0040,0x9225].value
                intercept = 0
            except:
                rescale = 1
                intercept = 0
    print("rescale factor = ", rescale)
    # rescale the data
    vol = vol * rescale + intercept
    return vol


def get_voxsizes(dcm):
    """
    Read and process voxel size data

    Parameters
    ----------
    dcm : pydicom FileDataset
        The dicom file to be read.

    Returns
    -------
    voxsizes : numpy array
        Containing the voxel size in mm in the x, y, and z directions.
    voxvol : float
        Volume in ml of the voxels.

    """
    
    # reading some metadata
    voxsize_x = dcm.PixelSpacing[0]
    voxsize_y = dcm.PixelSpacing[1]
    voxsize_z = abs(dcm.SpacingBetweenSlices)
    
    if (voxsize_x != voxsize_y) or (voxsize_y != voxsize_z):
        print("! Warning: the voxel size is not isotropic !")
    
    voxsizes = np.array([voxsize_x, voxsize_y, voxsize_z], dtype = float)
    voxvol = voxsizes[0] * voxsizes[1] * voxsizes[2] / 1000     # ml
    
    return voxsizes, voxvol

def show_slice(vol, plane = 'axial', colorbar = True, title = None):
    """
    Show an example slice of an image.
    For axial slices, the hottest slice is chosen, otherwise the central slice is shown.

    Parameters
    ----------
    vol : numpy array
        The volume to show.
    plane: str
        The plane to show. Options are 'axial', 'sagittal' or 'coronal', default is 'axial'.
    colorbar : boolean
        Whether or not to add a colorbar
    title : string
        Title of the image

    Returns
    -------
    index : int
        Index of the displayed slice

    """
    

    # Plotting
    if plane == 'sagittal':
        num_slices = np.size(vol, axis = 0)
        index = round(num_slices / 2)
        sl = vol[index,:,:]
    elif plane == 'coronal':
        num_slices = np.size(vol, axis = 1)
        index = round(num_slices / 2)
        sl = vol[:,index,:]
    else:
        counts_per_slice = np.sum(vol, axis = (0,1))
        index = np.argmax(counts_per_slice)
        sl = vol[:,:,index]
    sl = np.swapaxes(sl, 0, 1)  # swapping axes for viewing
    plt.imshow(sl)
    
    # Layout
    if title == None:
        title = plane + " slice"
    if colorbar:
        plt.colorbar()
    plt.title(title)
    plt.show()
    
    return index
    