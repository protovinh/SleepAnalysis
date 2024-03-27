import RPi.GPIO as GPIOimport time
import csv
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# Instansierer Firebase SDK
cred = credentials.Certificate("sleepdata-fa7f0-firebase-adminsdk-m40oa-44e253608c.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://sleepdata-fa7f0-default-rtdb.europe-west1.firebasedatabase.app/'
})

# GPIO setup
GPIO.setmode(GPIO.BCM)
#Her skapes variabelen PIR_PIN og knyttes til pin nummer 17 på raspberryen
PIR_PIN = 17
GPIO.setup(PIR_PIN, GPIO.IN)

# Beregner om det er morgen eller kveld
def get_time_period():
    current_hour = datetime.now().hour
    if current_hour < 20:
        return "Morning"
    else:
        return "Night"

# Skriv til firebase
def write_to_firebase(current_time, time_period):
    ref = db.reference('/movement_logs')
    ref.push({
        'timestamp': current_time,
        'period': time_period
    })



# Hoved funksjonen
def main():
    filename = "tider.txt"
    while True:
        if GPIO.input(PIR_PIN):
            now = datetime.now()
            current_time = now.strftime("%Y-%m-%d %H:%M:%S")
            time_period = get_time_period()

            # Her skrives det til en CSV som betyr comma separated values fil
            with open(filename, "a") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([current_time, time_period])
                print("Bevegelse registrert:", current_time, "(", time_period, ")")

            # Skriv til databasen i Firebase
            write_to_firebase(current_time, time_period)
            # Delay i 5 sekunder når bevegelse har blitt oppdaget for å redusere sjangse for feil registrering
            time.sleep(5)
            #hvis bevegelse ikke har blitt oppdaget så vil pir sensoren sjekke hvert 0.1 sekund for bevegelse
        else:
            time.sleep(0.1)

if __name__ == "__main__":
    try:
        print("Program begynt")
        main()
    except KeyboardInterrupt:
        print("Program avsluttet")
        GPIO.cleanup()
