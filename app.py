from flask import Flask, request, jsonify, url_for, render_template
from utils.deepai import generate_images_from_deepai
from moviepy.editor import *
from gtts import gTTS
import os
import random
import uuid

app = Flask(__name__)

IMG_DIR = "static/images/"
MUSIC_DIR = "static/bg_music/"
VOICE_DIR = "static/voices/"
VIDEO_DIR = "static/videos/"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_video', methods=['POST'])
def generate_video():
    data = request.get_json()
    prompt = data['prompt']
    lang = data['language']
    ratio = data['ratio']

    # Clear previous images
    for file in os.listdir(IMG_DIR):
        os.remove(os.path.join(IMG_DIR, file))

    # Step 1: Image generation
    selected_images = generate_images_from_deepai(prompt)

    # Step 2: Voice generation
    tts = gTTS(text=prompt, lang='hi' if lang == 'hindi' else 'en')
    voice_path = os.path.join(VOICE_DIR, f"{uuid.uuid4()}.mp3")
    tts.save(voice_path)

    # Step 3: Random background music
    bgms = [os.path.join(MUSIC_DIR, m) for m in os.listdir(MUSIC_DIR)]
    bgm_path = random.choice(bgms)

    # Step 4: Build video
    clips = []
    for img in selected_images:
        img_clip = ImageClip(img).set_duration(5)
        if ratio == '16:9':
            img_clip = img_clip.resize(height=720)
        elif ratio == '9:16':
            img_clip = img_clip.resize(height=1080).resize(width=608)
        elif ratio == '1:1':
            img_clip = img_clip.resize(height=720).resize(width=720)
        clips.append(img_clip)

    video = concatenate_videoclips(clips, method="compose")

    # Step 5: Combine audio
    voice_audio = AudioFileClip(voice_path)
    bgm_audio = AudioFileClip(bgm_path).volumex(0.2)
    final_audio = CompositeAudioClip([bgm_audio, voice_audio])
    final_video = video.set_audio(final_audio)

    # Step 6: Export
    filename = f"{uuid.uuid4()}.mp4"
    output_path = os.path.join(VIDEO_DIR, filename)
    final_video.write_videofile(output_path, fps=24)

    video_url = url_for('static', filename='videos/' + filename)
    return jsonify({'video_url': video_url})
