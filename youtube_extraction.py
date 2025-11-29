from pytube import YouTube
from typing import Optional, Tuple
import os

class YoutubeVideo():
    """
    A utility class for interacting with YouTube videos via pytube.
    Note: Downloading high-resolution streams (720p/1080p) often results in video-only files
    due to YouTube's adaptive streaming. The bot user may receive silent videos at these resolutions.
    A full solution requires merging audio and video streams (using libraries like ffmpeg).
    """
    def __init__(self, link):
        self.yt = YouTube(link)

    def check_subs(self) -> Tuple[bool, bool]:
        en = False
        ru = False
        try:
            captions = self.yt.captions
            en = captions.get_by_language_code('en') is not None or captions.get_by_language_code('a.en') is not None
            ru = captions.get_by_language_code('ru') is not None or captions.get_by_language_code('a.ru') is not None
            
            # Manual loop check for robust subtitle code detection
            if not en:
                for c in captions:
                    code = getattr(c, 'code', '') or getattr(c, 'language_code', '') or str(c)
                    if 'en' in code:
                        en = True
                        break
            if not ru:
                for c in captions:
                    code = getattr(c, 'code', '') or getattr(c, 'language_code', '') or str(c)
                    if 'ru' in code:
                        ru = True
                        break
        except Exception:
            en = False
            ru = False
        return en, ru

    def get_en_subtitles(self) -> Optional[str]:
        caption = self.yt.captions.get_by_language_code('en') or self.yt.captions.get_by_language_code('a.en')
        if caption is None:
            return None
        return caption.generate_srt_captions()
    
    def get_ru_subtitles(self) -> Optional[str]:
        caption = self.yt.captions.get_by_language_code('ru') or self.yt.captions.get_by_language_code('a.ru')
        if caption is None:
            return None
        return caption.generate_srt_captions()

    def download_video_144(self) -> Optional[str]:
        # Prioritize progressive stream (video + audio)
        stream = self.yt.streams.get_by_resolution("144p") or self.yt.streams.filter(res="144p").first()
        if stream is not None:
            file_path = stream.download(output_path='videos')
            return file_path
        else:
            return None
    
    def download_video_360(self) -> Optional[str]:
        stream = self.yt.streams.get_by_resolution("360p") or self.yt.streams.filter(res="360p").first()
        if stream is not None:
            file_path = stream.download(output_path='videos')
            return file_path
        else:
            return None
        
    def download_video_720(self) -> Optional[str]:
        # Often returns video-only stream (no audio).
        stream = self.yt.streams.get_by_resolution("720p") or self.yt.streams.filter(res="720p").first()
        if stream is not None:
            file_path = stream.download(output_path='videos')
            return file_path
        else:
            return None
        
    def download_video_1080(self) -> Optional[str]:
        # Often returns video-only stream (no audio).
        stream = self.yt.streams.get_by_resolution("1080p") or self.yt.streams.filter(res="1080p").first()
        if stream is not None:
            file_path = stream.download(output_path='videos')
            return file_path
        else:
            return None

    def download_audio(self) -> Optional[str]:
        stream = self.yt.streams.filter(only_audio=True, file_extension='mp4').first()
        if stream is not None:
            file_path = stream.download(output_path='videos')
            return file_path
        else:
            return None