import runpod
import requests
import os
import base64
from api import F5TTS
from scipy.io.wavfile import write


f5tts = F5TTS()

def handler(job):
    """Handler function to process jobs for voice cloning with F5TTS."""
    job_input = job['input']
    
    # Get inputs from job
    text_input = job_input.get("text_input", "")  # Multiline text input
    voice_url = job_input.get("voice_reference")
    transcript = job_input.get("transcript", None)
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
        
        
        # Clean up temporary files
        os.remove(temp_filename)
        os.remove(output_wave_file)
        os.remove("temp_out_spect.png")
        
        # Return response
        return {
            
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