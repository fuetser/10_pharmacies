import io
import sys
from PIL import Image
import requests


def get_middle_point(address):
    payload = {
        "geocode": address,
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "format": "json"
    }
    resp = requests.get("http://geocode-maps.yandex.ru/1.x/", params=payload)
    if resp.ok:
        json_resp = resp.json()
        pos = json_resp["response"]["GeoObjectCollection"]["featureMember"][0][
            "GeoObject"]["Point"]["pos"].replace(" ", ",")
        return pos


def get_pharmacies(center):
    payload = {
        "apikey": "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3",
        "text": "аптека",
        "ll": center,
        "lang": "ru_RU",
        "type": "biz"
    }
    resp = requests.get("https://search-maps.yandex.ru/v1/", params=payload)
    if resp.ok:
        return resp.json()["features"][:10]


def parse_pharmacies(data):
    addresses = []
    for pharamcy in data:
        address = pharamcy['properties']['description']
        hours = pharamcy["properties"]["CompanyMetaData"]["Hours"][
            "Availabilities"][0]
        mark = "pm2grm"
        if hours.get("TwentyFourHours") is not None:
            mark = "pm2gnm"
        elif hours.get("Intervals") is not None:
            mark = "pm2dbm"
        pos = get_middle_point(address)
        addresses.append((pos, mark))
    return addresses


def show_map(middle_pos, pharmacies):
    payload = {
        "ll": middle_pos,
        "l": "map",
        "pt": "~".join(["{},{}".format(*ph) for ph in pharmacies])
    }
    resp = requests.get("http://static-maps.yandex.ru/1.x/", params=payload)
    if resp.ok:
        Image.open(io.BytesIO(resp.content)).show()


def main():
    # middle_pos = get_middle_point(" ".join(sys.argv[1:]))
    middle_pos = get_middle_point("москва проспект мира 10")
    json_data = get_pharmacies(middle_pos)
    parsed_data = parse_pharmacies(json_data)
    show_map(middle_pos, parsed_data)


if __name__ == '__main__':
    main()
