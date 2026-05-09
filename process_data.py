import pandas as pd
import os

def combine_data(data_folder='data', start_year=2012, end_year=2025, output_file='eurojackpot_2012_2025_master.csv'):
    """
    Yhdistää vuosittaiset CSV-tiedostot yhdeksi master-tiedostoksi.
    Vastaa 01_combine_data.ipynb -notebookin toiminnallisuutta.
    """
    print("Yhdistetään datatiedostoja...")
    df_list = []
    years = range(start_year, end_year + 1)
    
    for year in years:
        file_path = os.path.join(data_folder, f'eurojackpot_{year}_all_draws.csv')
        if os.path.exists(file_path):
            df_year = pd.read_csv(file_path)
            df_list.append(df_year)
        else:
            print(f"  Tiedostoa ei löytynyt: {file_path}")

    if not df_list:
        print("Ei yhdistettävää dataa.")
        return None

    master_df = pd.concat(df_list, ignore_index=True)
    
    output_path = os.path.join(data_folder, output_file)
    master_df.to_csv(output_path, index=False)
    print(f"Yhdistetty dataset tallennettu: {output_path}")
    
    return output_path


def preprocess_data(input_file, output_file='eurojackpot_data.csv'):
    """
    Esikäsittelee yhdistetyn datan analyysia varten (poistaa valuuttamerkit, muuttaa tyypit yms.).
    Vastaa preprocessing_data.ipynb -notebookin toiminnallisuutta.
    """
    print(f"\nEsikäsitellään tiedostoa: {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"Tiedostoa {input_file} ei löytynyt!")
        return

    df = pd.read_csv(input_file)
    
    # 1. Päivämäärät oikeaan muotoon
    df['short_date'] = pd.to_datetime(df['short_date'], format='%d.%m.%Y', errors='coerce')
    
    # Valuuttamerkkien ja pilkkujen puhdistaminen apufunktiolla. 
    # Huomioidaan sekä '€' että '' (lukuongelmien varalta)
    def clean_currency(column):
        try:
            return column.astype(str).str.replace('€', '', regex=False)\
                         .str.replace(',', '', regex=False)\
                         .str.replace(' ', '', regex=False)\
                         .replace('nan', pd.NA)\
                         .replace('<NA>', pd.NA)
        except Exception:
            return column

    # 2. Jackpotin tyypin muunnos (float)
    if 'jackpot' in df.columns:
        df['jackpot'] = clean_currency(df['jackpot']).astype(float)
        
    # 3. Palkintorahaston tyypin muunnos (Int64 tukee puuttuvia arvoja)
    if 'prize fund' in df.columns:
        df['prize fund'] = clean_currency(df['prize fund']).astype('Int64')
        
    # 4. Voitto/voittaja tyypin muunnos (numeric)
    if 'prize / winner' in df.columns:
        df['prize / winner'] = clean_currency(df['prize / winner'])
        df['prize / winner'] = pd.to_numeric(df['prize / winner'], errors='coerce')

    # 5. Numeroiden muuttaminen listoiksi
    if 'main_numbers' in df.columns:
        df['main_numbers'] = df['main_numbers'].astype(str).apply(
            lambda x: [int(n) for n in x.split()] if x != 'nan' else []
        )
    if 'euro_numbers' in df.columns:
        df['euro_numbers'] = df['euro_numbers'].astype(str).apply(
            lambda x: [int(n) for n in x.split()] if x != 'nan' else []
        )

    # 6. Voittajien lkm
    if '# of winners' in df.columns:
        df['# of winners'] = df['# of winners'].astype(str).str.replace(',', '', regex=False)
        # Muutetaan ensin numeeriseksi, sitten intiksi
        df['# of winners'] = pd.to_numeric(df['# of winners'], errors='coerce')
        # Poistetaan ne mahdolliset nan-rivit tai fiksataan, mutta to_numeric + Int64 handlaa nullit fiksusti
        df['# of winners'] = df['# of winners'].astype('Int64')

    # 7. Match -sarake merkkijonoksi
    if 'Match' in df.columns:
        df['Match'] = df['Match'].astype(str)

    data_folder = os.path.dirname(input_file)
    output_path = os.path.join(data_folder, output_file)
    
    df.to_csv(output_path, index=False)
    print(f"Esikäsitelty data tallennettu: {output_path}")

if __name__ == "__main__":
    # 1. Yhdistetään datat
    master_file = combine_data()
    
    # 2. Esikäsitellään datat
    if master_file:
        preprocess_data(master_file)
