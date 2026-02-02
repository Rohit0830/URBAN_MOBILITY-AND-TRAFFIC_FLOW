"""End-to-end cleaning pipeline for US_Accidents_March23.csv

Writes a cleaned CSV to dataset/cleand-data/US_Accidents_March23_cleaned.csv

Usage:
    from tools.accidents_pipeline import main
    main()

Defaults:
- chunksize = 500_000
- impute_weather = True (fills weather numeric fields using city medians)
- fill_end_with_start = False
"""
from pathlib import Path
import pandas as pd
import numpy as np
import sys
import csv
from collections import defaultdict

# Configuration
SRC = Path('dataset') / 'US_Accidents_March23.csv'
OUT_DIR = Path('dataset') / 'cleand-data'
OUT_FILE = OUT_DIR / 'US_Accidents_March23_cleaned.csv'
CHUNKSIZE = 500_000
WEATHER_COLS = ['Temperature(F)','Wind_Chill(F)','Humidity(%)','Pressure(in)','Visibility(mi)','Wind_Speed(mph)','Precipitation(in)']
BOOL_COLS = ['Amenity','Bump','Crossing','Give_Way','Junction','No_Exit','Railway','Roundabout','Station','Stop','Traffic_Calming','Traffic_Signal','Turning_Loop']
NUMERIC_COLS = WEATHER_COLS + ['Distance(mi)']
DATE_COLS = ['Start_Time','End_Time','Weather_Timestamp']


def _to_bool_series(s: pd.Series) -> pd.Series:
    return s.fillna('').astype(str).str.strip().str.lower().isin({'true','1','t','yes'})


def _validate_latlng(s: pd.Series, minv: float, maxv: float) -> pd.Series:
    s = pd.to_numeric(s, errors='coerce')
    s[(s < minv) | (s > maxv)] = np.nan
    return s


def clean_accidents_df(df: pd.DataFrame, fill_end_with_start: bool = False, drop_missing_start_coords: bool = False) -> pd.DataFrame:
    df = df.copy()

    if 'ID' in df.columns:
        df['ID'] = df['ID'].astype(str)

    for c in DATE_COLS:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors='coerce')

    for c in NUMERIC_COLS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    for c in BOOL_COLS:
        if c in df.columns:
            df[c] = _to_bool_series(df[c])

    if 'Zipcode' in df.columns:
        df['Zipcode'] = df['Zipcode'].astype(str).str.extract(r'(\d{5})')[0]

    if 'Start_Lat' in df.columns:
        df['Start_Lat'] = _validate_latlng(df['Start_Lat'], -90.0, 90.0)
    if 'Start_Lng' in df.columns:
        df['Start_Lng'] = _validate_latlng(df['Start_Lng'], -180.0, 180.0)
    if 'End_Lat' in df.columns:
        df['End_Lat'] = _validate_latlng(df['End_Lat'], -90.0, 90.0)
    if 'End_Lng' in df.columns:
        df['End_Lng'] = _validate_latlng(df['End_Lng'], -180.0, 180.0)

    df['has_end_coords'] = (df.get('End_Lat').notna() & df.get('End_Lng').notna()) if 'End_Lat' in df.columns and 'End_Lng' in df.columns else False

    if fill_end_with_start and 'Start_Lat' in df.columns and 'Start_Lng' in df.columns and 'End_Lat' in df.columns and 'End_Lng' in df.columns:
        missing_end = df['has_end_coords'] == False
        df.loc[missing_end, 'End_Lat'] = df.loc[missing_end, 'Start_Lat']
        df.loc[missing_end, 'End_Lng'] = df.loc[missing_end, 'Start_Lng']
        df['has_end_coords'] = (df.get('End_Lat').notna() & df.get('End_Lng').notna())

    if drop_missing_start_coords:
        if 'Start_Lat' in df.columns and 'Start_Lng' in df.columns:
            before = len(df)
            df = df.dropna(subset=['Start_Lat','Start_Lng'])
            print(f'Dropped {before - len(df)} rows with missing start coordinates')

    if 'Start_Time' in df.columns:
        df['start_hour'] = df['Start_Time'].dt.hour
        df['start_date'] = df['Start_Time'].dt.date

    return df


def compute_city_medians(src: Path, chunksize: int = CHUNKSIZE, weather_cols=None):
    """Compute per-city medians for weather numeric columns."""
    if weather_cols is None:
        weather_cols = WEATHER_COLS
    city_vals = defaultdict(lambda: defaultdict(list))
    overall_vals = defaultdict(list)
    total = 0
    for chunk in pd.read_csv(src, usecols=['City'] + weather_cols, chunksize=chunksize, low_memory=False):
        total += len(chunk)
        # coerce numerics
        for c in weather_cols:
            if c in chunk.columns:
                chunk[c] = pd.to_numeric(chunk[c], errors='coerce')
        # accumulate
        # iterate rows safely (column names may contain special characters)
    for _, row in chunk.iterrows():
        city = row['City'] if 'City' in chunk.columns else None
        for c in weather_cols:
            if c in chunk.columns:
                val = row[c]
                if pd.notna(val):
                    if city:
                        city_vals[city][c].append(val)
                    overall_vals[c].append(val)
    # compute medians
    city_medians = {}
    for city, colvals in city_vals.items():
        city_medians[city] = {c: (np.median(vals) if len(vals) else np.nan) for c, vals in colvals.items()}
    overall_medians = {c: (np.median(vals) if len(vals) else np.nan) for c, vals in overall_vals.items()}
    print(f'Computed medians from {total} rows: overall medians sample: { {k: overall_medians[k] for k in list(overall_medians)[:3]} }')
    return city_medians, overall_medians


def run_pipeline(src: Path = SRC, out_file: Path = OUT_FILE, chunksize: int = CHUNKSIZE, impute_weather: bool = True, fill_end_with_start: bool = False):
    out_file.parent.mkdir(parents=True, exist_ok=True)
    # Prepare medians if requested
    city_medians, overall_medians = ({}, {})
    if impute_weather:
        print('Computing city-level medians for weather columns (this may take a while)...')
        city_medians, overall_medians = compute_city_medians(src, chunksize=chunksize)
    # Process chunks
    first_write = True
    processed = 0
    for chunk in pd.read_csv(src, chunksize=chunksize, low_memory=False):
        cleaned = clean_accidents_df(chunk, fill_end_with_start=fill_end_with_start, drop_missing_start_coords=False)
        # impute
        if impute_weather:
            # ensure start_date exists
            if 'start_date' not in cleaned.columns and 'Start_Time' in cleaned.columns:
                cleaned['start_date'] = pd.to_datetime(cleaned['Start_Time'], errors='coerce').dt.date
            # fill per-city medians where available else overall
            for c in WEATHER_COLS:
                if c in cleaned.columns:
                    def _fill_val(row):
                        if pd.notna(row[c]):
                            return row[c]
                        city = row.get('City')
                        if city in city_medians and c in city_medians[city] and not pd.isna(city_medians[city][c]):
                            return city_medians[city][c]
                        return overall_medians.get(c, np.nan)
                    cleaned[c] = cleaned.apply(_fill_val, axis=1)
        # write to CSV
        if first_write:
            cleaned.to_csv(out_file, index=False, mode='w', quoting=csv.QUOTE_MINIMAL)
            first_write = False
        else:
            cleaned.to_csv(out_file, index=False, header=False, mode='a', quoting=csv.QUOTE_MINIMAL)
        processed += len(cleaned)
        print(f'Processed {processed} rows...')
    print('Pipeline complete. Output written to', out_file)


def main():
    run_pipeline()


if __name__ == '__main__':
    main()
