import sys
import pandas as pd
import ast
import os

sys.stdout.reconfigure(encoding='utf-8')
def load_data(filepath='data/eurojackpot_data.csv'):
    """
    Lataa prosessoidun datan ja muuttaa listarakenteet oikeaan muotoon analyysia varten.
    """
    if not os.path.exists(filepath):
        print(f"\nDatatiedostoa '{filepath}' ei löytynyt!")
        print("Aja ensin 'process_data.py' jotta data luodaan.\n")
        return None
        
    df = pd.read_csv(filepath)
    
    # Koska listat tallentuvat CSV:hen merkkijonoina (esim. "[1, 2, 3]"),
    # ne täytyy muuntaa takaisin oikeiksi Python-listoiksi.
    def parse_list(val):
        if isinstance(val, str) and val.startswith('['):
            try:
                return ast.literal_eval(val)
            except:
                return []
        return []

    df['main_numbers'] = df['main_numbers'].apply(parse_list)
    df['euro_numbers'] = df['euro_numbers'].apply(parse_list)
    return df

def analyze_frequencies(df):
    """
    Laskee kuumimmat ja kylmimmät päänumerot sekä Euronumerot.
    """
    main_flat = [num for sublist in df['main_numbers'].dropna() for num in sublist]
    euro_flat = [num for sublist in df['euro_numbers'].dropna() for num in sublist]
    
    main_counts = pd.Series(main_flat).value_counts()
    euro_counts = pd.Series(euro_flat).value_counts()
    
    print("\n" + "="*50)
    print("📈 TÄHTINUMEROIDEN ANALYYSI")
    print("="*50)
    
    print("\n--- KUUMIMMAT JA KYLMIMMÄT PÄÄNUMEROT ---")
    print(f"🔥 Kuumimmat 5 päänumeroa: {', '.join(str(x) for x in main_counts.head(5).index)}")
    print(f"❄️  Kylmimmät 5 päänumeroa: {', '.join(str(x) for x in main_counts.tail(5).index)}")
    
    print("\n--- YLEISIMMÄT EURO-NUMEROT ---")
    print(f"⭐ Yleisimmät 2 Euro-numeroa:   {', '.join(str(x) for x in euro_counts.head(2).index)}")
    print(f"💤 Harvinaisimmat 2 numeroa:    {', '.join(str(x) for x in euro_counts.tail(2).index)}")

def biggest_jackpots(df):
    """
    Etsii suurimmat koskaan jaetut jättipotit.
    """
    print("\n--- 💰 SUURIMMAT POTIT HISTORIASSA ---")
    
    # Etsitään isoimmat potit (poistetaan saman päivän rivit)
    top_jackpots = df.sort_values(by='jackpot', ascending=False).drop_duplicates(subset=['short_date']).head(5)
    
    for idx, row in top_jackpots.iterrows():
        try:
            jackpot_val = int(row['jackpot']) if not pd.isna(row['jackpot']) else 0
            date_str = pd.to_datetime(row['short_date']).strftime('%d.%m.%Y')
            formatted_jackpot = f"{jackpot_val:,.0f} €".replace(',', ' ')
            print(f"📅 {date_str}: {formatted_jackpot} \t| Päänumerot: {row['main_numbers']} Euro: {row['euro_numbers']}")
        except ValueError:
            pass

def recommend_by_jackpot(df):
    """
    Kysyy käyttäjältä jättipottia ja ehdottaa numeroita samankokoisten pottien pohjalta.
    """
    print("\n" + "="*50)
    print("🔮 NUMEROEHDOTUS NYKYISEN JÄTTIPOTIN MUKAAN")
    print("="*50)
    
    while True:
        user_input = input("\nSyötä Eurojackpotin päävoitto miljoonina (esim. 10 tai 45)\ntai paina Enter lopettaaksesi: ")
        
        if not user_input.strip():
            print("Lopetetaan analysointi. Onnea arvontaan!")
            break
            
        try:
            # Muutetaan pilkku pisteeksi sallien syötteet tyyliin "10,5", kerrotaan miljoonalla
            target_jackpot = float(user_input.replace(' ', '').replace(',', '.')) * 1000000
            
            # Käytetään kiinteää ±5 miljoonan marginaalia pottien etsimiseen
            margin = 5000000.0
            
            matches = df[(df['jackpot'] >= target_jackpot - margin) & (df['jackpot'] <= target_jackpot + margin)]
            
            if matches.empty:
                print(f"\nOops! Rekisteristä ei löytynyt yhtäkään pottia joka olisi edes lähellä ~{target_jackpot:,.0f} € summaa.")
            else:
                matches = matches.sort_values(by='short_date', ascending=False)
                
                # Suodatetaan pois rivit, joissa ei ole kunnollisia numeroita
                matches = matches[matches['main_numbers'].apply(lambda x: len(x) == 5)]
                
                # Poistetaan saman päivän/arvonnan kaksoiskappaleet
                all_matches = matches.drop_duplicates(subset=['short_date'])
                
                recent_matches = all_matches.head(5)
                
                formatted_target = f"{target_jackpot:,.0f} €".replace(',', ' ')
                print(f"\nSamanlaisten jättipottien (±5 milj. €) aikana on arvottu mm. seuraavat rivit:")
                for idx, row in recent_matches.iterrows():
                    date_str = pd.to_datetime(row['short_date']).strftime('%d.%m.%Y')
                    jackpot_formatted = f"\t{int(row['jackpot']):,.0f} €".replace(',', ' ')
                    
                    # Etsi toiseksi suurin voittoluokka (5+1) samalle päivälle alkuperäisestä datasta
                    second_prize_row = df[(df['short_date'] == row['short_date']) & (df['Match'] == '5 + 1')]
                    second_prize_info = ""
                    if not second_prize_row.empty:
                        prize_val = second_prize_row.iloc[0]['prize / winner']
                        if pd.notna(prize_val):
                            prize_formatted = f"{int(prize_val):,.0f} €".replace(',', ' ')
                            second_prize_info = f"\n\t\t\t\t↳ 5+1 voittosumma: {prize_formatted}"
                    
                    print(f"[{date_str} | {jackpot_formatted}] \tPäänumerot: {row['main_numbers']} Euro: {row['euro_numbers']}{second_prize_info}")
                    
                # Lasketaan "toimivimmat" numerot kyseiselle summalle (kaikki osumat)
                main_flat = [num for sublist in all_matches['main_numbers'] for num in sublist]
                euro_flat = [num for sublist in all_matches['euro_numbers'] for num in sublist]
                
                if main_flat and euro_flat:
                    best_mains = pd.Series(main_flat).value_counts().head(5).index.tolist()
                    best_euros = pd.Series(euro_flat).value_counts().head(2).index.tolist()
                    
                    print("\n" + "-"*60)
                    print(f"🏆 TOIMIVIMMAT NUMEROT ({target_jackpot/1000000:g} milj. € päävoitolle)")
                    print(f"Näitä on arvottu eniten vastaavissa ({len(all_matches)} kpl) arvonnoissa:")
                    print(f"Päänumerot: {sorted(best_mains)}  |  Euro: {sorted(best_euros)}")
                    print("-"*60)
                    
        except ValueError:
            print("❌ Virheellinen syöte. Syötä numeroita miljoonina, esimerkiksi '10' tai '45,5'.")

if __name__ == '__main__':
    dataframe = load_data()
    if dataframe is not None:
        analyze_frequencies(dataframe)
        biggest_jackpots(dataframe)
        recommend_by_jackpot(dataframe)
