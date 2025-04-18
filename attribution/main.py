import numpy as np
import pandas as pd 
from typing import List, Tuple, Dict, Set, Optional, Union, Callable, Any
from .data_processing import data_transform 
from .models.first_touch import first_touch
from .models.last_touch import last_touch
from .models.linear import linear
from .models.position_based import position 
from .models.markov import markov

def get_conversion_attribution_weights(df: pd.DataFrame) -> pd.DataFrame: 

    user_summary = data_transform(df)

    #Models 
    m_first_touch = first_touch(user_summary)
    m_last_touch = last_touch(user_summary)
    m_linear = linear(user_summary)
    m_position = position(user_summary)
    m_markov = markov(user_summary)

    #Wide 
    merged_df = m_first_touch
    df_list = [m_first_touch, m_last_touch, m_linear, m_position, m_markov]

    for df in df_list[1:]:
        output_wide = pd.merge(merged_df, df, on='user_id', how='left')

    #Long
    melted = pd.melt(
    output_wide,
    id_vars=output_wide.columns[0],
    value_vars=output_wide.columns[1:],
    var_name="channel_model",
    value_name="conversion_credit"
    )

    melted["channel"] = melted["channel_model"].str.split("_").str[-1]
    melted["model"] = melted.apply(lambda row: row["channel_model"].replace("_" + row["channel"], "", 1), axis=1)
    
    output_long = melted.drop("channel_model", axis=1)
    
    return(output_wide, output_long)



