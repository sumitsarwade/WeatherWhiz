from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Database setup
def get_db_connection():
    conn = sqlite3.connect('weather.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to read API key from file
def get_api_key():
    with open('F:/Assignment/Blackcoeffer/Flask_api/Flask-Weather-App/api_key.txt', 'r') as file:
        return file.read().strip()

# OpenWeatherMap API details
API_KEY = get_api_key()
API_URL = f'http://api.openweathermap.org/data/2.5/weather?q={{}}&units=metric&appid={API_KEY}'

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    if request.method == 'POST':
        new_city = request.form.get('city')
        if new_city:
            # Check if city already exists
            existing_city = conn.execute('SELECT * FROM cities WHERE name = ?', (new_city,)).fetchone()
            if existing_city:
                flash('City already exists!', 'error')
            else:
                # Fetch weather data from API
                response = requests.get(API_URL.format(new_city)).json()
                if response['cod'] == 200:
                    conn.execute('INSERT INTO cities (name) VALUES (?)', (new_city,))
                    conn.commit()
                    flash('City added successfully!', 'success')
                else:
                    flash('City does not exist!', 'error')
    # Fetch all cities from the database
    cities = conn.execute('SELECT * FROM cities').fetchall()
    conn.close()

    # Fetch weather data for all cities
    weather_data = []
    for city in cities:
        response = requests.get(API_URL.format(city['name'])).json()
        weather = {
            'city': city['name'],
            'temperature': response['main']['temp'],
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon']
        }
        weather_data.append(weather)

    return render_template('weather.html', weather_data=weather_data)

@app.route('/delete/<name>')
def delete_city(name):
    conn = get_db_connection()
    conn.execute('DELETE FROM cities WHERE name = ?', (name,))
    conn.commit()
    conn.close()
    flash(f'City {name} deleted successfully!', 'success')
    return redirect(url_for('index'))

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        );
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
