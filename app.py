#All players stats are provided by MoneyPuck.com

from datetime import datetime
from urllib.request import Request, urlopen
import numpy as np
import pandas as pd
import streamlit as st
import datetime
import pytz
import os

# Stat weight values
penalty_weight = 0.25
takeaway_weight = 1
dZone_Start_weight = 0.25
onIce_xgf_weight = 1
blocked_weight = 1
onIce_corsi_weight = 1
hits_weight = 0.25
faceoffs_weight = 1

# Calculate the player's faceoff percentage
def calc_faceoff_percent (row):
    
    # divide by 0 protection
    if(row['faceoffsWon'] + row['faceoffsLost']) == 0:
        return 0.0
    
    return row['faceoffsWon'] / (row['faceoffsWon'] + row['faceoffsLost'])

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
    
    # divide by 0 protection 
    if (row['I_F_dZoneShiftStarts'] + row['I_F_oZoneShiftStarts'] + row['I_F_neutralZoneShiftStarts']) == 0:
        return 0.0
    
    return row['I_F_dZoneShiftStarts'] / (row['I_F_dZoneShiftStarts'] + row['I_F_oZoneShiftStarts'] + row['I_F_neutralZoneShiftStarts'])

# Calculate the expected goals for percentage when the player is on the ice
def calc_onIce_xgf_percent (row):
    
    return row['OnIce_F_xGoals'] / (row['OnIce_F_xGoals'] + row['OnIce_A_xGoals'])

# Calculate the percentage of shot attempts blocked by the player
def calc_blocked_percent (row):
    
    # Skewed data protection
    if row['OnIce_A_shotAttempts'] == 0:
        row['OnIce_A_shotAttempts'] = 0.01
    
    return row['shotsBlockedByPlayer'] / (row['shotsBlockedByPlayer'] + row['OnIce_A_shotAttempts'])

# Calculate the percentage of hits as a factor of total ice time
def calc_hit_percent (row):
    return row['I_F_hits'] / row['icetime']

# Calculate an overall defensive score based on all the previous stats
def calc_defensive_score (row):
    
    if(faceoffs):
        if(row['faceoffsWon'] + row['faceoffsLost']) < 25:
            faceoff_factor = 0
            stat_count = 7
        else:
            faceoff_factor = 1
            stat_count = 8
    else:
        faceoff_factor = 0
        stat_count = 7
    
    return (((row['onIce_xgf_Percentage'] * onIce_xgf_weight) + (row['shotBlockedPercentage'] * blocked_weight) + (row['onIce_corsiPercentage'] * onIce_corsi_weight) + (row['penaltiesPercentage'] * penalty_weight) + (row['takeawayPercentage'] * takeaway_weight) + (row['dZone_Start_Percentage'] * dZone_Start_weight) + (row['hitsPercentage'] * hits_weight) + ((row['faceoffPercentage'] * faceoffs_weight) * faceoff_factor)) / stat_count) * 10

# Get an up-to-date version of the player stats
def update_stats ():
    
    current_time = datetime.datetime.now(tz=pytz.timezone("UTC"))
    file_time = datetime.datetime.fromtimestamp(os.path.getctime('stats/{}.csv'.format(season.replace('/', ''))), tz=pytz.timezone("UTC")) if os.path.exists('stats/{}.csv'.format(season.replace('/', ''))) else datetime.datetime(2022, 1, 1, 1, 1, tzinfo=pytz.timezone("UTC"))
    diff_hours = (current_time - file_time).total_seconds() / 3600.0
    
    if(diff_hours >= 0.0):
        
        if os.path.exists('stats/{}.csv'.format(season.replace('/', ''))):
            os.remove('stats/{}.csv'.format(season.replace('/', '')))
        else:
            print("The file does not exist.")
        
        req = Request('https://www.moneypuck.com/moneypuck/playerData/seasonSummary/{}/regular/skaters.csv'.format(season[0:4]),
                      headers={'User-Agent': 'Mozilla/5.0'})
        with urlopen(req) as response, open('stats/{}.csv'.format(season.replace('/', '')), 'xb') as out_file:
            data = response.read() # a `bytes` object
            out_file.write(data)

# Set page title, headers, and controls
st.set_page_config(page_title='NHL Player Stats',
                   page_icon="🏒")

st.header('Top NHL Players by Advanced Stats')

st.subheader('Defensive Skater Stats')

season = st.selectbox('Season:', 
                      ('2022/2023', '2021/2022', '2020/2021', '2019/2020', '2018/2019', '2017/2018', '2016/2017'),
                      0,
                      help='Select the season from which the player\'s stats should be displayed.')

st.caption('Season stats last updated: ' + datetime.datetime.fromtimestamp(os.path.getctime('stats/{}.csv'.format(season.replace('/', ''))),
            tz=pytz.timezone("UTC")).strftime("%Y-%m-%d, %H:%M") + " UTC") 

st.button('Update Stats', 
          help='Get the most recent version of the player stats. (Stats will update only once every 24 hours.) This button will be diabled upon completion of the regular season.',
          on_click=update_stats, disabled=True)

faceoffs = st.checkbox('Use Faceoff Percentage?',
                       help='Should faceoff percentage be used to calculate defensive score? Only players with at least 25 faceoffs taken will have their faceoff percentage considered. This WILL add a noticable bias towards forwards playing the Center position.')

defense_only = st.checkbox('Only Show Defensemen?',
                           help='Should only defensemen be represented on the chart?')

minutes = st.slider('Minimum Icetime (minutes):',
                    1,
                    1000,
                    300,
                    help='Select the minimum ice time in minutes for a player to be represented on the chart. Please note that stats may become more misleading the lower the threshold is.')

# LOAD DATA
csv_file = 'stats/{}.csv'.format(season.replace('/', ''))
cols_to_use = ['name','team','position','situation','icetime','OnIce_F_xGoals','OnIce_A_xGoals','OnIce_A_shotAttempts','onIce_corsiPercentage','penalties','penaltiesDrawn','I_F_hits','I_F_takeaways','I_F_giveaways','I_F_dZoneGiveaways','I_F_dZoneShiftStarts','I_F_oZoneShiftStarts','I_F_neutralZoneShiftStarts','shotsBlockedByPlayer', 'faceoffsWon', 'faceoffsLost']

df = pd.read_csv(csv_file,
                 usecols=cols_to_use)

# Only display defensemen if the option is selected
if (defense_only):
    index_names = df[df['position'] != 'D'].index
    df.drop(index_names,
        inplace=True)

# Only use rows containing stats from all situations
index_names = df[df['situation'] != 'all'].index
df.drop(index_names,
        inplace=True)

# Only use players that have played a minimum 300 minutes this season
index_names = df[df['icetime'] < (minutes * 60)].index
df.drop(index_names,
        inplace=True)

# Drop the situation column
df.drop(columns='situation',
        inplace=True)

# Convert the icetime from seconds to minutes for better readability
df['icetime'] = (df['icetime'] / 60).astype(int)

# Convert necessary stats to integers for better readability
df = df.astype({'faceoffsWon':int,'faceoffsLost':int,'penalties':int,'penaltiesDrawn':int,'I_F_hits':int,'I_F_takeaways':int,'I_F_giveaways':int,'I_F_dZoneGiveaways':int,'I_F_dZoneShiftStarts':int,'I_F_oZoneShiftStarts':int,'I_F_neutralZoneShiftStarts':int,'shotsBlockedByPlayer':int,'OnIce_A_shotAttempts':int} )


# Calculate each necessary stat and add it to the dataframe
df['faceoffPercentage'] = df.apply(lambda row: calc_faceoff_percent(row), axis=1)
df['penaltiesPercentage'] = df.apply(lambda row: calc_penalty_percent(row), axis=1)
df['takeawayPercentage'] = df.apply(lambda row: calc_takeaway_percent(row), axis=1)
df['dZone_Start_Percentage'] = df.apply(lambda row: calc_dZone_start_percent(row), axis=1)
df['onIce_xgf_Percentage'] = df.apply(lambda row: calc_onIce_xgf_percent(row), axis=1)
df['shotBlockedPercentage'] = df.apply(lambda row: calc_blocked_percent(row), axis=1)
df['hitsPercentage'] = df.apply(lambda row: calc_hit_percent(row), axis=1)
df['defensive_score'] = df.apply(lambda row: calc_defensive_score(row), axis=1)



# Re-order and rename the columns in the dataframe
df = df[['name','team','position', 'defensive_score','icetime','onIce_corsiPercentage','faceoffPercentage','faceoffsWon','faceoffsLost','penaltiesPercentage','penalties','penaltiesDrawn','takeawayPercentage','I_F_takeaways','I_F_giveaways','I_F_dZoneGiveaways','dZone_Start_Percentage','I_F_dZoneShiftStarts','I_F_oZoneShiftStarts','I_F_neutralZoneShiftStarts','onIce_xgf_Percentage','OnIce_F_xGoals','OnIce_A_xGoals','shotBlockedPercentage','OnIce_A_shotAttempts','shotsBlockedByPlayer','hitsPercentage', 'I_F_hits']]
df.rename(columns={'name':'Name','team':'Team','position':'Position', 'defensive_score':'Defensive Score','icetime':'Time on Ice (Minutes)','onIce_xGoalsPercentage':'Expected Goals %','onIce_corsiPercentage':'On Ice Corsi %','faceoffPercentage':'Faceoff Percentage','faceoffsWon':'Faceoffs Won','faceoffsLost':'Faceoffs Lost','penaltiesPercentage':'Penalties %','penalties':'Penalties Taken','penaltiesDrawn':'Penalties Drawn','takeawayPercentage':'Takeaway %','I_F_takeaways':'Takeaways','I_F_giveaways':'Giveaways','I_F_dZoneGiveaways':'Defensive Zone Giveaways','dZone_Start_Percentage':'Defensive Zone Start %','I_F_dZoneShiftStarts':'Defensive Zone Starts','I_F_oZoneShiftStarts':'Offensive Zone Starts','I_F_neutralZoneShiftStarts':'Neutral Zone Starts','onIce_xgf_Percentage':'On Ice Expected Goals For %','OnIce_F_xGoals':'On Ice Expected Goals For','OnIce_A_xGoals':'On Ice Expected Goals Against','shotBlockedPercentage':'Shot Attempts Blocked %','OnIce_A_shotAttempts':'On Ice Shot Attempts Against','shotsBlockedByPlayer':'Shots Blocked','hitsPercentage':'Hits Percentage','I_F_hits':'Hits'},
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

st.caption('Defensive score is calculated by using a combination of the player\'s on ice expected goals for %, shot attempts blocked %, on ice corsi %, % of penalties taken vs. drawn, % of takeaways vs. giveaways, defensive zone start %, a small factor of total hits as a factor of icetime, and their faceoff percentage (if they\'ve taken more than 25 faceoffs on the season). The defensive score stat entirely made up and just for fun. Please don\'t take anything on the page too seriously. All stats are provided by MoneyPuck.com')
