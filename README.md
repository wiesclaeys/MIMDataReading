# MIMDataReading
Tools to easier read and access dicom data exported by MIM in Python.

Data can be exported from MIM via: “Send To…” > “Selected Folder”, which creates folders per month (“yyyy-mm_Studies”) that contain subfolders for each individual series. The names of these folders contain some information on the series itself, like patient name, acquisition date and time and series description. This code allows to read and process the folder names into a database from which all series can be more easily read and retrieved.

## Usage

Build the database by running
```
database = create_database(path)
```
where 'path' is the location where the MIM files were exported to.
The function
```
list_patients(database)
```
can be used to list all unique patient names and IDs in the database. A subset of the database containing the series for a single patient can be created using
```
subset = lookup_patient(database, lookup_patient(database, patient_name, patient_ID))
```
A further selection of series can be made using
```
subset = find_series(database, series_description, tags)
```
where the possible tags are modality, date, time, study_description, num_images.
Finally, 
```
dcms = load_series(subset)
```
can be used to obtained a list containing dicom objects for each serie in the subset database. For NM data, this will be a pydicom dataset, while for PT or CT data, this is a pymirc dataset instead (see https://github.com/gschramm/pymirc)
A simple example is provided in data_reading_sample.py.

## Extra: general dicom reading tools

```
get_rescaled_data(dcm)
```
Get pixel data from pydicom object and apply MIM (0040,9096) or Siemens (0033,1038) rescaling if needed.
```
voxsizes, voxvol = get_voxsizes(dcm)
```
Get 3d voxel size and volume.
