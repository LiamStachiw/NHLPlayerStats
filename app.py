import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
from PIL import Image

st.set_page_config(page_title='NHL Player Stats')
st.header('Top NHL Players by Advanced Stats')
st.subheader('Defensive Skater Stats')

# LOAD DATA
csv_file = 'skaters.csv'
sheet_name = 'DATA'
cols_to_use = ['name','team','position','situation','games_played','icetime','onIce_xGoalsPercentage','onIce_corsiPercentage','penalties','penaltiesDrawn','penalityMinutes','penalityMinutesDrawn','I_F_hits','I_F_takeaways','I_F_giveaways','I_F_dZoneGiveaways','I_F_dZoneShiftStarts','I_F_oZoneShiftStarts','shotsBlockedByPlayer']

#cols = pd.read_csv(csv_file,
#                   nrows=1).columns

df = pd.read_csv(csv_file,
                 usecols=cols_to_use)

index_names = df[df['situation'] != 'all'].index

df.drop(index_names,
        inplace=True)

index_names = df[df['icetime'] < 12000].index

df.drop(index_names,
        inplace=True)

df.drop(columns='situation',
        inplace=True)

df = df.reset_index(drop=True)

df.index = np.arange(1,len(df)+1)

df['icetime'] = (df['icetime'] / 60).astype(int)
df['onIce_xGoalsPercentage'] = df['onIce_xGoalsPercentage'].astype(float).map("{:.0%}".format)
df['onIce_corsiPercentage'] = df['onIce_corsiPercentage'].astype(float).map("{:.0%}".format)
df = df.astype({'penalties':int,'penaltiesDrawn':int,'penalityMinutes':int,'penalityMinutesDrawn':int,'I_F_hits':int,'I_F_takeaways':int,'I_F_giveaways':int,'I_F_dZoneGiveaways':int,'I_F_dZoneShiftStarts':int,'I_F_oZoneShiftStarts':int,'shotsBlockedByPlayer':int} )


st.dataframe(df)
