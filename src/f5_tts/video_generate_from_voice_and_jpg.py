import ffmpeg

def wav_to_mp4_with_original_size(wav_file, image_file, output_mp4):
    # Get the audio duration
    probe = ffmpeg.probe(wav_file)
    duration = float(probe['format']['duration'])  # Extract actual duration of audio

    # Load inputs
    audio = ffmpeg.input(wav_file)
    image = ffmpeg.input(image_file, loop=1, framerate=1, t=duration)  # Loop image for exact duration

    # Preserve original image size instead of forcing a resolution
    # Create output (Video with Audio)
    (
        ffmpeg
        .output(
            image, audio,  # Pass both video and audio
            output_mp4,
            vcodec="libx264",
            acodec="aac",
            audio_bitrate="192k",
            format="mp4",
            shortest=None,  # Ensures video ends with the audio
            pix_fmt="yuv420p"
        )
        .run(overwrite_output=True)  # Overwrite if exists
    )
