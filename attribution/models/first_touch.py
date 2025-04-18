import pandas as pd 
from typing import List, Tuple, Dict, Set, Optional, Union, Callable, Any

def first_touch(df: pd.DataFrame) -> pd.DataFrame:

    # Constrain the df to just converters & copy
    converters = df[df["approved"] == 1].copy()

    # ID first touch channel based on channel sequence
    converters["first_touch"] = converters["channel_seq"].apply(lambda x: x[1])

    ft_pivot = pd.get_dummies(converters["first_touch"], prefix="first_touch").astype(
        int
    )

    output = pd.concat([converters["user_id"], ft_pivot], axis=1)
    return output