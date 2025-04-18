import pandas as pd 
from typing import List, Tuple, Dict, Set, Optional, Union, Callable, Any

def last_touch(df: pd.DataFrame) -> pd.DataFrame:

    # Constrain the df to just converters & copy
    converters = df[df["approved"] == 1].copy()

    # ID last touch channel based on channel sequence
    converters["last_touch"] = converters["channel_seq"].apply(lambda x: x[-2])

    ft_pivot = pd.get_dummies(converters["last_touch"], prefix="last_touch").astype(int)

    output = pd.concat([converters["user_id"], ft_pivot], axis=1)
    return output