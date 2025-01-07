#!/usr/bin/env python3

import os
import ffmpeg
import whisper
import argparse
import asyncio
from googletrans import Translator

def extract_audio_from_video(mp4_file, audio_file):
    """Extract audio from an MP4 file and save as WAV."""
    ffmpeg.input(mp4_file).output(audio_file).run()
    return audio_file

def transcribe_audio_with_whisper(audio_file, model_name="base"):
    """Transcribe audio to text using Whisper."""
    # Load Whisper model
    model = whisper.load_model(model_name)

    # Transcribe audio
    result = model.transcribe(audio_file)
    return result["text"]

def transcribe_audio_with_segments(audio_file, model_name="base", pause_threshold=1.0):

    model = whisper.load_model(model_name)
    
    result = model.transcribe(audio_file, word_timestamps=True)
    
    segments = result["segments"]
    
    paragraphs = []
    current_paragraph = []
    previous_end_time = 0.0
    
    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()
        
        # create new paragraph if time distance is greater than pause threshold
        if start_time - previous_end_time > pause_threshold:
            if current_paragraph:
                paragraphs.append(" ".join(current_paragraph))
                current_paragraph = []
        
        current_paragraph.append(text)
        previous_end_time = end_time
    
    # the last paragraph
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
    
    return paragraphs


async def translate_text(text, src="en", dest="zh-cn"):
    """Translate text from English to Chinese."""
    translator = Translator()
    translated = await translator.translate(text, src=src, dest=dest)
    return translated.text

def do_translate(text_file, text):
    translated_text = asyncio.run(translate_text(text))
    with open(text_file.rsplit(".", 1)[0] + "_cn.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("-"*80)
    print("Transcribed Text:")
    print(translated_text)

def do_asr(text_file, audio_file):
    print("Transcribing audio with Whisper...")
    text = transcribe_audio_with_whisper(audio_file, model_name="base")  # Use "base", "small", or larger models as needed

    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text)
    print("ASR Text:")
    print(text)
    return text

def main(mp4_file, text_file):
    audio_file = mp4_file.rsplit(".", 1)[0] + ".wav"

    print(f"Extracting audio {audio_file} from {mp4_file}...")
    extract_audio_from_video(mp4_file, audio_file)

    text = do_asr(text_file, audio_file)

    do_translate(text_file, text)

    # Clean up temporary files
    if os.path.exists(audio_file):
        os.remove(audio_file)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert MP4 video to text using Whisper, and translate the text.")
    parser.add_argument("input", type=str, help="Path to the input mp4 file")
    parser.add_argument("output", type=str, help="Path to the output text file")
    args = parser.parse_args()

    main(args.input, args.output)
