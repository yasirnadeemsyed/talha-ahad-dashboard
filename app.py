import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import plotly.express as px
import datetime

# -------------------------
# CONFIG
# -------------------------
API_KEY = "AIzaSyCu7L5TCarOs9RNhu3nNzK9Gz3f6O1bxV8"
CHANNEL_ID = "UCuiyZZRtnpqU0r3gR5t8PoA"
youtube = build('youtube', 'v3', developerKey=API_KEY)

# -------------------------
# FUNCTIONS
# -------------------------
def get_channel_stats(channel_id):
    request = youtube.channels().list(
        part='snippet,contentDetails,statistics',
        id=channel_id
    )
    response = request.execute()
    data = response['items'][0]
    stats = {
        'Title': data['snippet']['title'],
        'Subscribers': int(data['statistics']['subscriberCount']),
        'Views': int(data['statistics']['viewCount']),
        'Videos': int(data['statistics']['videoCount'])
    }
    return stats, data['contentDetails']['relatedPlaylists']['uploads']

def get_video_data(playlist_id, max_results=10):
    videos = []
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=max_results
    )
    response = request.execute()
    for item in response['items']:
        video_id = item['snippet']['resourceId']['videoId']
        title = item['snippet']['title']
        published = item['snippet']['publishedAt']
        video_stats = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()['items'][0]['statistics']
        videos.append({
            'Title': title,
            'Views': int(video_stats.get('viewCount', 0)),
            'Likes': int(video_stats.get('likeCount', 0)),
            'Comments': int(video_stats.get('commentCount', 0)),
            'Published': published
        })
    return pd.DataFrame(videos)

# -------------------------
# UI START
# -------------------------
st.set_page_config(page_title="YouTube Analytics Dashboard", layout="wide")
st.title("📊 Talha Ahad Podcast - YouTube Analytics Dashboard")

# Fetch Data
stats, uploads_playlist = get_channel_stats(CHANNEL_ID)
df = get_video_data(uploads_playlist)

# Show Channel Stats
col1, col2, col3 = st.columns(3)
col1.metric("Subscribers", f"{stats['Subscribers']:,}")
col2.metric("Total Views", f"{stats['Views']:,}")
col3.metric("Total Videos", stats['Videos'])

st.write("### Latest Videos")
st.dataframe(df)

# Chart
fig = px.bar(df, x='Title', y='Views', title="Recent Videos by Views", text='Views')
fig.update_traces(texttemplate='%{text}', textposition='outside')
st.plotly_chart(fig, use_container_width=True)

# Timestamp
st.caption(f"Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
