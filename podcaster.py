import os
import shutil
import json
import subprocess
import re
from pathlib import Path
from openai import OpenAI
from pydub import AudioSegment

# Constants
CONTEXT_FOLDER = "context/"
OUTPUT_DIR = Path(__file__).parent / "audio_files"
FFMPEG_PATH = "/opt/homebrew/bin/ffmpeg"
FFPROBE_PATH = "/opt/homebrew/bin/ffprobe"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Make sure your API key is in environment variables

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# --- 1. Read Context Files ---
def read_context_files(folder_path: str = CONTEXT_FOLDER) -> str:
    """
    Reads all text files in the specified folder and combines them into a single context string.
    """
    context = ""

    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"The folder '{folder_path}' does not exist.")
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".txt"):
            file_path = os.path.join(folder_path, filename)
            with open(file_path, 'r') as file:
                content = file.read()
            context += f"### {filename}\n{content}\n\n"
    
    return context

# --- 2. Generate Podcast Script ---
def generate_podcast_script(context: str) -> dict:
    """
    Generates a podcast script using OpenAI's chat completion with the provided context.
    """
    instructions = (
        "Write a script for a 2-presenter podcast. One podcaster is Alpha, inquisitive and curious. "
        "The other is Beta, patient and structured. The generated text will be used for speech synthesis, "
        "so avoid symbols or long lists and focus on a narrative style. Here is the context: \n"
        f"{context}"
    )

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format="json",
        messages=[
            {"role": "system", "content": "You are a helpful podcast-style script generator.\
            The answer should be a json object with the structure {'1':{'alpha':'bla bla bla'}, '2':{'beta':'bla bla'}, ... } \
            each turn one dictionary with one podcaster"},
            {"role": "user", "content": instructions}
        ]
    )

    return json.loads(response.choices[0].message.content)

# --- 3. Generate Audio Files ---
def generate_audio_files(script_dict: dict, output_dir: Path = OUTPUT_DIR) -> None:
    """
    Converts the generated script into audio files using a text-to-speech model.
    """
    # Clean the audio output directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(exist_ok=True)

    voice_mapping = {"alpha": "nova", "beta": "onyx"}

    for key, value in script_dict.items():
        speaker, content = list(value.items())[0]
        voice = voice_mapping.get(speaker, "alloy")  # Default voice

        speech_file_path = output_dir / f"{key}.mp3"

        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=content
            )
            response.stream_to_file(speech_file_path)
            print(f"Created audio file for {speaker}: {speech_file_path}")
        except Exception as e:
            print(f"Error creating audio for {speaker}: {e}")

# --- 4. Concatenate Audio Files ---
def natural_sort_key(s: str):
    """
    Helper function to sort files numerically.
    """
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]

def concatenate_audio_files(folder_name: str, output_file: str) -> None:
    """
    Combines multiple audio files in a folder into a single output file using FFmpeg.
    """
    folder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), folder_name)
    audio_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.mp3')], key=natural_sort_key)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), output_file)

    # Prepare the FFmpeg command to concatenate files
    command = [FFMPEG_PATH, "-y"]
    for audio_file in audio_files:
        command.extend(["-i", os.path.join(folder_path, audio_file)])
    command.extend(["-filter_complex", f"concat=n={len(audio_files)}:v=0:a=1", "-c:a", "libmp3lame", output_path])

    try:
        subprocess.run(command, check=True, stderr=subprocess.PIPE)
        print(f"Combined audio saved to: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred during audio concatenation: {e}")
        print(f"FFmpeg error output: {e.stderr.decode()}")

# --- Main Execution Flow ---
if __name__ == "__main__":
    try:
        # Step 1: Read context files
        context = read_context_files()
        print("Context read successfully!")
        
        # Step 2: Generate podcast script
        script_dict = generate_podcast_script(context)
        
        # Step 3: Generate audio files
        generate_audio_files(script_dict)
        
        # Step 4: Combine audio files into a single output
        concatenate_audio_files(folder_name="audio_files", output_file="combined_podcast.mp3")
        print("Podcast audio generation complete.")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
