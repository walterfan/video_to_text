#!/usr/bin/env python3

import os
import ffmpeg
import whisper
import argparse
import asyncio
from googletrans import Translator

def format_time(seconds):
    millis = int((float(seconds) % 1) * 1000)
    seconds = int(float(seconds))
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"


def extract_file_info(file_path):
    folder_path, file_name_with_ext = os.path.split(file_path)
    file_name, file_extension = os.path.splitext(file_name_with_ext)
    return folder_path, file_name, file_extension

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

def transcribe_audio_with_segments(audio_file, model_name="base", pause_threshold=0.5):

    model = whisper.load_model(model_name)

    result = model.transcribe(audio_file, word_timestamps=True)
    
    segments = result["segments"]
    sn = 0
    paragraphs = []
    current_paragraph = []
    previous_end_time = 0.0
    paragraph_start_time = 0.0

    for segment in segments:
        start_time = segment["start"]
        end_time = segment["end"]
        text = segment["text"].strip()

        # the first paragraph
        if len(current_paragraph) == 0:
            paragraph_start_time = start_time

        # create new paragraph if time distance is greater than pause threshold
        if start_time - previous_end_time > pause_threshold:
            if current_paragraph:
                sn += 1
                merged_text = " ".join(current_paragraph)
                paragraphs.append(f"\n{sn}\n[{format_time(paragraph_start_time)} --> {format_time(end_time)}]\n{merged_text}")
                # start new paragraph
                current_paragraph = []
                paragraph_start_time = start_time
        
        current_paragraph.append(text)
        previous_end_time = end_time

    # the last paragraph
    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))
    
    return paragraphs


async def translate_text(text, src, dest):
    """Translate text from English to Chinese."""
    translator = Translator()
    translated = await translator.translate(text, src=src, dest=dest)
    return translated.text

def do_translate(text_file, text, src, dest):
    translated_text = asyncio.run(translate_text(text, src, dest))
    folder_path, file_name, file_extension = extract_file_info(text_file)
    with open(os.path.join(folder_path, file_name + "_" + dest + file_extension), "w", encoding="utf-8") as f:
        f.write(translated_text)
    print("-"*80)
    print(f"Transcribed Text:\n {translated_text}")

def do_asr(audio_file: str, text_file: str, model_name: str):
    print("Transcribing audio with Whisper...")
    #text = transcribe_audio_with_whisper(audio_file, model_name="base")  # Use "base", "small", or larger models as needed
    paragraphs = transcribe_audio_with_segments(audio_file, model_name=model_name, pause_threshold=1.5)
    text = "\n".join(paragraphs)
    with open(text_file, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"ASR Text:\n{text}")
    return text

def main(video_file: str, text_file: str, model_name: str , src: str, dest: str):
    file_path = video_file.rsplit(".", 1)[0]
    audio_file =  file_path + "_temp.wav"
    if not text_file:
        text_file = f"{file_path}_{src}.srt"

    print(f"1. Extracting audio {audio_file} from {video_file}...")
    extract_audio_from_video(video_file, audio_file)
    print(f"2. Recognizing text from audio {audio_file} to {text_file}...")
    text = do_asr(audio_file, text_file, model_name)
    print(f"3. Translate text file {text_file} from {src} to {dest}")
    do_translate(text_file, text, src, dest)

    # Clean up temporary files
    if os.path.exists(audio_file):
        os.remove(audio_file)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Convert MP4 video to text using Whisper, and translate the text.")
    parser.add_argument('--input','-i', required=True,  dest='input', help='path to the input mp4 file')
    parser.add_argument('--outout', '-o', dest='output', help='path to the output text file, it is the same as the input file with extenstion ".srt" if not specified')
    parser.add_argument('--model', '-m', dest='model', default="small", help='the model that whisper will use, it is "small" by default')
    parser.add_argument('--src', '-s', dest='src', default="en", help='source language, it is "en" by default')
    parser.add_argument('--dest', '-d', dest='dest', default="zh-cn", help='target language, it is "zh-cn" by default')
    parser.add_argument('--format', '-f', dest='format', default="srt", help='output format, only support "txt" or "srt" format for now')

    args = parser.parse_args()

    main(args.input, args.output, args.model, args.src, args.dest)