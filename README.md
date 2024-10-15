- This is a quick experiment, if you change voices or other parameters you may need to fix some other parts of the script
- To Do: voices/personalities easy configuration
- To Do: robust structured output

# openPodcaster
Generate podcast scripts and audio using AI-powered dialogue generation and text-to-speech technology.

## Features

- Context-driven script generation
- Multi-presenter podcast format
- Text-to-speech audio synthesis
- Audio concatenation
- Modular design

## Quick Start

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up OpenAI API key: `export OPENAI_API_KEY="your_key_here"`
4. Install FFmpeg
5. Add context files to `context/` folder
6. Run: `python podcast_generator.py`

## Usage

Place `.txt` files with context in the `context/` folder, then run the script. Output will be in `audio_files/` with the final podcast as `combined_podcast.mp3`.

## Control

For complete control of the style, narrative and voices, edit the variable "instructions". 

By default, instructions is:

```python
instructions = f"write a script for a 2 presenters podcast. \
     One of the podcasters is called Alpha, the other is Beta. \
     Alpha is inquisitorial, makes questions and wants to know more.\
     Beta is patient and structured and offers a clear perspective. \
     Consider that the text generated will be used to generate speech,\
     avoid symbols or long lists. Focus on a more narrative style.\
     Here is the context: \
    <CONTEXT>\
            {context}\
    </CONTEXT>"
```
## Example

See the examples/ folder for audio_files, context and combined_audio example.

## Requirements

- OpenAI API key
- FFmpeg (https://www.ffmpeg.org/)



