# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 10:42:05 2025

@author: wclaey6


This code is meant to provide an easy means to read DICOM files exported by MIM
The series information in the folder names is used to create a database of available series.
Several fcuntions are provided to look up specific patients or series within this database.
The final load_series function returns a list of DICOM objects for the selected functions.
For NM objects, a pydicom object is returned. For CT and PT, pymirc is used instead to merge the different slices into one dicom object (see https://github.com/gschramm/pymirc)
"""

import os
import pydicom

import pymirc

import pandas as pd
import numpy as np

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================

def create_database(path):
    """
    Read and process all folder names in a given path to form a database containing all available series info

    Parameters
    ----------
    path : str
        Path of the data exported by MIM.

    Returns
    -------
    database : pandas dataframe
        Containing the available series information including tha path to the full dicom data.

    """
    " create a pandas dataframe to easily look up exported MIM data"
    
    specifiers = ["patient_name", "patient_ID", "modality", "date", "time", "study_description", "series_description", "num_images", "r1", "r2"] # the information in the folder name
    
    files = []  # will contain the full path to each dicom file
    names = []  # will contain the folder name of each dicom file
    info = []   # will contain the information from each folder name
    
    # Find all available series and folder names
    folders = os.listdir(path)  #list the folders for the different months    
    for folder in folders:
        series = os.listdir(os.path.join(path, folder)) #list the folders containing the actual series
        
        for serie in series:
            names.append(serie)
            files.append(os.path.join(path, folder, serie))
    
    # Process the folder names
    for name in names:
        words = name.split("_")
        words = [process(word) for word in words]
        info.append(words)
    
    # Create the database containing the folder information and the path to the corresponding series
    info = pd.DataFrame(np.array(info), columns = specifiers)   
    paths = pd.DataFrame(np.array(files), columns = ["full_path"])
    database = info.join(paths)
    
    return database

def list_patients(database):
    """
    List all unique patient names and IDs in the current database

    Parameters
    ----------
    database : pandas dataframe
        The collection of series to consider

    Returns
    -------
    patient_names: numpy array
        Containing all unique patient names sorted alphabetically

    """    
    
    print("--- Listing all patients ---")
    
    patient_names = np.sort(database.patient_name.unique()) # finding and sorting all unique patients
    for patient_name in patient_names:
        patient = database.loc[database['patient_name'] == patient_name]
        patient_IDs = np.sort(patient.patient_ID.unique())  # finding and sorting all unique patient IDs for this patient
        for patient_ID in patient_IDs:
            print("Name: ", patient_name, " - ID: ",  patient_ID)
    
    print("-----------------------------")
    
    return patient_names

def lookup_patient(database, patient_name, patient_ID = None):
    """
    Look up the series from a specific patient based on patient name and ID (optional).

    Parameters
    ----------
    database : pandas dataframe
        The collection of series to consider
    patient_name : str
        (part of) the required patient name
    patient_ID : str, optional
        The required patient ID. The default is None.

    Returns
    -------
    subset : pandas dataframe
        All series corresponding to this patient.

    """
    # Printing
    if patient_ID is not None:
        print("Looking for patient", patient_name, "with patient ID", patient_ID)
    else:
        print("Looking for patient", patient_name)
    
    # Looking up all series with the correct patient name
    subset = database
    patient_name = process(patient_name)
    subset = subset.loc[subset['patient_name'].str.contains(patient_name)]
    if len(subset) == 0:
        print("Patient name", patient_name, " not found")
        return
    
    # Looking up all series with the correct patient ID
    if patient_ID is not None:
        patient_ID = process(patient_ID)
        subset = subset[subset['patient_ID'] == patient_ID]
        if len(subset) == 0:
            print("Patient ID", patient_ID, " not found")
            return
    
    print(len(subset), "series found corresponding to this patient")
    return subset

def find_series(database, series_description, modality = None, date = None, time = None, study_description = None, num_images = None):
    """
    Look up the subset of series satisfying certain criteria

    Parameters
    ----------
    database : pandas dataframe
        Containing the all the series to consider
    series_description : str
        (part of) the required series description.
    modality, date, time, study_description, num_images : str, optional
        The possible search criteria. Default is None.

    Returns
    -------
    series : pandas dataframe
        The subset of series satisfying all criteria.
        
    """
    
    # Optional search tags
    tags = {"modality" : modality, "date" : date, "time" : time, "study_description" : study_description, "num_images" : num_images}
    
    # Printing
    print("Selecting all series with: ")
    print('- series description containing "', series_description, '"')
    for tag in tags:
        if tags[tag] is not None:
            print("-", tag, "=" , tags[tag])
    
    # Finding the series with matching series description
    subset = database
    series_description = process(series_description)
    series = subset.loc[subset['series_description'].str.contains(series_description)]   
    if len(subset) == 0:
        print("No series found with series description containing ", series_description)
        return
    
    # Finding the series matching the optional search criteria
    for tag in tags:
        if tags[tag] is not None:
            val = process(tags[tag])
            subset = subset.loc[subset[tag] == val]
            if len(subset) == 0:
                print("No series found with ", tag, val)
                return
    
    print(len(series), "series found satisfying the requirements")
    
    return series

def load_series(database):
    """
    Return a list containing the DICOM file for each series in a database

    Parameters
    ----------
    database : pandas dataframe
        containing the series to be loaded.

    Returns
    -------
    dcms : list of DICOM objects
        the loaded series. Format:
        - CT, PT: PyMirc DICOM volume object
        - NM: Pydicom dataset object

    """
    dcms = []   # will contain the dicom objects
    
    print("Loading", len(database), "series:")
    series_counter = 0  # series ID
    for i in range(len(database)):
        print(series_counter, "-", database['series_description'].values[i])
        modality = database["modality"].values[i]
        path = database['full_path'].values[i]
        # print(os.path.join(path, '*'))
        if (modality == "CT" or modality == "PT"):  # use pymirc for slice-based dicoms
            dcm = pymirc.fileio.DicomVolume(os.path.join(path, '*'))
            dcms.append(dcm)
        
        else: 
            files = os.listdir(path)
            l = len(files)
            if l > 1:   # handling multiple NM instances (e.g. separately saved energy windows)
                print("Multiple instances detected: number of files = ", l)
                series_counter += (l-1)
            for j in range(l):  # use pydicom for volume-based dicoms
                dcm = pydicom.dcmread(os.path.join(path, files[j]))
                dcms.append(dcm)
        series_counter += 1
        
    return dcms
    
# =============================================================================
# AUXILIARY FUNCTIONS
# =============================================================================

def process(name):
    "Recreates the way MIM processes strings before using them as a folder name"
    news = ["_", "[", "]"]
    olds = [".", "(", ")"]
    for i in range(len(olds)):
        name = name.replace(olds[i], news[i])
    return name