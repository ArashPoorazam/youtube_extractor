import os
import re
from pytubefix import YouTube
from typing import Optional
import ffmpeg
import logging 

logger = logging.getLogger(__name__)

class YoutubeVideo():
    """
    A utility class for interacting with YouTube videos via pytubefix.
    """

    def __init__(self, link):
        self.yt = YouTube(link)

    def _extract_text_from_xml(self, xml_caption: str) -> str:
        # 1. Remove XML tags
        text = re.sub(r'<[^>]+>', '', xml_caption)
        
        # 2. Decode common HTML entities 
        text = text.replace('&amp;', '&').replace('&#39;', "'")
        
        # 3. Clean up whitespace and newlines from XML structure
        text = re.sub(r'\s*\n\s*', '\n', text)
        text = text.strip()
        
        return text

    def get_pure_subtitles_text(self, lang_code: str) -> Optional[str]:
        # Try finding the exact match first, then the auto-generated version
        caption = self.yt.captions.get_by_language_code(lang_code) or \
                  self.yt.captions.get_by_language_code(f'a.{lang_code}')
                  
        if caption is None:
            return None
        
        # 1. Get raw XML captions
        raw_xml = caption.xml_captions
        
        # 2. Extract and return pure text
        return self._extract_text_from_xml(raw_xml)

    def download_video_144(self) -> Optional[str]:
        try:
            stream = self.yt.streams.get_by_resolution("144p") or self.yt.streams.filter(res="144p").first()
            if stream is not None:
                # Use the 'videos' subdirectory
                file_path = stream.download(output_path='videos')
                return file_path
            return None
        except Exception as e:
            logger.error(f"Failed to download 144p video for {self.yt.title}: {e}")
            return None
    
    def download_video_360(self) -> Optional[str]:
        try:
            stream = self.yt.streams.get_by_resolution("360p") or self.yt.streams.filter(res="360p").first()
            if stream is not None:
                # Use the 'videos' subdirectory
                file_path = stream.download(output_path='videos')
                return file_path
            return None
        except Exception as e:
            logger.error(f"Failed to download 360p video for {self.yt.title}: {e}")
            return None
        
    def download_video_720(self) -> Optional[str]:
        video_res = "720p"
        output_dir = 'videos'
        
        try:
            # 1. Download Video-only stream 
            video_stream = self.yt.streams.filter(res=video_res, progressive=False, file_extension='mp4').first()
            if not video_stream:
                logger.error(f"No {video_res} video-only stream found for {self.yt.title}.")
                return None
            
            # 2. Download Audio-only stream
            audio_stream = self.yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
            if not audio_stream:
                logger.error(f"No suitable audio stream found for {self.yt.title}.")
                return None
            
            # Define temporary file paths
            # Note: We append resolution to ensure unique temp file names if multiple resolutions are run concurrently
            video_filepath = video_stream.download(output_path=output_dir, filename=f'temp_video_{video_res}')
            audio_filepath = audio_stream.download(output_path=output_dir, filename=f'temp_audio_{video_res}')

            # Define final merged file path
            safe_title = "".join(c for c in self.yt.title if c.isalnum() or c in (' ', '_')).rstrip()
            final_filepath = os.path.join(output_dir, f"{safe_title}_{video_res}.mp4")

            # 3. Merge video and audio using FFmpeg
            (
                ffmpeg
                .input(video_filepath)
                .output(ffmpeg.input(audio_filepath), final_filepath, vcodec='copy', acodec='copy')
                .run(overwrite_output=True, quiet=True)
            )

            # 4. Clean up temporary files
            os.remove(video_filepath)
            os.remove(audio_filepath)
            
            return final_filepath
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error during merge: {e.stderr.decode('utf8')}")
            return None
        except Exception as e:
            logger.error(f"Failed to download/merge {video_res} video for {self.yt.title}: {e}")
            return None
        
    def download_video_1080(self) -> Optional[str]:
        video_res = "1080p"
        output_dir = 'videos'
        
        try:
            # 1. Download Video-only stream 
            video_stream = self.yt.streams.filter(res=video_res, progressive=False, file_extension='mp4').first()
            if not video_stream:
                logger.error(f"No {video_res} video-only stream found for {self.yt.title}.")
                return None
            
            # 2. Download Audio-only stream 
            audio_stream = self.yt.streams.filter(only_audio=True, file_extension='mp4').order_by('abr').desc().first()
            if not audio_stream:
                logger.error(f"No suitable audio stream found for {self.yt.title}.")
                return None
            
            # Define temporary file paths
            # Note: We append resolution to ensure unique temp file names if multiple resolutions are run concurrently
            video_filepath = video_stream.download(output_path=output_dir, filename=f'temp_video_{video_res}')
            audio_filepath = audio_stream.download(output_path=output_dir, filename=f'temp_audio_{video_res}')

            # Define final merged file path
            safe_title = "".join(c for c in self.yt.title if c.isalnum() or c in (' ', '_')).rstrip()
            final_filepath = os.path.join(output_dir, f"{safe_title}_{video_res}.mp4")

            # 3. Merge video and audio using FFmpeg
            (
                ffmpeg
                .input(video_filepath)
                .output(ffmpeg.input(audio_filepath), final_filepath, vcodec='copy', acodec='copy')
                .run(overwrite_output=True, quiet=True)
            )

            # 4. Clean up temporary files
            os.remove(video_filepath)
            os.remove(audio_filepath)
            
            return final_filepath
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error during merge: {e.stderr.decode('utf8')}")
            return None
        except Exception as e:
            logger.error(f"Failed to download/merge {video_res} video for {self.yt.title}: {e}")
            return None

    def download_audio(self) -> Optional[str]:
        try:
            stream = self.yt.streams.filter(only_audio=True, file_extension='mp4').first()
            if stream is not None:
                # Use the dedicated 'audios' subdirectory
                file_path = stream.download(output_path='audios')
                return file_path
            return None
        except Exception as e:
            logger.error(f"Failed to download audio for {self.yt.title}: {e}")
            return None