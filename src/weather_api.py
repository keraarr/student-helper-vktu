import requests

API_KEY = "4915173ed1f55513ea418007b46a4f8d"  # вставь сюда свой ключ

def get_weather_now(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ru"
    r = requests.get(url)
    data = r.json()

    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]

    advice = get_advice(temp)

    return f"Сейчас в {city}:\n{temp}°C, {desc}\n\n{advice}"


def get_weather_forecast(city, days=1):
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric&lang=ru"
    r = requests.get(url)
    data = r.json()

    # берём прогноз через 24ч (примерно)
    index = 8 * days
    item = data["list"][index]

    temp = item["main"]["temp"]
    desc = item["weather"][0]["description"]

    advice = get_advice(temp)

    day_text = "Сегодня" if days == 0 else "Завтра"

    return f"{day_text} в {city}:\n{temp}°C, {desc}\n\n{advice}"


def get_advice(temp):
    if temp <= 0:
        return "❄️ Очень холодно — надень тёплую куртку, шапку и перчатки"
    elif temp <= 10:
        return "🧥 Прохладно — куртка или худи будет норм"
    elif temp <= 20:
        return "👕 Норм погода — можно в лёгкой одежде"
    elif temp <= 30:
        return "☀️ Тепло — футболка/шорты идеально"
    else:
        return "🔥 Очень жарко — пей воду и надевай что-то лёгкое"