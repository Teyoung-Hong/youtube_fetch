#---------------------------- 
# Import 
#----------------------------
import pandas as pd #csv作成用
from apiclient.discovery import build #youtube api for python
from apiclient.errors import HttpError

#----------------------------
# Init 
#----------------------------
API_KEY = 'AIzaSyDFNxPd-OzQEskj8MQq3H6v0Y7RUiNRF0s' #GCP APIキー
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'
CHANNEL_ID = 'UCirJ47xW7QIwXIbCs5TESfQ' #ママ割チャンネルID
channels = [] #チャンネル情報を格納する配列
searches = [] #videoidを格納する配列
videos = [] #各動画情報を格納する配列
nextPagetoken = None
nextpagetoken = None


#----------------------------
# youtubeオブジェクトを変数に格納
#----------------------------
youtube = build(
  YOUTUBE_API_SERVICE_NAME,
  YOUTUBE_API_VERSION,
  developerKey=API_KEY
)

#----------------------------
# チャンネル情報取得
#----------------------------
# チャンネル情報取得
channel_response = youtube.channels().list(
    part = 'snippet,statistics',
    id = CHANNEL_ID
    ).execute()

# チャンネル情報を配列に格納
for channel_result in channel_response.get("items", []):
    if channel_result["kind"] == "youtube#channel":
        channels.append([
          channel_result["snippet"]["title"],
          channel_result["statistics"]["subscriberCount"],
          channel_result["statistics"]["viewCount"],
          channel_result["statistics"]["videoCount"],
          channel_result["snippet"]["publishedAt"]
        ])


#----------------------------
# チャンネル情報取得
#----------------------------
#nextpagetokenがnoneになるまで取得処理（max50件しか取得できないため）
while True:
  if nextPagetoken != None:
    nextpagetoken = nextPagetoken

  #videoIdを取得
  search_response = youtube.search().list(
    part = "snippet",
    channelId = CHANNEL_ID,
    maxResults = 50,
    order = "date", #日付順にソート
    pageToken = nextpagetoken #再帰的に指定
  ).execute()

  #全videoIdの配列に格納
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
      searches.append(search_result["id"]["videoId"])

  try:
    nextPagetoken =  search_response["nextPageToken"]
  except:
    break

#----------------------------
# 動画情報を取得
#----------------------------
for result in searches:
  video_response = youtube.videos().list(
    part = 'snippet,statistics',
    id = result
    ).execute()

  # 動画情報をdictに格納
  for video_result in video_response.get("items", []):
    if video_result["kind"] == "youtube#video":
      videos.append([
        video_result["snippet"]["title"],
        video_result["statistics"]["viewCount"],
        video_result["statistics"]["likeCount"],
        video_result["statistics"]["dislikeCount"],
        video_result["statistics"]["commentCount"],
        video_result["snippet"]["publishedAt"]
      ])

#----------------------------
# csvにデータ書き出し
#----------------------------
#動画情報
videos_report = pd.DataFrame(videos, columns=['title', 'viewCount', 'likeCount', 'dislikeCount', 'commentCount', 'publishedAt'])
videos_report.to_csv("videos_report.csv", index=None)
#チャンネル情報
channel_report = pd.DataFrame(channels, columns=['title', 'subscriberCount','viewCount', 'videoCount', 'publishedAt'])
channel_report.to_csv("channels_report.csv", index=None)



