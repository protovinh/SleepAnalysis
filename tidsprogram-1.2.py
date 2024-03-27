import tkinter as tk
from tkinter import ttk
from collections import defaultdict
import csv
from datetime import datetime, timedelta

#Husk å installer de neste tre linjene i command prompt vinduet
#for at programmet har tilgang til riktig bibliotek og kan kjøres
#pip install joblib
#pip install pandas
#pip install -U scikit-learn==1.4.1.post1
from joblib import load
import pandas as pd



filename = 'tider.txt'

# Leser søvndata fra en fil og returnerer en liste med søvndatapunkter
def les_sovn_data(filename):
    sleep_data = []
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Ignorerer headeren i tekstdokumentet
        for row in reader:
            timestamp_str, time_period = row
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            sleep_data.append((timestamp, time_period))
    return sleep_data

#Beregner varigheten av søvn basert på start- og sluttidspunkt
def regn_ut_sovn_mengde(start_time, end_time):
    duration = end_time - start_time
    hours = duration.seconds / 3600
    return hours, minutes



# Beregner gjennomsnittlig søvntid basert på perioden (uke, måned, år).
def regn_ut_gjennomsnitt_sovn_mengde(sleep_data, period):
    # defaultdict er en underklasse av Pythons standard ordbok. Årsaken til å bruke defaultdict
    # istedenfor standard dict er at defaultdict automatisk tildeler en verdi til nøkler som ikke eksisterer.
    # Her tildeler jeg defaultdict en lambda-funksjon som returnerer {'total': timedelta(), 'count': 0}.
    # Dette gjør at jeg ikke trenger å sjekke om en nøkkel eksisterer før jeg tildeler den en verdi,
    # noe som forenkler koden ved å eliminere behovet for eksplisitt nøkkelkontroll.
    sleep_totals = defaultdict(lambda: {'total': timedelta(), 'count': 0})


    # Hjelpefunksjon for å finne ukenummeret i året for en gitt dato
    def finn_riktig_uke(date):
        #Setter datetime objektet til den første dagen i det opgitte året
        #så hvis dagens dato er 24 juni 2024 så settes first_day_of_year til 1.januar 2024
        first_day_of_year = datetime(date.year, 1, 1)
        #her tas en gitt dato og trekker fra antall dager siden første dag i året og plusser på 1 for 1 januar må tas med
        #i bregningen, så på denne måten finner programmet den nøyaktige dagen brukeren er ute etter
        day_of_year = (date - first_day_of_year).days + 1
        #for å finne en gitt uke så tas dagen og trekker fra day_of_year for å nulstille beregningen,
        #så deles det på 7 for å finne antall hele uker som har passert, også
        #legges det til +1 på slutten da programmet begynner å telle fra uke 1 og ikke uke 0 siden det ikke eksisterer
        week_of_year = (day_of_year - 1) // 7 + 1
        return week_of_year
    #Løkke som looper gjennom søvn data hvor den starter på indeks plass 0, og leser så lenge det er sleep_data
    #tilgjengelig, denne lesningen gjøres i iterasjoner av 2 grunnet det er en kveld og en morning per søvn tid informasjon
    for i in range(0, len(sleep_data), 2):
        start_timestamp, _ = sleep_data[i]
        #Sikkerhets sjekken sjekker at lengden av søvn data er mer enn 1 i neste iterasjon så det ikke blir indekserings feil
        if i + 1 < len(sleep_data):
            end_timestamp, _ = sleep_data[i + 1]
            sleep_duration = end_timestamp - start_timestamp
            #Bestemmer om det er måned, uke eller år det er snakk om
            if period == 'month':
                #02d brukes på mnd/uke for å sikre at de alltid har 2 siffer, år trenger ikke dette da det alltid har 4 siffer
                #denne tvunget 2 siffer strukturen sørger for en konsistent nøkkelformatering og gjør sortering/sammenligning lettere
                #uten denne strukturen måtte det tas høyde for uke 1 og uke 10 med helt forskjellig struktur, isten for uke 01 og uke 10 med helt lik struktur
                key = f"{start_timestamp.year}-{start_timestamp.month:02d}"
            elif period == 'year':
                key = str(start_timestamp.year)
            elif period == 'week':
                week_of_year = finn_riktig_uke(start_timestamp)
                key = f"{start_timestamp.year}-{week_of_year:02d}"

            #Legger til sovetid til totalen som brukes i gjennomsnitts beregninger
            sleep_totals[key]['total'] += sleep_duration
            sleep_totals[key]['count'] += 1

    #Regner ut gjennomsnittlig søvn tid for de forskjellige periodene
    average_sleep_times = {}
    for key, value in sleep_totals.items():
        if value['count'] == 0:
            continue
        average_duration = value['total'] / value['count']
        hours = int(average_duration.total_seconds() // 3600)
        minutes = int((average_duration.total_seconds() % 3600) // 60)
        average_sleep_times[key] = (hours, minutes)

    return average_sleep_times


def kategoriser_sovn_kvalitet(sleep_duration_hours):
        # Kartlegger søvn mengde kategorier til integers eller tall, slik at en maskin lærnings modell kan bruke det
    label_mapping = {
        'For lite søvn': 0,
        'Bra': 1,
        'For mye søvn': 2
    }
    if sleep_duration_hours < 7:
        return 'For lite søvn'
    elif sleep_duration_hours > 9:
        return 'For mye søvn'
    else:
        return 'Bra'



#Funksjon som åpner vindu for å vise alle de forskjellige søvn datoene
def aapne_sovn_dato_vindu():
    #Viser søvn informasjon for en spesifikk dato brukeren trykker på
    def vis_sovn_info(selected_date):
        for i in range(0, len(sleep_data), 2):
            start_timestamp, _ = sleep_data[i]
            if start_timestamp.date() == selected_date:
                if i + 1 < len(sleep_data):  # Sikrer at indeksering ikke blir out of range hvis det er slutt/mangler data
                    end_timestamp, _ = sleep_data[i + 1]
                    #Renger ut søvn durasjon i timer og minutter
                    sleep_duration = end_timestamp - start_timestamp
                    sleep_duration_hours = int(sleep_duration.total_seconds() // 3600)  # Timer som integer
                    sleep_duration_minutes = int((sleep_duration.total_seconds() % 3600) / 60)  # og resten av minuttene etter hele timer er slutt
                    #Regner ut søvn kvalitet
                    sleep_quality = kategoriser_sovn_kvalitet(sleep_duration_hours + sleep_duration_minutes / 60.0)
                    sleep_info_label.config(text=f"Dato: {start_timestamp.strftime('%Y-%m-%d')}\nStart: {start_timestamp.strftime('%H:%M')}\nSlutt: {end_timestamp.strftime('%H:%M')}\nVarighet: {sleep_duration_hours} timer {sleep_duration_minutes} minutter\nSøvnkvalitet: {sleep_quality}")
                    return
        sleep_info_label.config(text="Ingen søvn data tilgjengelig for den valgte datoen")


    #Dette er variabelen for det nye vinduet som opprettes og er knytett til spesifikke datoer
    dates_window = tk.Toplevel(root)
    #Setter navn på vindu
    dates_window.title("Søvn datoer")
    #Setter en spesifikk pixel størrelse på vinduet når det åpnes opp
    dates_window.geometry("300x700")
    #knytter variabel navnet filename til tekst filen 'tider.txt'
    filename = 'tider.txt'
    #knytter variabel navnet sleep_data til at den skal bruke funksjonen lagd tidligere i programmet les_sovn_data
    #og bruke denne fil lesnings funksjonen på variabel navnet filename som nå er knyttet til tider.txt filen
    sleep_data = les_sovn_data(filename)
    #Undertittel i det nye vinduet "Søvn datoer"
    dates_label = tk.Label(dates_window, text="Velg en dato for å vise søvn data:")
    dates_label.pack(anchor=tk.W)

    frame = tk.Frame(dates_window)
    frame.pack(fill=tk.BOTH, expand=True)

    date_listbox = tk.Listbox(frame)
    date_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    #Oppretter en scrollbar på høyre side som skroller vertikalt
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=date_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    #knytter det til en yscrollcommand som da er vertikal, med en xscrollcommand ville det vært horisontal skrolling
    date_listbox.config(yscrollcommand=scrollbar.set)
    #Fyller opp søvn data GUI boksen med søvn data
    for i in range(0, len(sleep_data), 2):
        start_timestamp, _ = sleep_data[i]
        #strftime formaterer dato og tidsobjekter til en year,month,day struktur som gjør det lesbart og kan vises i GUI'en
        #tk.END sørger for at hver nye data settes inn på slutten av listen, dette sikrer forutsigbar vising i riktig rekkefølge
        date_listbox.insert(tk.END, start_timestamp.strftime("%Y-%m-%d"))


    #Denne kode delen er en eventhandler som vil bli tatt i bruk når et event oppstår,
    #som når brukeren trykker på en av datoene i listen til søvn datoer funksjonen så vil det vises søvn mengde og om det er for lite/mye eller bra. 
    def spesifikk_dato_valg(event):
        #her knyttes index til date_listboxen som er listboxen med dato data i søvn dato vinduet
        index = date_listbox.curselection()
        #Sjekker om brukeren har valgt en dato i listen
        if index:
            #Hvert element i søvn dataen representerer to linjer, kveld og morgen men siden hver data linje i indeks listen kun viser en data
            #så må indeksen dobles for å samsvare med startpunktet i listen
            selected_index = index[0] * 2
            #Her filtreres det ut slutt tidspunktet siden det kun benyttes av start punktene i listen for visuell lettere lesbarhet
            start_timestamp, _ = sleep_data[selected_index]
            #Her kallse vis_sovn_info funksjonen og knytter det til start_timestamp.date variabelen
            vis_sovn_info(start_timestamp.date())

    date_listbox.bind("<<ListboxSelect>>", spesifikk_dato_valg)

    sleep_info_label = tk.Label(dates_window, text="")
    sleep_info_label.pack()

    #Knappen som lukker søvn datoer vinduet
    close_button = tk.Button(dates_window, text="Lukk", command=dates_window.destroy)
    close_button.pack(side=tk.BOTTOM, padx=10, pady=10)


def aapne_gjennomsnitt_sovn_vindu():
    avg_window = tk.Toplevel(root)
    avg_window.title("Gjennomsnittlig søvn tid")
    avg_window.geometry("1300x400")

    #instansierer variabelen sleep_data som leser søvn data fra tekstfilen tider.txt
    sleep_data = les_sovn_data(filename)

    #kaller på regn_ut_gjennomsnitt_sovn_mengde funksjonen og knytter det til søvn data variabelen sleep_data som leser gjennom søvn data filen
    #ved bruk av flere forskjellige funksjoner leser programmet gjennom tekstfilen og regner ut gjennomsnittlig søvn mengde for de
    #forskjellige tids periodene av ukentlig gjennomsnitt, månedlig og årlig gjennomsnittlig søvn tid
    average_sleep_times_weekly = regn_ut_gjennomsnitt_sovn_mengde(sleep_data, period='week')
    average_sleep_times_monthly = regn_ut_gjennomsnitt_sovn_mengde(sleep_data, period='month')
    average_sleep_times_yearly = regn_ut_gjennomsnitt_sovn_mengde(sleep_data, period='year')

    weekly_frame = tk.Frame(avg_window)
    weekly_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    weekly_label = tk.Label(weekly_frame, text="Ukentlig gjennomsnittlig søvn tid")
    weekly_label.pack()

    weekly_text = tk.Text(weekly_frame, height=20, width=30)
    weekly_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    weekly_scrollbar = tk.Scrollbar(weekly_frame, orient=tk.VERTICAL, command=weekly_text.yview)
    weekly_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    weekly_text.config(yscrollcommand=weekly_scrollbar.set)

    for week, (hours, minutes) in average_sleep_times_weekly.items():
        weekly_text.insert(tk.END, f"Week {week}: {hours} hours {minutes} minutes\n")

    monthly_frame = tk.Frame(avg_window)
    monthly_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    monthly_label = tk.Label(monthly_frame, text="Månedlig gjennomsnittlig søvn tid")
    monthly_label.pack()
    monthly_text = tk.Text(monthly_frame, height=20, width=40)
    monthly_text.pack()
    for month_key, (hours, minutes) in average_sleep_times_monthly.items():
        year, month = month_key.split('-')  # Splitter nøkkelen for å hente år+måned
        month_name = datetime.strptime(month, '%m').strftime('%B')  # Endrer måned nummer til navn så det blir lettere for brukeren å lese
        formatted_month = f"{month_name} {year}"  # Kombinerer måned med riktig år
        monthly_text.insert(tk.END, f"{formatted_month}: {hours} hours {minutes} minutes\n")

    yearly_frame = tk.Frame(avg_window)
    yearly_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    yearly_label = tk.Label(yearly_frame, text="Årlig gjennomsnittlig søvn tid")
    yearly_label.pack()
    yearly_text = tk.Text(yearly_frame, height=20, width=30)
    yearly_text.pack()
    for year, (hours, minutes) in average_sleep_times_yearly.items():
        yearly_text.insert(tk.END, f"{year}: {hours} hours {minutes} minutes\n")

    close_button = tk.Button(avg_window, text="Lukk", command=avg_window.destroy)
    close_button.pack(side=tk.BOTTOM, padx=10, pady=10)

    




#Laster in MaskinLærings modellen som forutser fremtidig søvn durasjon
#Dette gjøres globalt kun en gang i programmet
model = load('sovn_durasjon_model.joblib')


# Dette er en funksjon for å predikere søvn mengde på en gitt dag(ikke i bruk) da det ble krasj med måned prediksjon
def lag_prediksjon_uke(day_of_week):
    input_df = pd.DataFrame([day_of_week], columns=['DayOfWeek'])
    predicted_duration = model.predict(input_df)[0]
    return predicted_duration

def vis_ml_prediksjon():
    prediksjons_vindu = tk.Toplevel(root)
    prediksjons_vindu.title("Søvn lengde Prediksjon")
    prediksjons_vindu.geometry("400x300")
    #Setter labels eller string verdi navn til hver enkelt måned i en dropdown meny hvor brukeren skal velge
    #hvem måned i året det ønskes å få en prediksjon for fortventet søvn mengde
    tk.Label(prediksjons_vindu, text="Velg måned:").pack(pady=10)
    months = ["Januar", "Februar", "Mars", "April", "Mai", "Juni",
              "Juli", "August", "September", "Oktober", "November", "Desember"]
    month_var = tk.StringVar(prediksjons_vindu)
    month_var.set(months[0])  # Default verdi satt til indeks plass 0 da listen begynner på 0 og er Januar
    month_dropdown = tk.OptionMenu(prediksjons_vindu, month_var, *months)
    month_dropdown.pack()

    prediction_label = tk.Label(prediksjons_vindu, text="")
    prediction_label.pack(pady=20)

    def oppdater_prediksjon():
        month_index = months.index(month_var.get()) + 1  # +1 fordi måneder er indeksert til å være 1-basert i datetime
        features_df = pd.DataFrame([[month_index]], columns=['Month'])
        
        try:
            predicted_duration_hours = model.predict(features_df)[0]
            hours = int(predicted_duration_hours)
            minutes = int((predicted_duration_hours - hours) * 60)
            #Her bestemmes tilbakemelding bruker får basert på ML modellen sin prediksjon hvor beskjedene deles
            #på søvn mengde mindre enn 7 timer, 7 eller mer men også 9 eller mindre, og til slutt mer enn 9 timer
            if predicted_duration_hours < 7:
                sleep_quality_message = f"Det er forventet at du får for lite søvn i {month_var.get()},\nikke drikk koffein etter klokken 16:00,\nprøv å unngå skjermtid en time før sengetid."
            elif 7 <= predicted_duration_hours <= 9:
                sleep_quality_message = f"Det er forventet at du får en optimal mengde søvn i {month_var.get()},\ningen behov for forandring."
            else:
                sleep_quality_message = f"Det er forventet at du får for mye søvn i {month_var.get()},\nvurder å legge deg litt senere."

            prediction_label.config(text=f"Forventet søvn varighet i {month_var.get()}: {hours}h {minutes}min.\n{sleep_quality_message}")
        except Exception as e:
            prediction_label.config(text=f"Feil: {e}")
    #Knappen brukeren trykker på etter å ha valgt en spesifikk måned som da vil gi ML prediksjon på forventet søvn mengde
    prediksjon_button = tk.Button(prediksjons_vindu, text="Prediker", command=oppdater_prediksjon)
    prediksjon_button.pack(pady=10,padx=25)
    #Knappen som lukker ML vinduet
    lukk_button = tk.Button(prediksjons_vindu, text="Lukk", command=prediksjons_vindu.destroy)
    lukk_button.pack(side=tk.BOTTOM, padx=10, pady=20)




#Instansierer hoved GUI vinduet for programmet
root = tk.Tk()
root.title("Søvn data")
window_size = "250x200"

# Regner ut størrelse på skjerm og sørger for at vinduet havner midt på skjermen til brukeren når det startes opp
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
window_width, window_height = map(int, window_size.split('x'))
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
root.geometry(f"{window_size}+{center_x}+{center_y}")

# Her legges de forskjellige GUI knappene som er knyttet til nye vinduer med relevante funksjoner

#Gjennomsnittlig søvn for uker,måneder og år knapp
gjennomsnitt_sovn_button = tk.Button(root, text="Gjennomsnittlig søvn tid", command=aapne_gjennomsnitt_sovn_vindu)
gjennomsnitt_sovn_button.pack(padx=10, pady=10)

#Søvn datoer knappen
sovn_dato_button = tk.Button(root, text="Søvn datoer", command=aapne_sovn_dato_vindu)
sovn_dato_button.pack(padx=10, pady=10)

# ML prediksjons knappen
ml_prediksjons_button = tk.Button(root, text="Maskin Læring Forventet søvn", command=vis_ml_prediksjon)
ml_prediksjons_button.pack(padx=20, pady=20)


#Knapp som lukker hele programmet
lukk_program_button = tk.Button(root, text="Lukk", command=root.destroy)
lukk_program_button.pack(side=tk.BOTTOM, padx=10, pady=10)


root.mainloop()
