import streamlit as st
from huggingface_hub import InferenceClient
from moviepy import ImageClip, VideoFileClip, AudioFileClip
from pydub import AudioSegment
# import os
import requests
# from dotenv import load_dotenv

# Load environment variables
# load_dotenv()
hf_token = ""  # os.getenv("HF_TOKEN")

# Function to generate image
def generate_image(prompt, token):
    client = InferenceClient("stabilityai/stable-diffusion-3.5-large", token=token)
    image = client.text_to_image(prompt)
    image_path = "generated_image.png"
    image.save(image_path)
    return image_path

# Function to generate audio
def generate_audio(prompt, token):
    API_URL = "https://api-inference.huggingface.co/models/facebook/musicgen-small"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
    response.raise_for_status()
    
    # Save audio in FLAC format
    temp_file = "temp.flac"
    with open(temp_file, "wb") as audio_file:
        audio_file.write(response.content)
    
    # Convert to MP3
    output_mp3_file = "generated_audio.mp3"
    audio = AudioSegment.from_file(temp_file, format="flac")
    audio.export(output_mp3_file, format="mp3")
    return output_mp3_file

#  .flac --> convertable form -> exort mp3


# Function to create a video
def create_video(image_path, audio_path):
    video_path = "generated_video.mp4"  # image - > video
    output_file = "final_video.mp4"   # video + audio -> final
    
    # Create a video from the image
    image_clip = ImageClip(image_path).with_duration(10)
    image_clip.write_videofile(video_path, fps=24, codec="libx264", audio=False)
    
    # Combine video with audio
    video_clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(audio_path)
    video_with_audio = video_clip.with_audio(audio_clip)
    video_with_audio.write_videofile(output_file, codec="libx264", audio_codec="aac")
    return output_file

# Streamlit app
st.title("AI-Generated Video Content Creator")
st.write("Generate a video with an AI-generated image and audio based on your input!")

# Input fields
hf_token_input = st.text_input("Enter your Hugging Face API token", value=hf_token if hf_token else "", type="password")
prompt_input = st.text_area("Enter a description for your image and audio (e.g., 'Nature with relaxing music')")

# Generate button
if st.button("Generate"):
    if not hf_token_input or not prompt_input:
        st.error("Please provide both a Hugging Face token and a description.")
    else:
        try:
            image_prompt = f"Generate an art related to {prompt_input}."
            audio_prompt = f"Create relaxing low music that matches the theme of {prompt_input}."
            # Generate image
            st.write("Generating image...")
            image_path = generate_image(image_prompt, hf_token_input)
            st.image(image_path, caption="Generated Image")

            # Generate audio
            st.write("Generating audio...")
            audio_path = generate_audio(audio_prompt, hf_token_input)

            # Create final video
            st.write("Combining image and audio into a video...")
            final_video_path = create_video(image_path, audio_path)

            # Display the final video
            st.video(final_video_path)
        except Exception as e:
            st.error(f"An error occurred: {e}")
