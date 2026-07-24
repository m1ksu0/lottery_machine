import streamlit as st
import pandas as pd
import ast
import os

st.set_page_config(page_title="Eurojackpot Analyzer", layout="wide")

@st.cache_data
def load_data(filepath='data/eurojackpot_data.csv'):
    if not os.path.exists(filepath):
        st.error(f"Datatiedostoa '{filepath}' ei löytynyt!")
        st.error("Aja ensin 'process_data.py' jotta data luodaan.")
        return None

    df = pd.read_csv(filepath)

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
    main_flat = [num for sublist in df['main_numbers'].dropna() for num in sublist]
    euro_flat = [num for sublist in df['euro_numbers'].dropna() for num in sublist]

    main_counts = pd.Series(main_flat).value_counts()
    euro_counts = pd.Series(euro_flat).value_counts()

    st.header("📈 TÄHTINUMEROIDEN ANALYYSI")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("--- KUUMIMMAT JA KYLMIMMÄT PÄÄNUMEROT ---")
        st.write(f"🔥 Kuumimmat 5 päänumeroa: {', '.join(str(x) for x in main_counts.head(5).index)}")
        st.write(f"❄️  Kylmimmät 5 päänumeroa: {', '.join(str(x) for x in main_counts.tail(5).index)}")

    with col2:
        st.subheader("--- YLEISIMMÄT EURO-NUMEROT ---")
        st.write(f"⭐ Yleisimmät 2 Euro-numeroa:   {', '.join(str(x) for x in euro_counts.head(2).index)}")
        st.write(f"💤 Harvinaisimmat 2 numeroa:    {', '.join(str(x) for x in euro_counts.tail(2).index)}")

def biggest_jackpots(df):
    st.header("--- 💰 SUURIMMAT POTIT HISTORIASSA ---")

    top_jackpots = df.sort_values(by='jackpot', ascending=False).drop_duplicates(subset=['short_date']).head(5)

    for idx, row in top_jackpots.iterrows():
        try:
            jackpot_val = int(row['jackpot']) if not pd.isna(row['jackpot']) else 0
            date_str = pd.to_datetime(row['short_date']).strftime('%d.%m.%Y')
            formatted_jackpot = f"{jackpot_val:,.0f} €".replace(',', ' ')
            st.write(f"📅 {date_str}: {formatted_jackpot} \t| Päänumerot: {row['main_numbers']} Euro: {row['euro_numbers']}")
        except ValueError:
            pass

def recommend_by_jackpot(df):
    st.header("🔮 NUMEROEHDOTUS NYKYISEN JÄTTIPOTIN MUKAAN")

    user_input = st.text_input("Syötä Eurojackpotin päävoitto miljoonina (esim. 10 tai 45,5):", value="")

    if user_input:
        try:
            target_jackpot = float(user_input.replace(' ', '').replace(',', '.')) * 1000000
            margin = 5000000.0

            matches = df[(df['jackpot'] >= target_jackpot - margin) & (df['jackpot'] <= target_jackpot + margin)]

            if matches.empty:
                st.warning(f"Oops! Rekisteristä ei löytynyt yhtäkään pottia joka olisi edes lähellä ~{target_jackpot:,.0f} € summaa.")
            else:
                matches = matches.sort_values(by='short_date', ascending=False)
                matches = matches[matches['main_numbers'].apply(lambda x: len(x) == 5)]
                all_matches = matches.drop_duplicates(subset=['short_date'])
                recent_matches = all_matches.head(5)

                st.subheader(f"Samanlaisten jättipottien (±5 milj. €) aikana on arvottu mm. seuraavat rivit:")
                for idx, row in recent_matches.iterrows():
                    date_str = pd.to_datetime(row['short_date']).strftime('%d.%m.%Y')
                    jackpot_formatted = f"{int(row['jackpot']):,.0f} €".replace(',', ' ')

                    second_prize_row = df[(df['short_date'] == row['short_date']) & (df['Match'] == '5 + 1')]
                    second_prize_info = ""
                    if not second_prize_row.empty:
                        prize_val = second_prize_row.iloc[0]['prize / winner']
                        if pd.notna(prize_val):
                            prize_formatted = f"{int(prize_val):,.0f} €".replace(',', ' ')
                            second_prize_info = f" (5+1 voittosumma: {prize_formatted})"

                    st.write(f"[{date_str} | {jackpot_formatted}] Päänumerot: {row['main_numbers']} Euro: {row['euro_numbers']}{second_prize_info}")

                main_flat = [num for sublist in all_matches['main_numbers'] for num in sublist]
                euro_flat = [num for sublist in all_matches['euro_numbers'] for num in sublist]

                if main_flat and euro_flat:
                    best_mains = pd.Series(main_flat).value_counts().head(5).index.tolist()
                    best_euros = pd.Series(euro_flat).value_counts().head(2).index.tolist()

                    st.success(f"🏆 TOIMIVIMMAT NUMEROT ({target_jackpot/1000000:g} milj. € päävoitolle)")
                    st.write(f"Näitä on arvottu eniten vastaavissa ({len(all_matches)} kpl) arvonnoissa:")
                    st.write(f"Päänumerot: {sorted(best_mains)}  |  Euro: {sorted(best_euros)}")

        except ValueError:
            st.error("❌ Virheellinen syöte. Syötä numeroita miljoonina, esimerkiksi '10' tai '45,5'.")

st.title("Eurojackpot Analyzer")
dataframe = load_data()
if dataframe is not None:
    analyze_frequencies(dataframe)
    st.divider()
    biggest_jackpots(dataframe)
    st.divider()
    recommend_by_jackpot(dataframe)
