import os
import ffmpeg
import whisper
import asyncio
from googletrans import Translator
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Import the LLM agent
try:
    from .simple_llm_agent import LlmAgent
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: LLM agent not available, using Google Translate only")

class VideoProcessor:
    def __init__(self):
        self.translator = Translator()
        # Initialize LLM agent if available
        self.llm_agent = None
        if LLM_AVAILABLE:
            try:
                self.llm_agent = LlmAgent()
                print("LLM agent initialized successfully")
            except Exception as e:
                print(f"Failed to initialize LLM agent: {e}")
                self.llm_agent = None
    
    def format_time(self, seconds):
        """Format time for SRT format"""
        millis = int((float(seconds) % 1) * 1000)
        seconds = int(float(seconds))
        mins, secs = divmod(seconds, 60)
        hrs, mins = divmod(mins, 60)
        return f"{hrs:02}:{mins:02}:{secs:02},{millis:03}"
    
    def extract_audio_from_video(self, video_file, audio_file):
        """Extract audio from video file"""
        try:
            ffmpeg.input(video_file).output(audio_file).global_args('-loglevel', 'error').run()
            return True
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return False
    
    def transcribe_audio_with_segments(self, audio_file, model_name="small", src_language="auto"):
        """Transcribe audio with timestamps"""
        try:
            model = whisper.load_model(model_name)
            
            # Set language parameter
            language = None if src_language == "auto" else src_language
            
            result = model.transcribe(audio_file, word_timestamps=True, language=language)
            
            segments = result["segments"]
            captions = []
            
            for i, segment in enumerate(segments, 1):
                start_time = segment["start"]
                end_time = segment["end"]
                text = segment["text"].strip()
                
                if text:  # Only add non-empty segments
                    captions.append({
                        'id': i,
                        'start': self.format_time(start_time),
                        'end': self.format_time(end_time),
                        'text': text
                    })
            
            return captions
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return []
    
    def translate_text_with_llm(self, text, src, dest):
        """Translate text using LLM agent"""
        if not self.llm_agent:
            return None
        
        try:
            # Create language mapping for better prompts
            language_names = {
                'en': 'English',
                'zh': 'Chinese',
                'zh-cn': 'Simplified Chinese',
                'zh-tw': 'Traditional Chinese',
                'ja': 'Japanese',
                'ko': 'Korean',
                'es': 'Spanish',
                'fr': 'French',
                'de': 'German'
            }
            
            src_name = language_names.get(src, src)
            dest_name = language_names.get(dest, dest)
            
            system_prompt = f"You are a professional translator. Translate the given text from {src_name} to {dest_name}. Only return the translated text, no explanations or additional text."
            user_prompt = f"Translate this text: {text}"
            
            translated_text = self.llm_agent.get_str_response(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_token=1000,
                temperature=0.3
            )
            
            return translated_text.strip()
        except Exception as e:
            print(f"Error translating with LLM: {e}")
            return None
    
    def translate_text_with_google(self, text, src, dest):
        """Translate text using Google Translate as fallback"""
        try:
            import asyncio
            import nest_asyncio
            
            # Allow nested event loops
            nest_asyncio.apply()
            
            # Get or create event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run the async translation
            translated = loop.run_until_complete(
                self.translator.translate(text, src=src, dest=dest)
            )
            return translated.text
        except Exception as e:
            print(f"Error translating with Google Translate: {e}")
            return text
    
    def translate_text_sync(self, text, src, dest):
        """Translate text with LLM first, fallback to Google Translate"""
        # Try LLM first if available
        if self.llm_agent:
            translated = self.translate_text_with_llm(text, src, dest)
            if translated:
                return translated
            print("LLM translation failed, falling back to Google Translate")
        
        # Fallback to Google Translate
        return self.translate_text_with_google(text, src, dest)
    
    def translate_captions(self, captions, src_language, dest_language, translation_method='llm'):
        """Translate all captions using specified method"""
        if src_language == dest_language or dest_language == "auto":
            return captions
        
        translated_captions = []
        for caption in captions:
            if translation_method == 'google':
                # Force Google Translate
                translated_text = self.translate_text_with_google(
                    caption['text'], src_language, dest_language
                )
            else:
                # Use LLM with Google fallback
                translated_text = self.translate_text_sync(
                    caption['text'], src_language, dest_language
                )
            translated_captions.append({
                'id': caption['id'],
                'start': caption['start'],
                'end': caption['end'],
                'text': translated_text
            })
        
        return translated_captions
    
    def process_media(self, media_file, job_id, model_name, src_language, dest_language, status_dict, translation_method='llm'):
        """Main processing function for video or audio files"""
        try:
            # Determine if file is audio or video
            file_extension = os.path.splitext(media_file)[1].lower()
            audio_extensions = ['.mp3', '.wav', '.ogg', '.m4a', '.aac', '.flac']
            is_audio_file = file_extension in audio_extensions
            
            if is_audio_file:
                # For audio files, skip extraction step
                status_dict[job_id]['current_step'] = 'Transcribing audio...'
                status_dict[job_id]['progress'] = 30
                audio_file = media_file
            else:
                # For video files, extract audio first
                status_dict[job_id]['current_step'] = 'Extracting audio...'
                status_dict[job_id]['progress'] = 10
                
                file_path = media_file.rsplit(".", 1)[0]
                audio_file = f"{file_path}_temp.wav"
                
                if not self.extract_audio_from_video(media_file, audio_file):
                    status_dict[job_id]['status'] = 'error'
                    status_dict[job_id]['error'] = 'Failed to extract audio from video'
                    return
                
                # Update status
                status_dict[job_id]['current_step'] = 'Transcribing audio...'
                status_dict[job_id]['progress'] = 30
            
            # Transcribe audio
            captions = self.transcribe_audio_with_segments(audio_file, model_name, src_language)
            
            if not captions:
                status_dict[job_id]['status'] = 'error'
                status_dict[job_id]['error'] = 'Failed to transcribe audio'
                return
            
            # Store original captions
            status_dict[job_id]['original_captions'] = captions
            
            # Update status
            status_dict[job_id]['current_step'] = 'Translating text...'
            status_dict[job_id]['progress'] = 70
            
            # Translate if needed
            translated_captions = captions
            if src_language != dest_language and dest_language != "auto":
                translated_captions = self.translate_captions(captions, src_language, dest_language, translation_method)

            # Update status
            status_dict[job_id]['current_step'] = 'Finalizing...'
            status_dict[job_id]['progress'] = 90
            
            # Store results
            status_dict[job_id]['captions'] = translated_captions  # Keep this for backward compatibility
            status_dict[job_id]['translated_captions'] = translated_captions
            status_dict[job_id]['original_filename'] = os.path.basename(media_file)
            status_dict[job_id]['status'] = 'completed'
            status_dict[job_id]['progress'] = 100
            status_dict[job_id]['current_step'] = 'Completed!'
            
            # Clean up temporary files (only if we created them)
            if not is_audio_file and os.path.exists(audio_file):
                os.remove(audio_file)
                
        except Exception as e:
            status_dict[job_id]['status'] = 'error'
            status_dict[job_id]['error'] = str(e)
            print(f"Error processing video: {e}")
