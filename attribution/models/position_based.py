import pandas as pd 
from typing import List, Tuple, Dict, Set, Optional, Union, Callable, Any

def position(df: pd.DataFrame) -> pd.DataFrame:

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
        channel_col = f"u_shaped_{channel}"

        # Determine Weight based on channel indice in 'channels'
        converters[channel_col] = converters.apply(
            lambda row: (
                # First Channel
                (0.4 if channel == row["channels"][0] else 0) +
                # Last Channel
                (0.4 if channel == row["channels"][-1] else 0) +
                # Mid-Channels - based on freq, excluding first & last touchpoints
                (
                    (
                        0.2
                        if len(set(row["channels"])) == 1
                        else 0.1
                        if len(set(row["channels"])) == 2 and channel in row["channels"]
                        else 0.2
                        / (row["n_touchpoints"] - 2)
                        * row["channels"][1:-1].count(channel)
                        if len(set(row["channels"])) > 2
                        else 0
                    )
                )
                if channel in row["channels"]
                else 0
            ),
            axis=1,
        )

        output[channel_col] = converters[channel_col]

    return output