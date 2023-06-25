# Merging Walking Data

## Problem Statement

In this exercise, we need to combine two data sources: data from a phone's sensors recorded with Physics Toolbox Sensor Suite and metadata from a GoPro recording of the same walk. The goal is to merge the GPS data from the GoPro with the magnetometer data from the phone to analyze both datasets together.

The provided data consists of the following files:

- GoPro data:
  - `accl.ndjson.gz`: Accelerometer data from the GoPro.
  - `gopro.gpx`: GPS data from the GoPro.

- Phone data:
  - `phone.csv.gz`: Sensor data from the phone.

The phone data does not contain date/time values but only seconds offset from the start of the recording. We need to combine the GoPro and phone data to obtain the GPS data from the GoPro along with the magnetometer data from the phone.

## Approach and Methods

1. **Data Combination**

   - Implement a Python program, `combine_walk.py`, that takes the input directory path containing the data files and the destination directory path for the output files as command-line arguments.
   - Read the GoPro accelerometer data from the file `accl.ndjson.gz` and the GoPro GPS data from the file `gopro.gpx`.
   - Read the phone sensor data from the file `phone.csv.gz`.
   - Perform necessary data cleaning and preprocessing steps, such as removing unnecessary readings and noise.
   - Create a timestamp for the phone data using the offset and the timestamp from the GoPro accelerometer data.
   - Aggregate the data using 4-second bins by rounding the timestamps to the nearest 4 seconds.
   - Group the data based on the rounded timestamps and average the remaining values.
   - Ensure that the resulting DataFrames for accelerometer, GPS, and phone sensors have identical keys/labels on the rows, excluding any rows where the devices didn't start/stop at exactly the same time.

2. **Data Correlation**

   - Calculate the time offset between the phone data and the GoPro accelerometer data.
   - Define an array of possible offset values using `np.linspace(-5.0, 5.0, 101)` to cover offsets ranging from -5.0 to 5.0 seconds.
   - Iterate over the offset values and calculate the cross-correlation between the 'gFx' values from the phone data and the 'x' values from the accelerometer data.
   - The cross-correlation can be calculated by multiplying the corresponding 'gFx' and 'x' values and summing the results.
   - Determine the offset value that produces the highest cross-correlation.
   - Print the best time offset for the phone data.

3. **Output Generation**

   - Once the data is correctly combined and the best time offset is determined, generating the output files.
   - Create a file named `walk.gpx` in the output directory and populate it with the GPS data from the GoPro along with the corresponding magnetometer data from the phone.
   - Create a file named `walk.csv` in the output directory and populate it with the relevant fields from the combined data.
