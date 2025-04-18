# Marketing-Attribution-Models

## Overview

This project provides a streamlined solution for calculating marketing conversion attribution across various models and heuristics. It's designed to take raw conversion data as input, transform it into a usable format, calculate attribution credit based on the specified models, and output the results in two convenient table structures. The modular design allows for easy integration of additional attribution models and the ability to call specific models as needed.

## Included Models and Heuristics

The following attribution models and heuristics are currently implemented:

* **Data-Driven Model:** Based on a first-order Markov chain to provide a more nuanced understanding of channel contributions.
* **First Touch:** Assigns 100% of the conversion credit to the first marketing touchpoint in the customer journey.
* **Last Touch:** Assigns 100% of the conversion credit to the last marketing touchpoint before the conversion.
* **Linear:** Distributes conversion credit equally across all marketing touchpoints in the customer journey.
* **Position-Based:** Assigns a specified percentage of credit to the first and last touchpoints, with the remaining credit distributed equally among the intermediary touchpoints.

## Target Output Formats

The functions within this project will generate two distinct dataframe outputs:

* **Wide Table:**
    * Each row represents a unique user.
    * Columns represent the combination of an attribution model and a specific channel (e.g., `first_touch_email`, `linear_social_media`).
    * Each cell contains the conversion credit (a value between 0 and 1) attributed to that specific channel by that model for that user.
    * This format is ideal for comparing the outputs of different attribution models at the user level and provides a clear overview of channel performance across models.

* **Long Table:**
    * Each row represents a unique combination of user, channel, and attribution model.
    * Columns include user identifier, channel, attribution model name, and the corresponding conversion credit (a value between 0 and 1).
    * This format is more suitable for aggregate analysis, filtering by model or channel, and integration with Business Intelligence (BI) tools for reporting and visualization.

## Key Features

* **Raw Data Ingestion:** Designed to handle conversion records (user_id | date | funnel stage sequence # | channel).
* **Data Transformation:** Includes necessary steps to transform the raw data into a structured format suitable for attribution calculations.
* **Modular Design:** Easily extendable to incorporate new attribution models and heuristics.
* **Flexible Model Calling:** Enables users to execute all implemented models or call specific models as needed.
* **Two Output Formats:** Provides both 'wide' and 'long' table formats to cater to different analytical needs.
* **BI Tool Integration:** The 'long' format is specifically designed for convenient integration with BI platforms.

## Getting Started

A simple demonstration script (get_attribution_weights.py) with sample data is located in the 'example' folder.
