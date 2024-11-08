import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import math

def performance_to_float(performance: str, technical: bool) -> int | None:
    # Combined Events or One Hour Race
    performance = performance.strip().replace(',', '.')
    if technical:
        parsed_value = int(performance.replace('.', ''))
        if str(parsed_value) == performance.replace('.', ''):
            return parsed_value

    if technical:
        try:
            converted_performance = float(performance)
            return 0 if math.isnan(converted_performance) else int(round(converted_performance * 100))
        except ValueError:
            return 0

    parts = performance.split(':')

    if len(parts) == 1:
        return int(float(parts[0]) * 1000)

    if len(parts) == 2:
        minutes, rest = parts
        seconds = float(rest)
        return int((int(minutes) * 60 + seconds) * 1000)

    if len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
        return int((hours * 3600 + minutes * 60 + seconds) * 1000)

    raise ValueError(f"Invalid performance: {performance}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download performances for a specific event")
    parser.add_argument("--eventcode", help="Event code", required=True)
    parser.add_argument("--classcode", help="Class code", required=True)
    parser.add_argument("--environment", help="Environment", default=1, type=int)
    parser.add_argument("--year", help="Year", required=True, type=int)
    parser.add_argument("--showForeigners", help="Show foreigners", default=1)
    parser.add_argument("--search", help="Search")
    parser.add_argument("--page", help="Page", default=1, type=int)
    parser.add_argument("--output", help="Output file", required=True)
    parser.add_argument("--performanceList", help="Performance list id", required=True)
    parser.add_argument("--technical", type=int , help="Technical event", default=None, choices=[1, 0])
    parser.add_argument("--sex", type=str , choices=["M", "W", "X"])

    args = parser.parse_args()

    performanceList = args.performanceList
    eventcode = args.eventcode
    classcode = args.classcode
    environment = args.environment
    year =  args.year
    showForeigners = args.showForeigners
    search = args.search
    page = args.page
    technical = args.technical
    sex = ("M" if classcode.startswith("M") else "W") if args.sex is None else args.sex

    url = f"https://bestenliste.leichtathletik.de/Performances?performanceList={performanceList}&eventcode={eventcode}&classcode={classcode}&environment={environment}&year={year}&showForeigners=1&pageNumber={page}"
    if(search):
        url += f"&search={search}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    performance_tables = soup.select("div.performancetable")
    if(len(performance_tables) == 0):
        print("No performances found for event", eventcode, classcode, environment, year, showForeigners, search, page)
        exit(0)

    entry_lines = performance_tables[0].select("div.entryline")
    if(len(performance_tables) > 1):
        entry_lines = performance_tables[1].select("div.entryline")

    entries = []
    
    for entry_line in entry_lines:
        position_element = entry_line.select_one("div.col-5").select_one("div.firstline")
        performance_element = entry_line.select_one("div.col-4").select_one("div.firstline")
        wind_element = entry_line.select_one("div.col-4").select_one("div.secondline")
        name_element = entry_line.select_one("div.col-last").select_one("div.firstline")
        club_element = entry_line.select_one("div.col-last").select_one("div.secondline")
        nationality_element = entry_line.select_one("div.col-3").select_one("div.firstline")
        agegroup_element = entry_line.select_one("div.col-3").select_one("div.secondline")
        date_element = entry_line.select_one("div.col-95p").select_one("div")
        location_element = entry_line.select_one("div.col-95p").select_one("div.secondline")

        date = parsed_date = datetime.strptime(date_element.text.strip(), "%d.%m.%Y")
        performance = performance_element.text.strip()
        wind = float(wind_element.text.strip().replace(",", ".")) if wind_element.text.strip() != "" else None
        location = location_element.text.strip()
        name = name_element.text.strip()
        club = club_element.text.strip()
        nationality = nationality_element.text.strip()
        position = int(position_element.text.strip())
        birthyear = agegroup_element.text.strip().split(" ")[0]
        ageGroup = agegroup_element.text.strip().split(" ")[-1]
        age = year - int(birthyear)

        if performance.endswith("*"):
           print(f"Handtimed performance: {performance} for {name} at {location} on {date} in {eventcode} {classcode}")
           performance = performance[:-1]

        entries.append({
            "position": position,
            "date": date,
            "performance": performance,
            "wind": wind,
            "location": location,
            "name": name,
            "club": club,
            "nationality": nationality,
            "birthyear": birthyear,
            "age": age,
            "ageGroup": ageGroup,
            "eventcode": eventcode,
            "classcode": classcode,
            "environment": environment,
            "technical": technical,
            "sex": sex,
            "performanceValue": performance_to_float(performance, technical) if technical is not None else None
        })

    df = pd.DataFrame(entries)
    df.to_csv(args.output, index=False)