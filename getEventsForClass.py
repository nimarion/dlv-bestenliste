import requests
import pandas as pd
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download performances for a specific event")
    parser.add_argument("--output", help="Output file", required=True)
    parser.add_argument("--classCodes", type=str, help="Class codes", required=True)
    parser.add_argument("--environment", help="Environment", default=1, type=int)
    parser.add_argument("--performanceList", help="Performance list id", required=True)

    args = parser.parse_args()
    environment = args.environment
    performanceList = args.performanceList

    for classCode in args.classCodes.split(","):
        response = requests.get(f"https://bestenliste.leichtathletik.de/Performances/GetEventsForClass?cls={classCode}&performanceList={performanceList}&env={environment}")
        print(response.text)
        json = response.json()

        events = []
        for event in json:
            events.append({
                "value": event["code"],
                "text": event["name"]
            })

        events_df = pd.DataFrame(events)
        events_df.to_csv(args.output, index=False)