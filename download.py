import pandas as pd 
import os
import sqlite3
import concurrent.futures
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download performances for multiple events")
    parser.add_argument("--performanceList", help="Performance list id", required=True)
    parser.add_argument("--year", help="Year", required=True, type=int)
    parser.add_argument("--tmp", help="Temporary folder", default="tmp")
    parser.add_argument("--input", help="Input file")
    parser.add_argument("--output", help="Output file", required=True)
    args = parser.parse_args()
    year = args.year
    performanceList = args.performanceList
    watcher = pd.read_csv(args.input)
    tmp_folder = args.tmp

    def process_row(row):
        eventcode = row['eventcode']
        classcode = row['classcode']
        environment = row['environment']
        technical = row['technical']
        file = f"{tmp_folder}/{eventcode}_{classcode}_{year}_{environment}.csv"
        os.system(f"python main.py --classcode {classcode} --eventcode {eventcode} --year 2024 --performanceList {performanceList} --environment {environment} --technical {technical} --output {file}")

    # Using ThreadPoolExecutor to process rows in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(process_row, row) for _, row in watcher.iterrows()]

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing row: {e}")

    all_files = os.listdir(tmp_folder)
    df_from_each_file = []
    for f in all_files:
        try:
            df = pd.read_csv(f"{tmp_folder}/{f}")
            df_from_each_file.append(df)
        except:
            continue

    concatenated_df = pd.concat(df_from_each_file, ignore_index=True)
    concatenated_df.drop(columns=['position', 'ageGroup', 'classcode'], inplace=True, errors='ignore')
    concatenated_df.drop_duplicates(subset=['name', 'birthyear', 'eventcode', 'performance'], keep='first', inplace=True)

    if args.output.endswith(".csv"):
        concatenated_df.to_csv(args.output, index=False)
    elif args.output.endswith(".db"):
        conn = sqlite3.connect("watcher.db")
        concatenated_df.to_sql("watcher", conn, if_exists="replace", index=False)
        conn.close()

    