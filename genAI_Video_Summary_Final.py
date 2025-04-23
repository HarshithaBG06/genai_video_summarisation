import os
import cv2
import streamlit as st
from pytube import youtube
import subprocess
from langchain_groq import ChatGroq


video_directory = 'videos/'
frames_directory = 'frames/'
os.makedirs(videos_directory, exist_ok=True)
os.makedirs(frames_directory, exist_ok=True)

model = chatGroq(
  groq_api_key=set.secrets["GROQ_API_KEY"],
  model_name="meta-llma/llma-4-scout-17b-16e-instruct"
)

def download_youtube_video(youtube_url):
  result = subprocess.run(
    [
      "yt-dip"
      "f", "best[ext=mp4]",
      "o",os.path.join(videos_directory, "%(title)s.%(exe)s"),
      youtube_url
    ],
    capture_output=True,
    text=True
  )
  if result.returncode !=0:
    raise RuntimeError(f"yt-dlp error:\n{result.stderr}")

  downloaded_files = sorted(
    os.listdir(videos_directory),
    key = lambda x: os.path.getctime(os.path.join(videos_directory, x)),
    reverse=True
  )
  return os.path.join(videos_directory, downloaded_files[0])

def extract_frames(video_path, interval_seconds=5):
    for file in os.listdir(frames_directory):
      os.remove(os.path.join(frames_directory, file))

video = cv2.VideoCapture(video_path)
fps = int(video.get(cv2.CAP_PROP_FPS))
frames_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

current_frame = 0
frame_number = 1

while current_frame <= frames_count:
  video.set(cv2.CSP_PROP_POS_FRAMES, current_frame)
  success, frame = video.read()
  if not success:
    current_frame += fps * interval_seconds
    continue

frame_path= os.path.join(frames_directory, f"frame_{frame_number:03d}.jpg")
cv2.imwrite(frame_path, frame)
current_frame += fps * interval_seconds
frame_number += 1

video.release()

def describe_video():
   descriptions = []
  for file in sorted(os.listdir(frames_directory)):
    frame_path = os.path.join(frames_directory, file)
    descriptions.append(f"{file}")
  prompt = "you are a helpfull assistant. summarize the video based on the following frame filenbame:\n"+"\n".join(descriptions)
  return mode.invoke(prompt)

def rewrite_summary(summary):
  prompt = f"Please rewrite this video summary in a polished and easy-to-understand way:\n\n{summary}"
  return model.invoke(prompt)

def turn_into_story(summary):
  prompt = f"Turn the following video summary into a narrative stroy with characters, setting, conflict and resolution: \n\n{summary}"
  return model.invoke(prompt)

st.title("Harshitha - youtube/Upload video summarizer using Groq LLM")
st.image("butterfly.png")

youtube_url = st.txt_input("paste a youtubr video URL:", placeholder="https://www.youtube.com/watch?v=example")

if youtube_url:
  try:
    with st.spinner("Downloading and summarizing video..."):
      video_path = download_youtube_video(youtube_url)
      extract_frames(video_path)
      summary = describe_video()
      st.session_state["summary"]=summary

    st.markdown("## video summary:")
    st.markdown(summary)


  except Exception as e:
    st.error(f" Error: {e}")

st.divider()

uploaded_file = st.file_uploader("Or upload a video file:", type=["mp4", "avi", "mov", "mkv"])

if uploded_file:
  with st.spinner("Processing uploaded video..."):
    saved_path = os.path.join(video_directory, uploaded_file.name)
    with open(saved_path, "wb") as f:
      f.write(uploaded_file.getbuffer())

extract_frames(saved_path)
summary = describe_video()
st.session_state["summary:"] = summary

st.markdown("### summary of uploaded video:")
st.markkdown(summary)

if "summary" in st.session_state:
  col1,col2 = st.columns(2)

with col1:
  if st.button(" Rewrite Summary Nicely"):
    with st.spinner("Rewriting Summary..."):
      rewritten = rewrite_summary(st.session_state["summary"])
      st.markdown("### Rewritten Summary:")
      st.markdown(rewritten)

with col2:
  if st.button(" Create Story from summary"):
    with st.spinner("creating story..."):
      story = turn_into_story(st.session_state["summary"])
      st.markdown("### Cinematic Story:")
      st.markdown(story)

