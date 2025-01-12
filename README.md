# video text


A python script to convert mp4 video to text using whisper,
and translate the text from source language("en" by default) to destination language("zh-cn" by default).


## usage

```bash
./video_to_text.py -h
usage: video_to_text.py [-h] --input INPUT [--outout OUTPUT] [--model MODEL] [--src SRC] [--dest DEST] [--format FORMAT]

Convert MP4 video to text using Whisper, and translate the text.

options:
  -h, --help            show this help message and exit
  --input INPUT, -i INPUT
                        path to the input mp4 file
  --outout OUTPUT, -o OUTPUT
                        path to the output text file, it is the same as the input file with extenstion ".srt" if not specified
  --model MODEL, -m MODEL
                        the model that whisper will use, it is "small" by default
  --src SRC, -s SRC     source language, it is "en" by default
  --dest DEST, -d DEST  target language, it is "zh-cn" by default
  --format FORMAT, -f FORMAT
                        output format, only support "txt" or "srt" format for now

```

for example

```bash
./video_to_text.py -i ./example/5_minutes_for_50_years.mp4
```


## tips

You can download any video from youtube or other site, and then use the script to make subtitles.

1. use https://cobalt.tools/ to download the video you want

2. trim the video
```
ffmpeg -i input.mp4 -ss 00:00:07 -c:v copy -c:a copy output_trimmed.mp4

```
3. convert the video resolution
```
ffmpeg -i output_trimmed.mp4 -vf scale=320:180 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k output_180p.mp4
```