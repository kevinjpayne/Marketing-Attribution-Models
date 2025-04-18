import pandas as pd 
from typing import List, Tuple, Dict, Set, Optional, Union, Callable, Any


def data_transform(df: pd.DataFrame) -> pd.DataFrame:
    # Validate required columns
    required_columns = ["user_id", "date", "conv_seq_num", "channel"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Required column '{col}' not found in DataFrame")

    # Convert date column to datetime
    df["date"] = pd.to_datetime(df["date"])

    # Create a temporary copy of the DataFrame for the channel arrays
    temp_df = df.copy()

    # Initial aggregations
    user_summary_df = (
        df.groupby("user_id")
        .agg(
            date_start=("date", "min"),
            date_end=("date", "max"),
            approved=("conv_seq_num", lambda x: 1 if x.max() == 4 else 0),
            max_conv_seq=("conv_seq_num", "max"),
            n_touchpoints=("date", "size"),
            n_channels=("channel", "nunique"),
        )
        .reset_index()
    )

    # Days in funnel
    user_summary_df["days_in_funnel"] = (
        user_summary_df["date_end"] - user_summary_df["date_start"]
    ).dt.days + 1

    # Channel Sequence
    # Calculate conversion result (a user has converted if they reached sequence 4)
    user_summary_df["conv_result"] = user_summary_df["max_conv_seq"].apply(
        lambda x: "conversion" if x == 4 else "null"
    )
    # Generate Channel Arrays
    temp_df = temp_df.sort_values(["user_id", "conv_seq_num"])
    channel_arrays = (
        temp_df.groupby("user_id")
        .apply(lambda x: x.sort_values("conv_seq_num")["channel"].tolist())
        .reset_index(name="temp_channels")
    )

    # Merge the channel arrays into the main summary DataFrame
    user_summary_df = user_summary_df.merge(channel_arrays, on="user_id", how="left")

    # Create the final channel array with 'start' at the beginning and conversion result at the end
    user_summary_df["channel_seq"] = user_summary_df.apply(
        lambda row: ["start"]
        + (row["temp_channels"] if isinstance(row["temp_channels"], list) else [])
        + [row["conv_result"]],
        axis=1,
    )

    # Drop the temporary channels & conv result columns
    user_summary_df.drop(["temp_channels", "conv_result"], axis=1, inplace=True)

    return user_summary_df