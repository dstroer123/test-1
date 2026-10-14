import requests


# Координаты городов: долгота, широта.
CITY_COORDINATES = {
    "алматы": (76.945, 43.238),
    "астана": (71.430, 51.128),
    "шымкент": (69.590, 42.341),
    "караганда": (73.102, 49.806),
    "кокшетау": (69.386, 53.283),
    "актобе": (57.207, 50.283),
    "тараз": (71.366, 42.900),
}


def normalize_city(city):
    """Нормализует название города."""
    return " ".join(city.strip().casefold().split())


class RouteError(Exception):
    """Ошибка при построении автомобильного маршрута."""


def get_route(origin, destination):
    """Возвращает расстояние, время и геометрию маршрута."""
    start = CITY_COORDINATES.get(normalize_city(origin))
    end = CITY_COORDINATES.get(normalize_city(destination))

    if start is None or end is None:
        raise RouteError(
            "Поддерживаются города: Алматы, Астана, Шымкент, "
            "Караганда, Кокшетау, Актобе и Тараз."
        )

    if start == end:
        raise RouteError(
            "Города отправления и назначения должны различаться."
        )

    coordinates = (
        f"{start[0]},{start[1]};{end[0]},{end[1]}"
    )

    url = (
        "https://router.project-osrm.org/route/v1/driving/"
        f"{coordinates}"
    )

    try:
        response = requests.get(
            url,
            params={
                "overview": "full",
                "geometries": "geojson",
            },
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()

    except (requests.RequestException, ValueError) as exc:
        raise RouteError(
            "Сервис маршрутов недоступен. Попробуйте позже."
        ) from exc

    routes = data.get("routes", [])

    if data.get("code") != "Ok" or not routes:
        raise RouteError(
            "Не удалось построить маршрут между городами."
        )

    route = routes[0]

    return {
        "distance_km": round(route["distance"] / 1000, 2),
        "duration_hours": round(route["duration"] / 3600, 2),
        "geometry": route["geometry"],
    }