import os
import csv
import math
import time
import pandas as pd
import numpy as np

np.seterr(divide='ignore', invalid='ignore')
C_light=3E14 # um/s

WL_DUSTY = [1.000E-02, 1.500E-02, 2.000E-02, 3.000E-02, 4.000E-02, 5.000E-02, 6.000E-02, 8.000E-02, 1.000E-01, 1.200E-01, 1.500E-01, 2.000E-01, 2.500E-01, 3.000E-01, 3.600E-01, 4.400E-01, 5.500E-01, 7.000E-01, 8.500E-01, 1.000E+00, 1.150E+00, 1.300E+00, 1.700E+00, 2.000E+00, 2.200E+00, 2.700E+00, 3.000E+00, 3.500E+00, 4.000E+00, 4.500E+00, 5.000E+00, 5.500E+00, 6.000E+00, 6.500E+00, 7.000E+00, 7.500E+00, 8.000E+00, 8.500E+00, 9.000E+00, 9.400E+00, 9.550E+00, 9.700E+00, 9.850E+00, 1.000E+01, 1.050E+01, 1.100E+01, 1.130E+01, 1.160E+01, 1.200E+01, 1.250E+01, 1.300E+01, 1.350E+01, 1.400E+01, 1.450E+01, 1.500E+01, 1.600E+01, 1.700E+01, 1.800E+01, 1.900E+01, 2.000E+01, 2.200E+01, 2.300E+01, 2.400E+01, 2.500E+01, 2.600E+01, 2.700E+01, 2.800E+01, 3.000E+01, 3.500E+01, 4.000E+01, 4.500E+01, 5.000E+01, 5.500E+01, 6.000E+01, 6.500E+01, 7.000E+01, 7.500E+01, 8.000E+01, 8.500E+01, 9.000E+01, 9.500E+01, 1.000E+02, 1.050E+02, 1.100E+02, 1.200E+02, 1.300E+02, 1.400E+02, 1.500E+02, 2.000E+02, 2.500E+02, 3.000E+02, 4.000E+02, 5.000E+02, 7.000E+02, 1.000E+03, 1.500E+03, 2.250E+03, 3.350E+03, 5.000E+03, 7.400E+03, 1.100E+04, 1.300E+04, 1.600E+04, 2.400E+04, 3.600E+04]


def calculate_chi_square(stb_fluxes, obs_fluxes):
    return np.sum(((stb_fluxes - obs_fluxes)**2)/(stb_fluxes**2))

observations_folder = 'Inputs'
stb_folder = 'Grids/M_Lib'
results_file = 'Results_M.csv'


start_time = time.time()

with open(results_file, 'w', newline='') as csvfile:
	writer = csv.writer(csvfile, delimiter='\t')
	writer.writerow(['filename', 'min_chi_square_stb_file', 'L_shift', 'min_chi_square'])
	for filename in os.listdir(observations_folder):
		if filename.endswith('.csv'):
			csv_path = os.path.join(observations_folder, filename)
			observations = pd.read_csv(csv_path, header=None)
			obs_wavelengths = observations.iloc[:, 0].values
			obs_fluxes_nu = observations.iloc[:, 1].values
			obs_fluxes = (C_light/(obs_wavelengths))*(1E-26)*(obs_fluxes_nu)
			distances = np.abs(obs_wavelengths[:,None] - WL_DUSTY) 
			nearest_indices = distances.argmin(axis=1)
			nearest_values = np.array(WL_DUSTY)[nearest_indices.astype(int)]
			min_chi_square_stb_file = None
			min_chi_square = np.inf
			min_chi_square_index = -1
			L_shift=0.0
			for stb_file in os.listdir(stb_folder):
				if stb_file.endswith('.stb'):
					stb_path = os.path.join(stb_folder, stb_file)
    	            # Read the STB file
					stb_data = pd.read_csv(stb_path, comment='#', sep=r'\s+', header=None)
					stb_fluxes = stb_data.iloc[:, 1].values
					stb_fluxes_CSV = np.array(stb_fluxes)[nearest_indices.astype(int)]
					SHIFT=np.abs(np.log10(stb_fluxes_CSV)-np.log10(obs_fluxes))
					for i, shift in enumerate(SHIFT):
						modified_stb_fluxes = np.array(np.log10(stb_fluxes_CSV)) - shift
						chi_square = calculate_chi_square(modified_stb_fluxes, np.log10(obs_fluxes)) 
						if chi_square < min_chi_square:
							min_chi_square = chi_square
							min_chi_square_index = i
							min_chi_square_stb_file = stb_file
							L_shift=shift
    	    
			print(min_chi_square,L_shift,min_chi_square_stb_file)
			writer.writerow([filename, min_chi_square_stb_file, L_shift, min_chi_square])
               
elapsed_time = time.time() - start_time
print(f"Elapsed time: {elapsed_time} seconds")
