import difflib
import math
import re
from typing import Dict, List, Optional
import urllib.request

URL = "https://www.toyota.ua/new-cars/corolla-cross"

CARS_DATABASE = {
    "Toyota Corolla Cross": {
        "Live": 1445000,
        "Active": 1575000,
        "Lounge": 1745000,
        "GR Sport": 1850000,
    },
    "Toyota Corolla": {
        "City": 980000,
        "Live": 1070000,
        "Active": 1150000,
        "Style": 1240000,
    },
    "Toyota RAV4": {
        "Live": 1520000,
        "Active": 1690000,
        "Lounge": 1920000,
        "Adventure": 2050000,
    },
    "Toyota Camry": {
        "Comfort": 1560000,
        "Elegance": 1710000,
        "Prestige": 1890000,
        "Premium": 2120000,
    },
}


def fetch_site_prices(url: str) -> List[int]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode("utf-8", errors="ignore")
        raw_prices = re.findall(r"\b1[\s\xa0]?\d{3}[\s\xa0]?\d{3}\b", html)
        prices = sorted(
            {
                int(p.replace(" ", "").replace("\xa0", ""))
                for p in raw_prices
                if 1_200_000 <= int(p.replace(" ", "").replace("\xa0", "")) <= 2_500_000
            }
        )
        return prices
    except Exception:
        return []


def smart_find(user_text: str, options: List[str], cutoff: float = 0.45) -> Optional[str]:
    user_clean = user_text.strip().lower()
    if not user_clean:
        return None

    for option in options:
        if user_clean in option.lower():
            return option

    best_match = None
    best_score = 0.0

    for option in options:
        opt_lower = option.lower()
        score_full = difflib.SequenceMatcher(None, user_clean, opt_lower).ratio()

        words = opt_lower.split()
        score_words = max(
            difflib.SequenceMatcher(None, user_clean, word).ratio() for word in words
        )

        score = max(score_full, score_words)
        if score > best_score:
            best_score = score
            best_match = option

    if best_score >= cutoff:
        return best_match
    return None


def main():
    site_prices = fetch_site_prices(URL)
    if len(site_prices) >= len(CARS_DATABASE["Toyota Corolla Cross"]):
        for trim_name, parsed_price in zip(
            CARS_DATABASE["Toyota Corolla Cross"].keys(), site_prices
        ):
            CARS_DATABASE["Toyota Corolla Cross"][trim_name] = parsed_price

    print("Доступні моделі в базі:", ", ".join(CARS_DATABASE.keys()))
    raw_car = input("Введіть назву машини (можна з помилкою, напр. 'corila'): ")

    matched_car = smart_find(raw_car, list(CARS_DATABASE.keys()))
    if matched_car:
        print(f"-> Знайдено модель: {matched_car}")
        car_name = matched_car
        trims: Dict[str, int] = CARS_DATABASE[car_name]
    else:
        print("-> Схожої моделі в базі не знайдено, використовуємо введену назву.")
        car_name = raw_car.strip() or "Toyota Corolla Cross"
        trims = CARS_DATABASE["Toyota Corolla Cross"]

    print(f"\nКомплектації для {car_name}:")
    for trim, price in trims.items():
        print(f" - {trim}: {price:,} грн".replace(",", " "))

    raw_trim = input("\nВведіть комплектацію (можна приблизно, напр. 'lung' або 'aktiv'): ")
    matched_trim = smart_find(raw_trim, list(trims.keys()), cutoff=0.4)

    if matched_trim:
        print(f"-> Обрано комплектацію: {matched_trim}")
        chosen_trim = matched_trim
        car_price = float(trims[chosen_trim])
    else:
        chosen_trim = raw_trim.strip() or "Базова"
        car_price = float(input("Комплектацію не розпізнано. Введіть ціну авто (грн): "))

    salary = float(input("Введіть вашу зарплату за місяць (грн): "))
    expenses = float(input("Введіть щомісячні витрати на їжу, одяг тощо (грн): "))

    net_savings = salary - expenses

    print("\n" + "=" * 45)
    print(f"Машина: {car_name}")
    print(f"Комплектація: {chosen_trim}")
    print(f"Ціна: {car_price:,.0f} грн".replace(",", " "))
    print(f"Залишок за місяць: {net_savings:,.0f} грн".replace(",", " "))

    if net_savings <= 0:
        print("Накопичити на авто неможливо.")
        print("ти не крутий вась іди купи скутера")
    else:
        months = math.ceil(car_price / net_savings)
        years = months / 12
        print(f"Потрібно працювати: {months} міс. ({years:.1f} р.)")
        if years > 10:
            print("ти не крутий вась іди купи скутера")
        else:
            print("Ну ти ЧОТКИЙ пацик Вась")
    print("=" * 45)


if __name__ == "__main__":
    main()