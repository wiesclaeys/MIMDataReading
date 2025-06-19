# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 12:10:49 2024

@author: wclaey6

Sample code to show the functionality of the functions in data_reading
"""

from data_reading import *
from data_reading_MIM import *

from functions_viewing import show_slice

# =============================================================================
# Creating the list of relevant series
# =============================================================================
path = "C:\\Wies Data\\Data for Python"

# Gather metadata of all series in the given path
database = create_database(path)

# Choose a patient within the database
list_patients(database)

patient_name = "QCintevo_WC"
patient_ID = "Noise Levels"

patient = lookup_patient(database, patient_name, patient_ID = patient_ID)


# Choose subset of series from this patient
series_description = "01_minutes"
date = "2024-10-03"

series = find_series(patient, series_description, date= date)
dcm_list = load_series(series)




#%% ===========================================================================
# Loading one series from the series list
# =============================================================================


dcm = dcm_list[3]
data = get_rescaled_data(dcm)
data = np.swapaxes(data, 0, 2)


show_slice(data, plane = "axial")