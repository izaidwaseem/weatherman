import argparse
import pandas as pd
import os
from glob import glob
from colorama import Fore, Style, init


# intialize colorama
init()


def load_weather_data(file):
    try:
        df = pd.read_csv(file)
        df.fillna(0, inplace=True)  # Fill NaN values with 0
        return df
    except pd.errors.ParserError as e:
        print(f"Error parsing {file}: {e}")
        return pd.DataFrame()


def get_date_column(df):
    for column in ['PKT', 'PKST', 'GST']:
        if column in df.columns:
            return column
    return None


def filter_by_year_and_month(df, year, month=None):
    date_column = get_date_column(df)
    if not date_column:
        print("No known date column found.")
        return pd.DataFrame()
    
    # Filter out rows with invalid date format
    df = df[df[date_column].str.match(r'\d{4}-\d{1,2}-\d{1,2}')]

    # Convert to datetime
    df['Date'] = pd.to_datetime(df[date_column], errors='coerce')

    # Filter by year
    df = df[df['Date'].dt.year == year]

    # If month is specified, filter by month as well
    if month is not None:
        df = df[df['Date'].dt.month == month]

    return df


def plot_temperature_bars(df):
    if df.empty:
        print("No data available for the specified month.")
        return

    print(f"{df['Date'].dt.month_name()[0]} {df['Date'].dt.year.iloc[0]}")

    for _, row in df.iterrows():
        date = row['Date'].strftime("%d")
        high_temp = row['Max TemperatureC']
        low_temp = row['Min TemperatureC']
        
        # Prepare bars
        high_bar = '+' * int(high_temp)
        low_bar = '+' * int(low_temp)
        
        # Print both temperatures on the same line
        print(f"{date} {Fore.BLUE}{low_bar} {low_temp}C {Style.RESET_ALL}- {Fore.RED}{high_bar} {high_temp}C{Style.RESET_ALL}")


def calculate_averages(df):
    if df.empty:
        return None, None, None
    
    avg_highest_temp = df['Max TemperatureC'].mean()
    avg_lowest_temp = df['Min TemperatureC'].mean()
    avg_humidity = df['Max Humidity'].mean()
    
    return avg_highest_temp, avg_lowest_temp, avg_humidity


def find_extremes(df):
    if df.empty:
        return None, None, None, None, None, None
    
    highest_temp = df['Max TemperatureC'].max()
    lowest_temp = df['Min TemperatureC'].min()
    most_humid = df['Max Humidity'].max()

    highest_temp_day = df[df['Max TemperatureC'] == highest_temp]['Date'].values[0]
    lowest_temp_day = df[df['Min TemperatureC'] == lowest_temp]['Date'].values[0]
    most_humid_day = df[df['Max Humidity'] == most_humid]['Date'].values[0]

    return highest_temp, highest_temp_day, lowest_temp, lowest_temp_day, most_humid, most_humid_day


def process_weather_files(year, month, folder_path, year_wise=False, chart=False):   
    txt_files = glob(os.path.join(folder_path, "*.txt"))
    
    all_data = []
    all_highest_temps = []
    all_lowest_temps = []
    all_humidities = []

    highest_temp = -float('inf')
    lowest_temp = float('inf')
    most_humid = -float('inf')

    highest_temp_day = ""
    lowest_temp_day = ""
    most_humid_day = ""

    for file in txt_files:
        df = load_weather_data(file)
        if df.empty:
            continue
        
        # Filter data by year and month
        df_filtered = filter_by_year_and_month(df, year, month)
        
        # Collect data for charting
        if chart:
            all_data.append(df_filtered)
        
        # Process extremes or averages depending on flags
        if year_wise:  # Year-wise report for extremes
            current_highest, current_highest_day, current_lowest, current_lowest_day, current_most_humid, current_most_humid_day = find_extremes(df_filtered)
            
            if current_highest is not None and current_highest > highest_temp:
                highest_temp = current_highest
                highest_temp_day = current_highest_day

            if current_lowest is not None and current_lowest < lowest_temp:
                lowest_temp = current_lowest
                lowest_temp_day = current_lowest_day

            if current_most_humid is not None and current_most_humid > most_humid:
                most_humid = current_most_humid
                most_humid_day = current_most_humid_day
        elif month:  # Month-wise report for averages
            avg_highest_temp, avg_lowest_temp, avg_humidity = calculate_averages(df_filtered)
            
            if avg_highest_temp is not None:
                all_highest_temps.append(avg_highest_temp)
            if avg_lowest_temp is not None:
                all_lowest_temps.append(avg_lowest_temp)
            if avg_humidity is not None:
                all_humidities.append(avg_humidity)

    # Handle year-wise extremes reporting
    if year_wise:
        if highest_temp != -float('inf'):
            print(f"Highest: {highest_temp}C on {highest_temp_day}")
        else:
            print(f"No data for highest temperature in {year}")
        
        if lowest_temp != float('inf'):
            print(f"Lowest: {lowest_temp}C on {lowest_temp_day}")
        else:
            print(f"No data for lowest temperature in {year}")
        
        if most_humid != -float('inf'):
            print(f"Humid: {most_humid}% on {most_humid_day}")
        else:
            print(f"No data for humidity in {year}")

    # Handle month-wise averages reporting
    if month:
        if all_highest_temps and all_lowest_temps and all_humidities:
            overall_avg_highest_temp = sum(all_highest_temps) / len(all_highest_temps)
            overall_avg_lowest_temp = sum(all_lowest_temps) / len(all_lowest_temps)
            overall_avg_humidity = sum(all_humidities) / len(all_humidities)

            print(f"Highest Average: {overall_avg_highest_temp:.1f}C")
            print(f"Lowest Average: {overall_avg_lowest_temp:.1f}C")
            print(f"Average Humidity: {overall_avg_humidity:.1f}%")
        else:
            print(f"No data available for {year}-{month}")

    # Handle chart generation
    if chart and all_data:
        combined_df = pd.concat(all_data)
        plot_temperature_bars(combined_df)
    elif chart:
        print(f"No data available for {year}-{month}")


def main():
    parser = argparse.ArgumentParser(description='Weather report')
    parser.add_argument("-e", "--year", type=int, required=True, help="Year of report")
    parser.add_argument("-m", "--month", type=int, help="Month of report (optional, for monthly reports)")
    parser.add_argument("-y", "--year-wise", action="store_true", help="Generate a year-wise report")
    parser.add_argument("-c", "--chart", action="store_true", help="Generate bar charts for a given month")
    parser.add_argument("path", type=str, help="Path to the folder containing weather files")

    args = parser.parse_args()

    year = args.year
    month = args.month
    folder_path = args.path
    year_wise = args.year_wise
    chart = args.chart

    process_weather_files(year, month, folder_path, year_wise, chart)


if __name__ == "__main__":
    main()
