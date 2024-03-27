#Import av forskjellige bibliotek som tas i bruk for å manipulere data og trene AI'n som blir brukt i GUI programmet
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

#Husk å installer de neste tre linjene i command prompt vinduet
#for at programmet har tilgang til riktig bibliotek og kan kjøres
#pip install joblib
#pip install pandas
#pip install -U scikit-learn==1.4.1.post1
import pandas as pd
from joblib import dump

def preprocess_data(filename):
    #Print's for å fortelle om dataen lastes inn
    print("Laster data")
    # Laster inn og sorterer data, at det er merket med csv read betyr at den leser en komma separert tekstfil(comma sepparated values)
    #da tekstfilen som brukes "tider.txt" har innholdet sitt organisert i en komma separert struktur
    #skiprows=1 er for at programmet skal hoppe over den første linjen som inneholder overskriften da dette er irrelevant data
    df = pd.read_csv(filename, skiprows=1, names=['DateTime', 'Period'], parse_dates=['DateTime'])
    df.sort_values('DateTime', inplace=True)

    # Regner ut tid sovet basert på night/morning intervaler sine timestamps
    #df står for DataFrame og i panda biblioteket brukes for å holde på forhåndsbehandlet data
    df['NextDateTime'] = df['DateTime'].shift(-1)
    df['Duration'] = (df['NextDateTime'] - df['DateTime']).dt.total_seconds() / 3600

    # Filtrerer data for å beholde natt så lenge det finnes en tilsvarende morgen
    df = df[df['Period'] == 'Night']
    df = df[:-1] if df.iloc[-1]['Period'] == 'Night' else df

    # Henter ut måned
    df['Month'] = df['DateTime'].dt.month

    # Her beholdes kun informasjon om måned, da modellen ble forvirret når jeg prøvde å legge inn uke/dag i tillegg
    df_final = df[['Month', 'Duration']].dropna()

    print(f"Dataen har blitt forhåndsbehandlet, ferdig form: {df_final.shape}")
    return df_final

def tren_og_lagre_model(df, filename='sovn_durasjon_model.joblib'):
    if df.empty:
        print("Ingen tilgjengelig data for trening. Avslutter...")
        return
    
    # Variabel for månedlig informasjon av søvn data
    X = df[['Month']]
    # Variabel for søvn lengde
    Y = df['Duration']
    
    #train_test split test_size=0.2 forteller programmet at den skal splitte dataene hvor den holder tilbake 20%
    #av dataene for testing,og de andre 80% skal brukes til trening av modellen
    X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

    #RandomForestRegressor er en maskinlærings modell fra sklearn biblioteket og brukes til prediksjons trening
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, Y_train)
    model.score(X_train,Y_train)
    #Dump funksjonen serialiserer maskin lærings modellen til en fil slik at det ikke er
    #behov for å trene den på nytt hver gang GUI programmet skal kjøres
    #isteden lages modellen en gang også lastes den ferdige modellen inn i GUI programmet hver gang det startes
    #dette gjør også at ML modellen lett kan brukes i mange forskjellige programmer, så lenge de har tilgang til filen
    dump(model, filename)
    print(model.score(X_test,Y_test))
    print("Model trening fullført og lagret.")

if __name__ == "__main__":
    data = preprocess_data('tider.txt')
    tren_og_lagre_model(data)
