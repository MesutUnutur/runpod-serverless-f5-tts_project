import os
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from PIL import Image

def wav_to_mp4_with_original_size( audio_path,image_path, output_path):

    try:
        # Fix Pillow compatibility: ensure LANCZOS resampling is used for resizing
        img = Image.open(image_path)
        img = img.resize((int(img.width * (1080 / img.height)), 1080), Image.Resampling.LANCZOS)
        
        # Define the custom directory where you want to save the image
        output_dir = '/workspace/F5-TTS/src/f5_tts/'  # Your desired directory
        os.makedirs(output_dir, exist_ok=True)  # Make sure the directory exists

        # Save resized image temporarily in the specified directory
        temp_image_path = os.path.join(output_dir, "resized_temp_image.jpg")
        img.save(temp_image_path)

        # Load audio
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration

        # Load resized image and set duration and audio
        image_clip = ImageClip(temp_image_path, duration=duration).set_audio(audio_clip)
        image_clip = image_clip.set_fps(24)

        # Write to video file
        image_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

        # Clean up temporary image
        os.remove(temp_image_path)

        print(f"✅ Video saved to: {output_path}")
    except Exception as e:
        print(f"Error encountered: {e}")