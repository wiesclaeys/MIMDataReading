# -*- coding: utf-8 -*-
"""
Created on Tue Oct 15 11:08:37 2024

@author: wclaey6


This code provides tools to read dicom data into Python
"""

import os

import pydicom
import pymirc

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def read_file(path):
    """
    Read the dicom file(s) in a given path.
    Returns the dicom header and pixel data separately

    Parameters
    ----------
    path : string
        Location of the file(s) to be read.

    Returns
    -------
    header : pydicom dataset
        Containing the dicom metadata.
    data : numpy array
        The image data.

    """
    files = os.listdir(path)
    first_header = pydicom.dcmread(os.path.join(path, files[0]))
    Modality = first_header.Modality
    
    if Modality == 'NM' or Modality == 'OT':
        if len(files) > 1:  # check for multiple files
            print("Multiple instances detected: number of files = ", l)
            datas = []
            headers = []
            for i in range(len(files)):
                headers.append(pydicom.dcmread(os.path.join(path, files[i])))
                datas.append(get_rescaled_data(os.path.join(path, files[i])))
            return headers, datas
        else:
            header = first_header
            data = get_rescaled_data(header)
            if "RECON TOMO" in header.ImageType:    # rearrange axis if reconstructed image
                print("--- swapping axis 0 and 2")
                data = np.swapaxes(data, 0, 2)  # change coordinates to x,y,z
    
    if Modality == 'PT':    # use pymirc to get pixel data
        header = first_header
        DicomVolume = pymirc.fileio.DicomVolume(os.path.join(path, '*'))
        data = DicomVolume.get_data()
    
    return header, data

def get_rescaled_data(dcm):
    """
    Read pixel data and apply rescaling if needed.
    Includes MIM rescaling, Siemens rescaling.
    Converts data to float
    
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
    vol         = np.array(vol, dtype = float)
        
    # try to find a rescale factor
    try:
        rescale = dcm.RescaleSlope
        try:
            intercept = dcm.RescaleIntercept
        except:
            intercept = 0
    except:
        try:
            # Siemens rescale
            rescale = 1 / dcm[0x0033,0x1038].value
            intercept = 0
            print("2")
        except:    
            try:    # normal rescale (https://dicom.innolitics.com/ciods/nuclear-medicine-image/general-image/00409096)
                field = dcm[0x0040,0x9096][-1]
                rescale = field[0x0040,0x9225].value
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
    
    try:
        voxsize_z = abs(dcm.SpacingBetweenSlices)
    except:
        voxsize_z = abs(dcm.SliceThickness)
    
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
    