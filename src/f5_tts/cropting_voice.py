from pydub import AudioSegment

# === File paths ===
input_mp3 = "elonmusk-101soundboards.mp3"
output_mp3 = "elonmusk_short_voice_for_inference.mp3"

# === Start and end times (in seconds, decimal allowed) ===
start_time = 0         # Start at 0.0 seconds
end_time = 11.4       # End at 10.8 seconds

# === Load MP3 ===
audio = AudioSegment.from_mp3(input_mp3)

# === Convert to ms and crop ===
start_ms = int(start_time * 1000)
end_ms = int(end_time * 1000)
cropped_audio = audio[start_ms:end_ms]

# === Export to new MP3 ===
cropped_audio.export(output_mp3, format="mp3")

print(f"✅ Cropped MP3 created accurately: {output_mp3}")
