import requests
import bs4

if __name__ == "__main__":
    response = requests.get("https://bestenliste.leichtathletik.de/")
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    classcode_select = soup.select_one("select#classcode")
    classcode_options = classcode_select.select("option")

    classcodes = []
    for option in classcode_options:
        classcodes.append(option["value"])
    
    print(",".join(classcodes))