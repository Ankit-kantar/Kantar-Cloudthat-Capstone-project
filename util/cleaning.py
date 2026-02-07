import pandas as pd
import re


def load_raw_data(
    listings_path: str,
    demographics_path: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load raw listings and demographics data.
    """
    listings = pd.read_csv(listings_path)
    demographics = pd.read_csv(demographics_path)
    return listings, demographics


def clean_postal_code(series: pd.Series) -> pd.Series:
    """
    Standardize postal/ZIP codes to 5-digit strings.
    """
    series = series.astype(str)
    series = series.str.extract(r'(\d{5})')
    return series


def clean_listings_data(listings: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare listings data.
    """
    df = listings.copy()

    # Clean ZIP code
    df["zip_code"] = clean_postal_code(df["postal_code"])

    # Ensure numeric fields
    df["listing_price"] = pd.to_numeric(df["listing_price"], errors="coerce")
    df["sq_ft"] = pd.to_numeric(df["sq_ft"], errors="coerce")
    df["bedrooms"] = pd.to_numeric(df["bedrooms"], errors="coerce")

    # Create price per sq ft
    df["price_per_sqft"] = df["listing_price"] / df["sq_ft"]

    return df


def clean_demographics_data(demographics: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and prepare demographics data.
    """
    df = demographics.copy()

    # Standardize ZIP code
    df["zip_code"] = clean_postal_code(df["zip_code"])

    # Ensure numeric fields
    df["median_income"] = pd.to_numeric(df["median_income"], errors="coerce")
    df["school_rating"] = pd.to_numeric(df["school_rating"], errors="coerce")
    df["crime_index"] = pd.to_numeric(df["crime_index"], errors="coerce")

    return df


def merge_datasets(
    listings: pd.DataFrame,
    demographics: pd.DataFrame
) -> pd.DataFrame:
    """
    Merge cleaned listings and demographics into a single dataset.
    """
    merged_df = listings.merge(
        demographics,
        on="zip_code",
        how="left"
    )
    return merged_df


def prepare_final_dataset(
    listings_path: str,
    demographics_path: str,
    output_path: str = "final_property_data.csv"
) -> pd.DataFrame:
    """
    Full pipeline:
    load → clean → merge → export final dataset
    """
    listings, demographics = load_raw_data(
        listings_path, demographics_path
    )

    listings_clean = clean_listings_data(listings)
    demographics_clean = clean_demographics_data(demographics)

    final_df = merge_datasets(
        listings_clean, demographics_clean
    )

    # Drop rows missing core business metrics
    final_df = final_df.dropna(
        subset=["listing_price", "sq_ft", "median_income"]
    )

    final_df.to_csv(output_path, index=False)

    return final_df
