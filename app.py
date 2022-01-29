#All players stats are provided by MoneyPuck.com

from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import pandas as pd
import streamlit as st

# Stat weight values
penalty_weight = 0.5
takeaway_weight = 2
dZone_Start_weight = 1
onIce_xgf_weight = 0.5
blocked_weight = 5
onIce_corsi_weight = 1

# Normalize column
def normalize_column ():
    return 0

# Calculate a percentage of penalties taken vs penalties drawn
def calc_penalty_percent (row):
    
    # divide by 0 protection
    if (row['penaltiesDrawn'] + row['penalties']) == 0:
        return 0.0
    
    return row['penaltiesDrawn'] / (row['penaltiesDrawn'] + row['penalties'])

# Calculate a percentage of takeaways vs giveaways (defensive zone giveaways are weighed heavier)
def calc_takeaway_percent (row):
    
    # divide by 0 protection
    if (row['I_F_takeaways'] + row['I_F_takeaways'] + row['I_F_dZoneGiveaways']) == 0:
        return 0.0
    
    return row['I_F_takeaways'] / (row['I_F_takeaways'] + row['I_F_giveaways'] + row['I_F_dZoneGiveaways'])

# Calculate the percentage of starts the player gets in the defensive zone, indicating trust from the coach
def calc_dZone_start_percent (row):
    
    return row['I_F_dZoneShiftStarts'] / (row['I_F_dZoneShiftStarts'] + row['I_F_oZoneShiftStarts'] + row['I_F_neutralZoneShiftStarts'])

# Calculate the expected goals for percentage when the player is on the ice
def calc_onIce_xgf_percent (row):
    
    return row['OnIce_F_xGoals'] / (row['OnIce_F_xGoals'] + row['OnIce_A_xGoals'])

# Calculate the percentage of shot attempts blocked by the player
def calc_blocked_percent (row):
    
    return row['shotsBlockedByPlayer'] / (row['shotsBlockedByPlayer'] + row['OnIce_A_shotAttempts'])

# Calculate an overall defensive score based on all the previous stats
def calc_defensive_score (row):
    
    return ((row['onIce_xgf_Percentage'] * onIce_xgf_weight) + (row['shotBlockedPercentage'] * blocked_weight) + (row['onIce_corsiPercentage'] * onIce_corsi_weight) + (row['penaltiesPercentage'] * penalty_weight) + (row['takeawayPercentage'] * takeaway_weight) + (row['dZone_Start_Percentage'] * dZone_Start_weight))

# Set page title and headers
st.set_page_config(page_title='NHL Player Stats',
                   page_icon="🏒")
st.header('Top NHL Players by Advanced Stats')
st.subheader('Defensive Skater Stats (Min. 200 Minutes Played)')
st.caption('Last updated: 01/28/2022, 18:38:18 EST')

# LOAD DATA
csv_file = 'skaters.csv'
cols_to_use = ['name','team','position','situation','icetime','OnIce_F_xGoals','OnIce_A_xGoals','OnIce_A_shotAttempts','onIce_corsiPercentage','penalties','penaltiesDrawn','I_F_hits','I_F_takeaways','I_F_giveaways','I_F_dZoneGiveaways','I_F_dZoneShiftStarts','I_F_oZoneShiftStarts','I_F_neutralZoneShiftStarts','shotsBlockedByPlayer']

df = pd.read_csv(csv_file,
                 usecols=cols_to_use)

# Only use rows containing stats from all situations
index_names = df[df['situation'] != 'all'].index
df.drop(index_names,
        inplace=True)

# Only use players that have played a minimum 200 minutes this season
index_names = df[df['icetime'] < 12000].index
df.drop(index_names,
        inplace=True)

# Drop the situation column
df.drop(columns='situation',
        inplace=True)

# Convert the icetime from seconds to minutes for better readability
df['icetime'] = (df['icetime'] / 60).astype(int)

# Convert necessary stats to integers for better readability
df = df.astype({'penalties':int,'penaltiesDrawn':int,'I_F_hits':int,'I_F_takeaways':int,'I_F_giveaways':int,'I_F_dZoneGiveaways':int,'I_F_dZoneShiftStarts':int,'I_F_oZoneShiftStarts':int,'I_F_neutralZoneShiftStarts':int,'shotsBlockedByPlayer':int,'OnIce_A_shotAttempts':int} )

# Create columns to normalize all the necessary data
df['penalties_normal'] = MinMaxScaler().fit_transform(np.array(df['penalties']).reshape(-1,1))
df['penalties_drawn_normal'] = MinMaxScaler().fit_transform(np.array(df['penaltiesDrawn']).reshape(-1,1))
df['takeaways_normal'] = MinMaxScaler().fit_transform(np.array(df['I_F_takeaways']).reshape(-1,1))
df['giveaways_normal'] = MinMaxScaler().fit_transform(np.array(df['I_F_giveaways']).reshape(-1,1))
df['dZone_giveaways_normal'] = MinMaxScaler().fit_transform(np.array(df['I_F_dZoneGiveaways']).reshape(-1,1))
df['dZone_starts_normal'] = MinMaxScaler().fit_transform(np.array(df['I_F_dZoneShiftStarts']).reshape(-1,1))
df['oZone_starts_normal'] = MinMaxScaler().fit_transform(np.array(df['I_F_oZoneShiftStarts']).reshape(-1,1))
df['nZone_starts_normal'] = MinMaxScaler().fit_transform(np.array(df['I_F_neutralZoneShiftStarts']).reshape(-1,1))
df['blocks_normal'] = MinMaxScaler().fit_transform(np.array(df['shotsBlockedByPlayer']).reshape(-1,1))
df['shots_against_normal'] = MinMaxScaler().fit_transform(np.array(df['OnIce_A_shotAttempts']).reshape(-1,1))



# Calculate each necessary stat and add it to the dataframe
df['penaltiesPercentage'] = df.apply(lambda row: calc_penalty_percent(row), axis=1)
df['takeawayPercentage'] = df.apply(lambda row: calc_takeaway_percent(row), axis=1)
df['dZone_Start_Percentage'] = df.apply(lambda row: calc_dZone_start_percent(row), axis=1)
df['onIce_xgf_Percentage'] = df.apply(lambda row: calc_onIce_xgf_percent(row), axis=1)
df['shotBlockedPercentage'] = df.apply(lambda row: calc_blocked_percent(row), axis=1)
df['defensive_score'] = df.apply(lambda row: calc_defensive_score(row), axis=1)



# Re-order and rename the columns in the dataframe
df = df[['name','team','position', 'defensive_score','icetime','onIce_corsiPercentage','penaltiesPercentage','penalties','penaltiesDrawn','takeawayPercentage','I_F_takeaways','I_F_giveaways','I_F_dZoneGiveaways','dZone_Start_Percentage','I_F_dZoneShiftStarts','I_F_oZoneShiftStarts','I_F_neutralZoneShiftStarts','onIce_xgf_Percentage','OnIce_F_xGoals','OnIce_A_xGoals','shotBlockedPercentage','OnIce_A_shotAttempts','shotsBlockedByPlayer','I_F_hits']]
df.rename(columns={'name':'Name','team':'Team','position':'Position', 'defensive_score':'Defensive Score','icetime':'Time on Ice (Minutes)','onIce_xGoalsPercentage':'Expected Goals %','onIce_corsiPercentage':'On Ice Corsi %','penaltiesPercentage':'Penalties %','penalties':'Penalties Taken','penaltiesDrawn':'Penalties Drawn','takeawayPercentage':'Takeaway %','I_F_takeaways':'Takeaways','I_F_giveaways':'Giveaways','I_F_dZoneGiveaways':'Defensive Zone Giveaways','dZone_Start_Percentage':'Defensive Zone Start %','I_F_dZoneShiftStarts':'Defensive Zone Starts','I_F_oZoneShiftStarts':'Offensive Zone Starts','I_F_neutralZoneShiftStarts':'Neutral Zone Starts','onIce_xgf_Percentage':'On Ice Expected Goals For %','OnIce_F_xGoals':'On Ice Expected Goals For','OnIce_A_xGoals':'On Ice Expected Goals Against','shotBlockedPercentage':'Shot Attempts Blocked %','OnIce_A_shotAttempts':'On Ice Shot Attempts Against','shotsBlockedByPlayer':'Shots Blocked','I_F_hits':'Hits'},
          inplace=True)

# Sort the dataframe by defensive score
df = df.sort_values(by=['Defensive Score'],
                    ascending=False)

# Reset the index of the dataframe
df = df.reset_index(drop=True)

# Change the dataframe to be indexed from 1 for better readability
df.index = np.arange(1,len(df)+1)

#Display the dataframe on the webapp
st.dataframe(df)

st.caption('Defensive score is calculated by using a combination of the player\'s on ice expected goals for %, shot attempts blocked %, on ice corsi %, % of penalties taken vs. drawn, % of takeaways vs. giveaways, and their defensive zone start %. These stats are entirely made up and just for fun. Please don\'t take anything on the page seriously. All stats are provided by MoneyPuck.com')

df_normalized = df.copy()
df_normalized['Takeaways Normalized'] = MinMaxScaler().fit_transform(np.array(df_normalized['Takeaways']).reshape(-1,1))

st.dataframe(df_normalized)