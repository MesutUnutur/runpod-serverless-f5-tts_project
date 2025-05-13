import runpod
import requests
import os
import base64
from api import F5TTS
from io import BytesIO
from scipy.io.wavfile import write
import uuid  # To generate unique names
import boto3
from video_generate_from_voice_and_jpg import wav_to_mp4_with_original_size
from dotenv import load_dotenv


load_dotenv()

f5tts = F5TTS()

def handler(job):
    """Handler function to process jobs for voice cloning with F5TTS."""
    job_input = job['input']
    
    # Get inputs from job
    text_input = job_input.get("text_input", "")  # Multiline text input
    voice_url = job_input.get("voice_reference")
    transcript = job_input.get("transcript", None)
    famous_jpg = job_input.get("famous_jpg", "elon_musk_image.jpg")
    seed = job_input.get("seed", -1)  # Use the seed from job input or default to -1 for random
    # Get additional settings
    remove_silence = job_input.get("remove_silence", False)  # Whether to remove silence
    speed = job_input.get("speed", 1.0)  # Speed multiplier for the speech

    # Get settings for output format and sampling rate
    output_format = job_input.get("output_format", "wav")
    sampling_rate = job_input.get("sampling_rate", 22050)
    #enable_base64_output = job_input.get("enable_base64_output", True)

    # Temporary filename for downloaded reference audio
    temp_filename = "temp_voice_ref.wav"
    output_wave_file = f"temp_out.{output_format}"
    try:
        # Download and save the reference audio
        response = requests.get(voice_url)
        with open(temp_filename, 'wb') as f:
            f.write(response.content)
        
        # Run the inference
        wav, sr, spect = f5tts.infer(
            ref_file=temp_filename,
            ref_text=transcript if transcript else "Default transcript",
            gen_text=text_input,
            file_wave=output_wave_file,
            file_spec="temp_out_spect.png",
            seed=seed,
            speed=speed,
            remove_silence=remove_silence
        )
        
        audio_output_path = output_wave_file

        R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
        R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
        R2_ENDPOINT_URL = os.getenv("R2_ENDPOINT_URL")
        R2_BUCKET_NAME = os.getenv("R2_BUCKET_NAME")
        
        # Function to upload file to R2
        def upload_to_r2(file_path, bucket_name, object_name):
            """ Uploads a file to Cloudflare R2 """
            s3_client = boto3.client(
                "s3",
                aws_access_key_id=R2_ACCESS_KEY_ID,
                aws_secret_access_key=R2_SECRET_ACCESS_KEY,
                endpoint_url=R2_ENDPOINT_URL,
            )

            if not os.path.exists(file_path):
                print(f"❌ ERROR: File {file_path} does not exist.")
                return False

            try:
                s3_client.upload_file(file_path, bucket_name, object_name)
                print(f"✅ Uploaded to R2: {bucket_name}/{object_name}")

            except Exception as e:
                print(f"❌ Upload failed: {e}")
                return False
        object_name_tts= f"output/F5tts/ttsF5_{uuid.uuid4().hex}.wav"


        upload_to_r2(audio_output_path, R2_BUCKET_NAME, object_name_tts)
        print("mp3 uploaded to R2 BUCKET")

        output_video = "video.mp4"
        wav_to_mp4_with_original_size(audio_output_path, famous_jpg, output_video)
        print("Video with audio created successfully!")

        object_name_video= f"output/F5tts/video_{uuid.uuid4().hex}.mp4"
        upload_to_r2(output_video, R2_BUCKET_NAME, object_name_video)
        print("Video uploaded to R2 BUCKET")

        # Clean up temporary files
        os.remove(temp_filename)
        os.remove(output_wave_file)
        os.remove("temp_out_spect.png")
        
        # Return response
        return {
            "object_name" : object_name_video,
            "audio_sampling_rate": sampling_rate,
            "output_format": output_format
        }
    
    except Exception as e:
        # Clean up in case of an error
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        if os.path.exists(output_wave_file):
            os.remove(output_wave_file)
        if os.path.exists("temp_out_spect.png"):
            os.remove("temp_out_spect.png")
        
        return {"error": str(e)}

runpod.serverless.start({"handler": handler})