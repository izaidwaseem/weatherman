import argparse
import pandas as pd
import os
from glob import glob


def process_weather_files(year, folder_path):   
    txt_files = glob(os.path.join(folder_path, "*.txt"))

    highest_temp = -float('inf')
    lowest_temp = float('inf')
    most_humid = -float('inf')

    highest_temp_day = ""
    lowest_temp_day = ""
    most_humid_day = ""

    for file in txt_files:
        try:
            df = pd.read_csv(file)
            # df.dropna(inplace=True)
            df.fillna(0, inplace=True)
        except pd.errors.ParserError as e:
            print(f"Error parsing {file}: {e}")
            continue

        # Handle the different date formats and column names
        if 'PKT' in df.columns:
            date_column = 'PKT'
        elif 'PKST' in df.columns:
            date_column = 'PKST'
        elif 'GST' in df.columns:
            date_column = 'GST'
        else:
            print(f"No known date column found in {file}")
            continue

        # Filter out rows with invalid date format
        df = df[df[date_column].str.match(r'\d{4}-\d{1,2}-\d{1,2}')]

        # Convert to datetime
        df['Date'] = pd.to_datetime(df[date_column], errors='coerce')

        # Filter by year
        df = df[df['Date'].dt.year == year]

        # Update highest, lowest, and most humid days
        max_temp = df['Max TemperatureC'].max()
        min_temp = df['Min TemperatureC'].min()
        max_humidity = df['Max Humidity'].max()

        if max_temp > highest_temp:
            highest_temp = max_temp
            highest_temp_day = df[df['Max TemperatureC'] == max_temp]['Date'].values[0]

        if min_temp < lowest_temp:
            lowest_temp = min_temp
            lowest_temp_day = df[df['Min TemperatureC'] == min_temp]['Date'].values[0]

        if max_humidity > most_humid:
            most_humid = max_humidity
            most_humid_day = df[df['Max Humidity'] == max_humidity]['Date'].values[0]

    print(f"Highest temperature of {highest_temp}C on {highest_temp_day}")
    print(f"Lowest temperature of {lowest_temp}C on {lowest_temp_day}")
    print(f"Most humid day with {most_humid}% humidity on {most_humid_day}")


def main():
    parser = argparse.ArgumentParser(description='Weather report')
    parser.add_argument("-e", "--year", type=int, required=True, help="Year of report")
    parser.add_argument("path", type=str, help="Path to the folder containing weather files")

    args = parser.parse_args()

    year = args.year
    folder_path = args.path

    process_weather_files(year, folder_path)


if __name__ == "__main__":
    main()
