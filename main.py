import argparse
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download performances for a specific event")
    parser.add_argument("--performanceList", help="Performance list id")
    parser.add_argument("--eventcode", help="Event code", required=True)
    parser.add_argument("--classcode", help="Class code", required=True)
    parser.add_argument("--environment", help="Environment", default=1, type=int)
    parser.add_argument("--year", help="Year", required=True, type=int)
    parser.add_argument("--showForeigners", help="Show foreigners", default=1)
    parser.add_argument("--search", help="Search")
    parser.add_argument("--page", help="Page", default=1, type=int)
    parser.add_argument("--output", help="Output file", required=True)
    parser.add_argument("--performanceList", help="Performance list id", required=True)

    args = parser.parse_args()

    performanceList = args.performanceList
    eventcode = args.eventcode
    classcode = args.classcode
    environment = args.environment
    year =  args.year
    showForeigners = args.showForeigners
    search = args.search
    page = args.page

    url = f"https://bestenliste.leichtathletik.de/Performances?performanceList={performanceList}&eventcode={eventcode}&classcode={classcode}&environment={environment}&year={year}&showForeigners=1&pageNumber={page}"
    if(search):
        url += f"&search={search}"
    print(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    performance_tables = soup.select("div.performancetable")
    if(len(performance_tables) == 0):
        print("No performances found")
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
        print(position,date,performance,wind,location,name,club,nationality,birthyear, ageGroup)
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
            "ageGroup": ageGroup,
            "eventcode": eventcode,
            "classcode": classcode,
            "environment": environment,
        })

    df = pd.DataFrame(entries)
    df.to_csv(args.output, index=False)