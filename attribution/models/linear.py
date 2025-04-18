import pandas as pd 
from typing import List, Tuple, Dict, Set, Optional, Union, Callable, Any

def linear(df: pd.DataFrame) -> pd.DataFrame:

    # Constrain the df to just converters & copy
    converters = df[df["approved"] == 1].copy()

    # ID all channels based on channel sequence
    converters["channels"] = converters["channel_seq"].apply(lambda x: x[1:-1])

    # Extract Unique Channels
    channels = set(
        channel for channels in converters["channels"] for channel in channels
    )

    output = pd.DataFrame({"user_id": converters["user_id"]})

    for channel in channels:
        channel_col = f"linear_{channel}"

        # Calculate how many times each channel appears in each user's journey
        converters[channel_col] = converters.apply(
            lambda row: row["channels"].count(channel) / row["n_touchpoints"], axis=1
        )

        output[channel_col] = converters[channel_col]

    return output