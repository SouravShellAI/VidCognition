import re
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url):
    """
    Uses Regex patterns to isolate the 11-character YouTube video ID from various URL formats.
    Supports standard, shortened (youtu.be), and attribution URLs.
    """
    patterns = [r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", r"be\/([0-9A-Za-z_-]{11})"]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match: return match.group(1)
    return None

def ingest_youtube_video():
    """
    Main execution flow for downloading and saving YouTube transcripts.
    """
    user_url = input("Enter the YouTube URL: ").strip()
    video_id = extract_video_id(user_url)

    if not video_id:
        print("❌ Invalid URL.")
        return

    print(f"--- ANALYZING VIDEO: {video_id} ---")

    try:
        # Initialize the YouTube Transcript API client
        ytt_api = YouTubeTranscriptApi()
        
        print("Fetching transcript...")
        # Retrieve all available transcripts for the given video ID
        transcript_list = ytt_api.list(video_id)

        try:
            # Priority 1: Attempt to find transcripts in Bengali or English
            transcript = transcript_list.find_transcript(['bn', 'en'])
        except:
            # Priority 2: Fallback to the first available language (Auto-generated or Original)
            print("Preferred languages not found. Fetching original language...")
            transcript = next(iter(transcript_list))

        # Output the detected language for user clarity
        print(f" FOUND TRANSCRIPT IN: {transcript.language} ({transcript.language_code}) ")
        data = transcript.fetch()
        
        # Merge individual timestamped segments into a single cohesive string
        full_text = "\n".join([item.text for item in data])
        
        # Persist the raw transcript to a local text file for downstream processing
        with open("transcript.txt", "w", encoding="utf-8") as f:
            f.write(full_text)

        print(f" SUCCESS: {len(full_text)} characters stored in transcript.txt ")

    except Exception as e:
        print(f"❌ Error during ingestion: {e}")

if __name__ == "__main__":
    ingest_youtube_video()