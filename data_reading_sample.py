# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 12:10:49 2024

@author: wclaey6

Sample code to show the functionality of the functions in data_reading
"""

from data_reading import *
from data_reading_MIM import *

import matplotlib.pyplot as plt

# =============================================================================
# Creating the list of relevant series
# =============================================================================
path = "C:\\Wies Data\\Data for Python"

# Gather metadata of all series in the given path
database = create_database(path)

# Choose a patient within the database
list_patients(database)

patient_name = "patient_name"
patient_ID = "patient_ID"

patient = lookup_patient(database, patient_name, patient_ID = patient_ID)

# Choose subset of series from this patient
series_description = ""
date = "yyyy-mm-dd"

series = find_series(patient, series_description, date= date)
dcm_list = load_series(series)


#%% ===========================================================================
# Loading an NM series and showing the central slice
# =============================================================================


dcm = dcm_list[0]

data = get_rescaled_data(dcm)
data = np.swapaxes(data, 0, 2)

i = round(np.size(data, axis = 2) / 2)
plt.imshow(data[:,:,i])