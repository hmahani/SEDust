# run_parallel.py
import os
import multiprocessing
import time
import subprocess
import pandas as pd
import glob
from multiprocessing import Pool, cpu_count



def run_script1():
    subprocess.run(["python3", "Codes/C_types.py"])

def run_script2():
    subprocess.run(["python3", "Codes/M_Types.py"])

def run_plotter():
    subprocess.run(["python3", "Codes/Plot.py"])



def extract_parameters(args):
    index, row, base_path, prefix = args
    try:
        stb_file = row['min_chi_square_stb_file']
        out_file = glob.glob(f'{base_path}/{stb_file.replace(".stb", ".out")}')[0]
        out_filename = os.path.basename(out_file)
        original_filename = row['filename']  

        with open(out_file) as f:
            lines = f.readlines()
            star_temp = float(lines[9].split()[2])
            dust_temp = float(lines[19].split()[6])
            tau = float(lines[40].split()[1])
            mdot = float(lines[40].split()[8])

        return index, {
            'filename': original_filename,
            f'{prefix}_OutFile': out_filename,
            f'Star_temperature_{prefix}': star_temp,
            f'Dust_temperature_{prefix}': dust_temp,
            f'Tau_{prefix}': tau,
            f'Mdot_{prefix}': mdot,
            f'L_shift_{prefix}': row['L_shift'],
            f'min_chi_square_{prefix}': row['min_chi_square']
        }

    except Exception as e:
        print(f"Error processing {row.get('filename', 'Unknown')} in {prefix}: {e}")
        return index, {
            'filename': row.get('filename', 'Unknown'),
            f'{prefix}_OutFile': None,
            f'Star_temperature_{prefix}': None,
            f'Dust_temperature_{prefix}': None,
            f'Tau_{prefix}': None,
            f'Mdot_{prefix}': None,
            f'L_shift_{prefix}': None,
            f'min_chi_square_{prefix}': None
        }

def parallel_process(input_csv, base_path, prefix):
    df = pd.read_csv(input_csv, sep='\t')
    args = [(i, row, base_path, prefix) for i, row in df.iterrows()]

    with Pool(processes=cpu_count()) as pool:
        results = pool.map(extract_parameters, args)

    extracted_data = pd.DataFrame([r[1] for r in results])
    return df, extracted_data




if __name__ == "__main__":
    start = time.time()

    print("Running C_types.py and M_Types.py in parallel...")
    p1 = multiprocessing.Process(target=run_script1)
    p2 = multiprocessing.Process(target=run_script2)

    p1.start()
    p2.start()

    p1.join()
    p2.join()
    print("Parallel jobs finished.")


    print("Extracting parameters and combining results...")

    carbon_csv = 'Results_C.csv'
    carbon_path = 'Grids/C_Lib'

    oxygen_csv = 'Results_M.csv'
    oxygen_path = 'Grids/M_Lib'

    carbon_data, carbon_params = parallel_process(carbon_csv, carbon_path, 'C')
    oxygen_data, oxygen_params = parallel_process(oxygen_csv, oxygen_path, 'M')

    combined = pd.DataFrame()
    combined['ID'] = carbon_data.get('ID', pd.Series(range(len(carbon_data))))
    combined = pd.concat([combined, carbon_params, oxygen_params], axis=1)

    combined.to_csv('Combined_Stars.csv', sep='\t', index=False)
    print("Saved: Combined_Stars.csv")


    print("Running plot script...")
    run_plotter()


    print("Post-processing Combined_Stars.csv to generate Results.csv...")

    combined_df = pd.read_csv('Combined_Stars.csv', sep='\t')


    filename_cols = [col for col in combined_df.columns if col.startswith('filename')]

    if len(filename_cols) < 2:
        print("Warning: Expected at least two 'filename' columns, but found less.")
    else:
        combined_df.rename(columns={filename_cols[0]: 'Star_file_name'}, inplace=True)
        combined_df['Star_file_name'] = combined_df['Star_file_name'].str.replace('.csv', '', regex=False)
        combined_df.sort_values(by='Star_file_name', key=lambda x: x.astype(str).astype(int), inplace=True)
        combined_df.to_csv('Results.csv', sep='\t', index=False)
        print("Saved: Results.csv")




    if 'ID' in combined_df.columns:
        combined_df = combined_df.drop(columns=['ID'])
        combined_df.to_csv('Results.csv', sep='\t', index=False)



    csv_files = glob.glob('*.csv')
    for file in csv_files:
        if file != 'Results.csv':
            try:
                os.remove(file)
            except Exception as e:
                print(f"Error deleting {file}: {e}")




    end = time.time()
    print(f"\nTotal elapsed time: {end - start:.2f} seconds")

