import numpy as np
import pandas as pd 
from typing import List, Tuple, Dict, Set, Optional, Union, Callable, Any

# Generate an array of channels, based on user touchpoints
def transition_array(path):

    state_transitions = []
    initial_state = path[0]

    for state in path[1:]:
        state_transitions.append([initial_state, state])
        initial_state = state

    return state_transitions


# Apply transition_array function to transformed user data
def make_transition_arrays(df: pd.DataFrame) -> pd.DataFrame:

    # Copy df & constrain to relevant columns
    temp_df = df.loc[:, ["user_id", "channel_seq"]]
    # Apply transition_array function
    temp_df["transitions_array"] = temp_df["channel_seq"].apply(transition_array)

    return temp_df


# Derive transition state probabilities from transitions_array & applies removal when relevant
def get_transition_probs(df: pd.DataFrame, removal=None) -> pd.DataFrame:

    temp_df = make_transition_arrays(df)
    # Explode transition array -> unique transition per row
    temp_df = temp_df.explode("transitions_array")
    # Convert to Tuples for value counts
    temp_df["transition_tuple"] = temp_df["transitions_array"].apply(tuple)
    # Aggregate pair counts
    trans_pair_counts = pd.DataFrame(
        temp_df["transition_tuple"].value_counts()
    ).reset_index()
    # Break out start & end states
    trans_pair_counts["state_start"] = trans_pair_counts["transition_tuple"].apply(
        lambda x: str(x[0])
    )
    trans_pair_counts["state_end"] = trans_pair_counts["transition_tuple"].apply(
        lambda x: str(x[1])
    )
    # Remove circular state transitions
    trans_pair_counts = trans_pair_counts[
        trans_pair_counts["state_start"] != trans_pair_counts["state_end"]
    ]

    # Removal Effect
    trans_summary = trans_pair_counts.copy()

    if removal is not None:
        removal = removal.lower().strip()
        start_states = set(trans_summary['state_start'])
        if removal in start_states:
            trans_summary["state_end"] = trans_summary["state_end"].mask(trans_summary["state_end"] == removal, "null")
            trans_summary = trans_summary[trans_summary["state_start"] != removal]
        else:
            raise ValueError("Error - Ineligible Removal State: {}".format(removal))

    # Summarize start state totals for prob % calc
    state_start_counts = (
        trans_summary.groupby("state_start").agg(total=("count", "sum")).reset_index()
    )

    # Prob % calc
    trans_summary = pd.merge(
        trans_summary, state_start_counts, on="state_start", how="left"
    )
    trans_summary["transition_prob"] = trans_summary["count"] / trans_summary["total"]

    output = trans_summary[["state_start", "state_end", "transition_prob"]]

    return output


# Transition Matrix
def get_transition_matrix(df: pd.DataFrame, removal=None) -> pd.DataFrame:

    # Generate transition probabilities
    temp_df = get_transition_probs(df, removal)
    # Pivot – Indexed by start state, pivoting end state
    output = pd.pivot_table(
        temp_df,
        index="state_start",
        columns="state_end",
        values="transition_prob",
        fill_value=0,
    ).reset_index()

    # Add rows for conversion and null if they don't exist
    if "conversion" not in output["state_start"].values:
        # Create a row for conversion with 1.0 probability of staying in conversion
        conversion_row = pd.DataFrame(
            {
                "state_start": ["conversion"],
                **{
                    col: [0.0]
                    for col in output.columns
                    if col != "state_start" and col != "conversion"
                },
                "conversion": [1.0],
            }
        )
        output = pd.concat([output, conversion_row])

    if "null" not in output["state_start"].values:
        # Create a row for null with 1.0 probability of staying in null
        null_row = pd.DataFrame(
            {
                "state_start": ["null"],
                **{
                    col: [0.0]
                    for col in output.columns
                    if col != "state_start" and col != "null"
                },
                "null": [1.0],
            }
        )
        output = pd.concat([output, null_row])

    if "start" not in output.columns:
        output["start"] = 0.0

    column_order = output["state_start"].tolist()
    column_order.insert(0, "state_start")  # Keep 'state_start' as the first column

    # Reorder the columns
    output = output[column_order]

    return output


# Formatted Transition Probabilities for Conversion Probability Calculations with removal channel designation
def transition_probs_input(df: pd.DataFrame, removal=None) -> pd.DataFrame:

    # Generate transition probabilities
    temp_df = get_transition_matrix(df, removal)
    # states
    states = temp_df["state_start"]
    # Next states array
    next_states = temp_df.columns[1:].to_numpy()
    # Next state probabilities array
    next_state_probs = (
        temp_df.iloc[:, 1:].apply(lambda row: row.values, axis=1).to_numpy()
    )
    matrix = np.vstack(next_state_probs)

    return (states, next_states, matrix)


# Conversion Probabilities
def get_conversion_probs(df: pd.DataFrame, removal=None) -> pd.DataFrame:

    states, next_states, P = transition_probs_input(df, removal)

    state_indices = {state: idx for idx, state in enumerate(states)}

    conversion_idx = state_indices["conversion"]

    # Get indices of transient states (all except conversion and null)
    transient_states = [s for s in states if s.lower() not in ["conversion", "null"]]
    transient_indices = [state_indices[s] for s in transient_states]

    # Extract Q (transitions between transient states)
    Q = P[np.ix_(transient_indices, transient_indices)]

    # Extract R (transitions from transient to conversion state)
    R = P[np.ix_(transient_indices, [conversion_idx])]

    # Calculate fundamental matrix N = (I-Q)^(-1)
    I = np.eye(len(transient_indices))
    N = np.linalg.inv(I - Q)

    # Calculate absorption probabilities B = N·R
    B = np.dot(N, R)

    # Create result dictionary
    conversion_probs = {}
    for i, state in enumerate(transient_states):
        conversion_probs[state] = float(B[i, 0])  # Convert to float for cleaner output

    # Add 1.0 for conversion state and 0.0 for null state
    conversion_probs["conversion"] = 1.0
    if "null" in state_indices:
        conversion_probs["null"] = 0.0

    return conversion_probs


# Calculate removal effects for each Channel – return dict
def removal_effects(df: pd.DataFrame)-> Dict:

    removal_effects = {}

    conv_probs_base = get_conversion_probs(df)

    channels = list(conv_probs_base.keys())

    for channel in [c for c in channels if c not in ["start", "conversion", "null"]]:

        rm_conv_probs = get_conversion_probs(df, removal=channel)

        removal_effects[channel] = conv_probs_base["start"] - rm_conv_probs["start"]

    total_effect = sum(removal_effects.values())
    normalized_effects = {
        channel: effect / total_effect for channel, effect in removal_effects.items()
    }

    return normalized_effects


def markov(df):

    # Constrain the df to just converters & copy
    converters = df[df["approved"] == 1].copy()

    rme = removal_effects(df)

    channels = list(rme.keys())

    output = pd.DataFrame({"user_id": converters["user_id"]})

    for channel in channels:
        channel_col = f"markov_{channel}"

        converters[channel_col] = rme.get(channel)

        output[channel_col] = converters[channel_col]

    return output
