import pandas as pd
import glob
import numpy as np
from matplotlib import pyplot as plt
import random
import os
import numpy as np

np.seterr(divide='ignore', invalid='ignore')

results_m = pd.read_csv('Results_M.csv', sep='\t')
results_c = pd.read_csv('Results_C.csv', sep='\t')

merged = results_m.merge(results_c, on='filename')

if not os.path.exists('Plots'):
    os.makedirs('Plots')

for idx, row in merged.iterrows():
    obs_file = glob.glob(f'Inputs/{row["filename"]}')[0]
    obs = pd.read_csv(obs_file, header=None)
    obs_wavelengths = obs.iloc[:, 0]
    obs_fluxes_nu = obs.iloc[:, 1]

    obs_fluxes = (3E14 / (obs_wavelengths)) * (1E-26) * obs_fluxes_nu

    m_file = glob.glob(f'Grids/M_Lib/{row["min_chi_square_stb_file_x"]}')[0]
    c_file = glob.glob(f'Grids/C_Lib/{row["min_chi_square_stb_file_y"]}')[0]

    m_data = pd.read_csv(m_file, comment='#', sep=r'\s+', header=None)
    c_data = pd.read_csv(c_file, comment='#', sep=r'\s+', header=None)

    m_wavelengths = m_data.iloc[:, 0]
    m_fluxes = m_data.iloc[:, 1] / 10 ** row["L_shift_x"]

    c_wavelengths = c_data.iloc[:, 0]
    c_fluxes = c_data.iloc[:, 1] / 10 ** row["L_shift_y"]

    ERx = np.random.uniform(0, 0.4, size=len(obs_wavelengths))
    ERy = np.random.uniform(0, 0.4, size=len(obs_fluxes))
    errx = np.log10(1 + ERx) - np.log10(1)
    erry = np.log10(1 + ERy) - np.log10(1)

    obs_wavelengths_log = np.log10(obs_wavelengths)
    obs_fluxes_log = np.log10(obs_fluxes)
    min_obs_fluxes_log = min(obs_fluxes_log)
    max_obs_fluxes_log = max(obs_fluxes_log)


    errx_log = obs.iloc[:, 2].values
    erry_log = obs.iloc[:, 3].values

    plt.errorbar(obs_wavelengths_log, obs_fluxes_log, xerr=errx_log, yerr=erry_log, fmt='o', ecolor='k', color='black',
                 label='Observed')

    plt.plot(np.log10(m_wavelengths), np.log10(m_fluxes), 'g-', label='Model M')

    plt.plot(np.log10(c_wavelengths), np.log10(c_fluxes), 'r--', label='Model C')

    plt.legend()

    plt.ylim(min_obs_fluxes_log-0.5, max_obs_fluxes_log+0.5)
    plt.xlim(-0.5, 1.5)

    plt.savefig(f'Plots/{row["filename"].replace(".csv", ".png")}')

    plt.close()
