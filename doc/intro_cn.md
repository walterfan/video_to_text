
| **Abstract**  | AI 把字幕组的活都干了  |
| --------------|------------------------|
| **Authors**   | [Walter Fan](https://www.fanyamin.com)       |
| **Category**  | learning note  |
| **Status**    | v1.0          |
| **Updated**   | 2025-01-12     |
| **License**   | [CC-BY-NC-ND 4.0](http://creativecommons.org/licenses/by-nc-nd/4.0)|


- [详细步骤](#详细步骤)
  - [**第一步**：将mp4文件的语音提取为 wave 文件](#第一步将mp4文件的语音提取为-wave-文件)
  - [**第二步**：调用 whisper 识别语音为文本。](#第二步调用-whisper-识别语音为文本)
  - [**第三步**：调用Google Translate把文本翻译成中文。](#第三步调用google-translate把文本翻译成中文)
  - [**第四步**：将文本转换为字幕文件srt格式。](#第四步将文本转换为字幕文件srt格式)
  - [**第五步**：播放原本的mp4文件，并载入生成的字幕文件。](#第五步播放原本的mp4文件并载入生成的字幕文件)
- [具体用法](#具体用法)
  - [前提条件](#前提条件)
  - [使用方法](#使用方法)
  - [小技巧](#小技巧)


最近我在看一个外国同事录的 Demo 视频呀，那里面有两句他说得那叫一个快，我听了好几遍都没听清楚。这可咋办呢？
我灵机一动，想着自己写个脚本吧，把语音转换成文本，然后再把文本从英文翻译成中文，这样不就清楚啦。

说干就干，有了 AI 的加持, 没花多长时间就写好了一段小程序，你别说，效果还不错。
后来我一琢磨，哎呀，我这方法好像把字幕组的活儿都给干了，难道以后字幕组都可以解散了？
虽然只是句玩笑话, 不过说真的，时代的洪流不服不行，好多职业都在 AI 这股洪流中“灰飞烟灭”了。

想当年，字幕组给少年时期的我带来了好多欢乐。那时候我就想着，要是我能苦练英语，以后成为一名光荣的字幕组成员。
没想到现在我成了程序员，居然写个小程序就能把字幕组的活儿给干了，这世界变化真快，就像歌里唱的“不是我不明白，这世界变化快”。

在人工智能蓬勃发展的时代，好多岗位都面临着被取代的风险呀，我们程序员也不例外, 令人唏嘘的是，程序员自己写程序把自己的职位给搞没了.
虽然说程序员不会都失业，毕竟人工智能也是要靠我们程序员来实现，但以后确实也不需要那么多程序员了。君不见，多少公司都在搞“裁员广进”，
就连宇宙大厂微软最近也都传出了裁员的消息呢。我自己也是前两年刚从大厂被裁员出来的，说起来都是一把辛酸泪。

好啦，废话不多说，咱们来看看这个小程序是怎么把字幕组的活儿都干了。

## 详细步骤
### **第一步**：将mp4文件的语音提取为 wave 文件

将视频文件转换成音频文件，让它变成我们更容易处理的格式。对应的代码如下：
```python
def extract_audio_from_video(mp4_file, audio_file):
    """Extract audio from an MP4 file and save as WAV."""
    ffmpeg.input(mp4_file).output(audio_file).global_args('-loglevel', 'error').run()
    return audio_file
```

在命令行中使用时，相关操作示例（假设你已经安装好ffmpeg）：无单独命令行，它是被程序内部调用的哦，你只需要提供正确的mp4文件路径，程序就会自动处理并生成对应的wave文件。

### **第二步**：调用 whisper 识别语音为文本。

这个whisper就厉害, openai 出口, 必属精品, 可以把视频里的语音识别成文字呢。代码如下：

```python
def transcribe_audio_with_whisper(audio_file, model_name="base"):
    """Transcribe audio to text using Whisper."""
    # Load Whisper model
    model = whisper.load_model(model_name)

    # Transcribe audio
    result = model.transcribe(audio_file)
    return result["text"]
```
同样，这部分也是程序内部调用，没有直接面向用户的命令行操作，但你可以了解到它是如何加载模型并进行语音转文字的核心逻辑。
为了制作字幕文件, 我们最好按段落识别, 并记录段落的赶止时间, 代码如下：
```python
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
```
### **第三步**：调用Google Translate把文本翻译成中文。
-
借助 google translator 这个强大的翻译工具，英文文本能轻松翻译成中文啦。代码如下：
```python
async def translate_text(text, src, dest):
    """Translate text from English to Chinese."""
    translator = Translator()
    translated = await translator.translate(text, src=src, dest=dest)
    return translated.text

def do_translate(text_file, text, src, dest):
    translated_text = asyncio.run(translate_text(text, src, dest))
    dest_file_name = text_file.replace(src, dest)
    with open(os.path.join(dest_file_name), "w", encoding="utf-8") as f:
        f.write(translated_text)

    print(f"### Transcribed Text:\n {translated_text}")
```
它利用`googletrans`库的`Translator`类来实现异步翻译，将源语言文本转换成目标语言文本。

### **第四步**：将文本转换为字幕文件srt格式。

代码中虽然没有单独一个函数明确叫“转换为srt格式”，但实际上整个流程最终生成的文本文件（如果指定格式为`srt`）就是按照字幕文件格式要求来组织内容的，关键在于`transcribe_audio_with_segments`函数中对段落、时间戳等信息的处理，生成符合字幕格式规范的文本段落，比如:

```python
paragraphs.append(f"\n{sn}\n[{format_time(paragraph_start_time)} --> {format_time(end_time)}]\n{merged_text}")
```

这里`format_time`函数用来格式化时间戳：
```python
def format_time(seconds):
    millis = int((float(seconds) % 1) * 1000)
    seconds = int(float(seconds))
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"
```
### **第五步**：播放原本的mp4文件，并载入生成的字幕文件。

如此这般, 我们就能看着带有中文字幕的视频啦。这一步通常是在视频播放软件中操作，比如常见的VLC播放器，你在播放mp4文件时，在播放器界面找到加载字幕的选项，然后选择我们程序生成的`srt`字幕文件即可。不同播放器操作略有不同，但大致思路一样。

## 具体用法

具体的用法可以参见[https://github.com/walterfan/video_to_text/edit/master/README.md](https://github.com/walterfan/video_to_text/edit/master/README.md) 。

这个脚本是用Python写的，它可以把mp4视频通过 whisper 转换成文本，并且还能把文本从默认的源语言“en”翻译成默认的目标语言“zh-cn”, 最后生成字幕文件。

### 前提条件
首先，你得安装ffmpeg和一些必要的库。

在Mac上可以用

```bash
brew install ffmpeg
```

来安装ffmpeg，然后用

```bash
pip install -r requirements.txt
```

来安装其他需要的库。

### 使用方法
安装好之后呢，就可以使用啦。在命令行里输入

```bash
./video_to_text.py -h
```
就能看到具体的使用说明咯, 有如下参数可以设置:

* --input INPUT: 也就是你要输入的mp4文件的路径；
* --output OUTPUT”: 这是输出的文本文件的路径，如果不指定的话，就会和输入文件同名，但是扩展名是“.srt”哦；
* --model MODEL: whisper 使用的模型，默认是“small”；
* --src SRC: 源语言，默认是“en”, 即英文
* --dest DEST: 目标语言, 默认是“zh-cn”, 即中文
* --format FORMAT: 输出格式，目前只支持“txt”和“srt”格式哟。

例如，你可以输入如下命令来生成视频的一个对应的字幕文件

```bash
./video_to_text.py -i./example/5_minutes_for_50_years.mp4
```
生成的结果

* 5_min_for_50_years_en.srt
```

1
[00:00:00,620 --> 00:00:32,600]
I'm gonna talk to you about some things I've learned in my journey. Most from experience, some of them I've heard in passing, many of them I'm still practicing, but all of them I do believe are true. Life is not easy. It is not. Don't try to make it that way. Life's not fair. It never was. It is it now and it won't ever be. Do not fall into the trap, the entitlement trap, a feeling like you're a victim. You are not. Get over it and get on with it.

2
[00:00:28,079 --> 00:04:04,680]
So the question that we're gonna ask ourselves is what success is to us. What success is to you? Is it more money? That's fine. I got nothing against money. Maybe it's a healthy family. Maybe it's a happy marriage. Maybe it's to help others to be famous, to be spiritually sound, to leave the world a little bit better place than you found it. Continue to ask yourself that question. Now your answer may change over time and that's fine. But do yourself this favor. Whatever your answer is, don't choose anything that will jeopardize your soul. Prioritize who you are, who you want to be, and don't spend time with anything that antagonizes your character. Be brave, take the hill, but first answer that question what's my hill? For first, we have to define success for ourselves and then we have to put in the work to maintain it. Take that daily talent. Tend our guard. Keep the things that are important to us in good shape. Where you are not is as important as where you are. It is just as important where we are not as it is where we are. Look, the first step that leads to our identity life is usually not. I know who I am. I know who I am. That's not the first step. The first steps usually I know who I am not. Process of elimination. Defining ourselves by what we are not is the first step that leads us to really knowing who we are. You know, that group of friends that you hang out with that really might not bring out the best in you. They gossip too much, they're kind of shady. They really aren't going to be there for you in a pinch. How about that bar that we keep going to that we always seem to have the worst hangover problem? Or that computer screen, right? The computer screen that keeps giving us an excuse not to get out of the house and engage with the world and get some real human interaction. How about that food that we keep eating? Stuff that tastes so good going down, makes us feel like crap the next week? We feel a thardic when we keep putting on weight? Well, those people, those places, those things, stop giving them your time and energy. Just don't go there. I mean, put them down. And when you do this, when you do put them down, you put them down there. When you put them in your time, you inadvertently find yourself spending more time and in more places that are healthy for you, that bring you more joy. Why? Because you just eliminated the who's, the where's, the what's and the wins that were keeping you from your identity. Look, trust me, too many options. I promise you, too many options will make a tyrant of us all. Alright, so get rid of the excess, the wasted time, decrease your options. If you do this, you will have accidentally, almost innocently, put in front of you what is important to you. By processing elimination. Knowing who we are is hard. It's hard. Give yourself a break. Eliminate who you are not first. And you're going to find yourself where you need to be.

3
[00:03:59,139 --> 00:04:26,939]
Instead of creating outcomes that take from us, let's create more outcomes that pay us back. Fill us up. Keep your fire lit. Turn you on for the most amount of time in your future. We try our best. We don't always do our best.

4
[00:04:16,899 --> 00:04:50,120]
Architecture is a verb as well. And since we are the architects of our own lives, let's study the habits, the practices, the routines that we have that lead to and feed our success. Our joy, our honest pain, our laughter, our earned tears. Let's dissect that and give thanks for those things. And when we do that, guess what happens? We get better at them. And we have more to dissect.

5
[00:04:43,980 --> 00:05:00,120]
Be discerning. Choose it because you want it. Do it because you want to.

6
[00:04:52,819 --> 00:05:23,519]
We're going to make mistakes. You got to own them. Then you got to make amends. And then you got to move on. Guilt and regret kills many a man before their time. So turn the page. Get off the ride. You are the author of the book of your life.
Thank you.
```

* 5_min_for_50_years_zh-cn.srt
```
1
[00:00:00,620 --> 00:00:32,600]
我将和你谈谈我在旅途中学到的一些事情。大多数来自经验，其中一些是我偶然听到的，其中许多我仍在练习，但我相信所有这些都是真实的。生活并不容易。它不是。不要试图那样做。生活并不公平。从来都不是。现在是这样，以后也不会是这样。不要落入陷阱、权利陷阱、感觉自己是受害者。你不是。克服它并继续它。

2
[00:00:28,079 --> 00:04:04,680]
所以我们要问自己的问题是成功对我们来说意味着什么。成功对你来说意味着什么？是不是钱多了？没关系。我对金钱没有任何抵触。也许这就是一个健康的家庭。也许这才是幸福的婚姻。也许是为了帮助别人出名，在精神上健全，让世界变得比你发现的更好一些。继续问自己这个问题。现在你的答案可能会随着时间的推移而改变，但这没关系。但帮自己一个忙吧。无论你的答案是什么，都不要选择任何会危及你灵魂的事情。优先考虑你是谁，你想成为谁，不要把时间花在任何与你的性格相悖的事情上。勇敢一点，登上这座山，但首先要回答这个问题：我的山是什么？首先，我们必须为自己定义成功，然后我们必须付出努力来维持它。以日常天赋为例。照顾我们的警卫。保持对我们重要的事物处于良好状态。你不在的地方和你在的地方同样重要。我们不在的地方和我们在的地方同样重要。看，通向我们身份生活的第一步通常不是。我知道我是谁。我知道我是谁。这不是第一步。第一步通常我知道我不是谁。消除过程。通过我们不是什么来定义自己是让我们真正了解自己是谁的第一步。你知道，和你一起出去玩的那群朋友可能并不能发挥出你最好的一面。他们闲话太多，有点阴暗。他们真的不会在紧要关头为你提供帮助。我们经常去的那个酒吧怎么样，我们似乎总是有最严重的宿醉问题？或者那个电脑屏幕，对吧？电脑屏幕不断给我们借口不走出家门，与世界接触，进行一些真正的人际互动。我们一直吃的食物怎么样？味道很好的东西下周会让我们感觉很糟糕吗？当我们体重持续增加时，我们会感到疲劳吗？好吧，那些人，那些地方，那些事，停止给他们你的时间和精力。只是不要去那里。我的意思是，把它们放下。当你这样做时，当你把它们放下时，你就把它们放在那里。当你把它们放在你的时间里时，你会不经意地发现自己花了更多的时间和更多对你健康的地方，这给你带来更多的快乐。为什么？因为你刚刚消除了那些阻碍你了解自己身份的人物、地点、事件和胜利。看，相信我，有太多选择。我向你保证，太多的选择会让我们所有人成为暴君。好吧，所以摆脱多余的、浪费的时间，减少你的选择。如果你这样做，你就会无意中、几乎是无辜地把对你来说重要的东西摆在你面前。通过处理消除。知道我们是谁很难。这很难。让自己休息一下。首先消除你不是的人。你会发现自己处于你需要去的地方。

3
[00:03:59,139 --> 00:04:26,939]
让我们创造更多回报我们的成果，而不是创造索取我们利益的成果。填满我们。让你的火一直点燃。让您在未来的大部分时间内保持活力。我们尽力而为。我们并不总是尽力而为。

4
[00:04:16,899 --> 00:04:50,120]
建筑也是一个动词。既然我们是自己生活的建筑师，那么让我们研究一下我们的习惯、做法和惯例，这些习惯、做法和惯例会导致并促进我们的成功。我们的欢乐，我们真诚的痛苦，我们的笑声，我们应得的泪水。让我们剖析一下并感谢这些事情。当我们这样做时，猜猜会发生什么？我们在这些方面做得更好。我们还有更多需要剖析的内容。

5
[00:04:43,980 --> 00:05:00,120]
要有辨别力。选择它，因为您想要它。因为你想做所以去做。

6
[00:04:52,819 --> 00:05:23,519]
我们会犯错误。你必须拥有它们。那你就得去弥补。然后你必须继续前进。内疚和悔恨会提前杀死许多人。所以翻页吧。下车吧。你是你生命之书的作者。
谢谢。
```

对应的完整代码可以参见[https://github.com/walterfan/video_to_text/blob/master/video_to_text.py](https://github.com/walterfan/video_to_text/blob/master/video_to_text.py) 。

### 小技巧

另外，还有几个小技巧:

* 你可以从YouTube或其他网站上下载任何你想要的视频，然后用这个脚本来制作字幕哦。

比如说，你可以用[https://cobalt.tools/](https://cobalt.tools/) 这个网站来下载视频。

* 下载好之后呢，还可以对视频进行一些处理。比如说用如下命令来裁剪视频

```bash
ffmpeg -i input.mp4 -ss 00:00:07 -c:v copy -c:a copy output_trimmed.mp4
```

* 或者用如下命令来转换视频的尺寸和码率

```bash
ffmpeg -i output_trimmed.mp4 -vf scale=320:180 -c:v libx264 -preset fast -crf 23 -c:a aac -b:a 192k output_180p.mp4
```

具体的代码可以参见[https://github.com/walterfan/video_to_text/blob/master/video_to_text.py](https://github.com/walterfan/video_to_text/blob/master/video_to_text.py) 。怎么样，是不是很有趣呀，大家也赶紧去试试吧。

---

希望以上内容你能喜欢，你可以根据实际情况进行调整和修改, 并回馈到代码库 [https://github.com/walterfan/video_to_text](https://github.com/walterfan/video_to_text), 让更多人受益。如果你还有其他问题，欢迎随时问我, 我会尽力回答。

<hr/>
本作品采用[知识共享署名-非商业性使用-禁止演绎 4.0 国际许可协议](http://creativecommons.org/licenses/by-nc-nd/4.0/)进行许可。