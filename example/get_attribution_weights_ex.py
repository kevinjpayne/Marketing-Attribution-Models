import pandas as pd 
import numpy as np 
from attribution.main import get_conversion_attribution_weights

df = pd.read_csv('example/attribution_model_sample.csv')

output_wide, output_long = get_conversion_attribution_weights(df)

print(f"Wide table head: \n {output_wide.head()}")
print(f"Long table head: \n {output_long.head()}")
