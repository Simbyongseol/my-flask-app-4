from flask import Flask, request, jsonify
import requests
import random
import csv
import schedule
import time
from collections import Counter
from datetime import datetime

app = Flask(__name__)

WEATHER_API_KEY = 'd4a828a7cd2ef69eae63ec87aaba688'
NASA_API_KEY = '8kc8ru17I0hlNwr8s0dpM1UpVCTVpDrELWbITtB'
NOAA_API_KEY = 'mwtBWFzDKRnXTxLxdjxnalFfXvMnGpe'

WEATHER_API_URL = f"http://api.openweathermap.org/data/2.5/weather?q=Seoul&appid={WEATHER_API_KEY}"
MAGNETIC_API_URL = f"https://api.noaa.gov/magnetic?date={datetime.today().strftime('%Y-%m-%d')}&api_key={NOAA_API_KEY}"
SOLAR_ACTIVITY_API_URL = f"https://api.nasa.gov/DONKI/FLR?startDate={datetime.today().strftime('%Y-%m-%d')}&api_key={NASA_API_KEY}"

weather_data = None
magnetic_data = None
solar_activity_data = None

def read_lotto_numbers(filename):
    past_lotto_numbers = []
    try:
        with open(filename, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                past_lotto_numbers.append([int(num) for num in row])
        print("CSV 파일에서 읽은 로또 번호:", past_lotto_numbers)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    return past_lotto_numbers

def fetch_weather_data():
    global weather_data
    try:
        response = requests.get(WEATHER_API_URL)
        weather_data = response.json()
        print("Fetched weather data:", weather_data)
    except Exception as e:
        print(f"Error fetching weather data: {e}")

def fetch_magnetic_data():
    global magnetic_data
    try:
        response = requests.get(MAGNETIC_API_URL)
        magnetic_data = response.json()
        print("Fetched magnetic data:", magnetic_data)
    except Exception as e:
        print(f"Error fetching magnetic data: {e}")

def fetch_solar_activity_data():
    global solar_activity_data
    try:
        response = requests.get(SOLAR_ACTIVITY_API_URL)
        solar_activity_data = response.json()
        print("Fetched solar activity data:", solar_activity_data)
    except Exception as e:
        print(f"Error fetching solar activity data: {e}")

def schedule_updates():
    schedule.every().day.at("00:00").do(fetch_weather_data)
    schedule.every().day.at("00:00").do(fetch_magnetic_data)
    schedule.every().day.at("00:00").do(fetch_solar_activity_data)
    while True:
        schedule.run_pending()
        time.sleep(1)

def analyze_past_numbers(past_numbers):
    all_numbers = [num for sublist in past_numbers for num in sublist]
    counter = Counter(all_numbers)
    common_numbers = counter.most_common(6)
    return [num for num, count in common_numbers]

def generate_lotto_numbers(past_numbers, user_favorites, exclude_numbers):
    if user_favorites is None:
        user_favorites = []
    if exclude_numbers is None:
        exclude_numbers = []

    common_numbers = analyze_past_numbers(past_numbers)
    selected_numbers = set(user_favorites)
    all_numbers = set(range(1, 46)) - set(exclude_numbers)

    while len(selected_numbers) < 6:
        selected_numbers.add(random.choice(list(all_numbers - selected_numbers)))

    return sorted(selected_numbers)

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    user_favorites = data.get('favorites', [])
    exclude_numbers = data.get('excludes', [])

    if len(user_favorites) > 5:
        return jsonify({"error": "행운의 숫자는 최대 5개까지 입력할 수 있습니다."}), 400

    lotto_sets = []
    for _ in range(10):
        lotto_numbers = generate_lotto_numbers(past_lotto_numbers, user_favorites, exclude_numbers)
        lotto_sets.append(lotto_numbers)

    return jsonify({"lotto_sets": lotto_sets})

if __name__ == "__main__":
    schedule_updates()
    import threading
    scheduler_thread = threading.Thread(target=schedule_updates, daemon=True)
    scheduler_thread.start()
    app.run(debug=True)
