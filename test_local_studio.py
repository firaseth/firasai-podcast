import sys
import os
import sqlite3
import json
from pydub import AudioSegment
from tools.db_tool import DbTool
from tools.audio_tool import AudioTool
from config import Config

def run_local_validation_test():
    print("🧪 Starting Local Podcast Studio Validation Test...")
    print(f"🐍 Python version: {sys.version}")
    
    # 1. Test Database Caching
    print("\n--- Phase 1: Testing SQLite Caching (db_tool) ---")
    try:
        db = DbTool("data/test_firasai.db")
        print("✅ SQLite Database initialized successfully.")
        
        # Test Caching an Episode
        test_episode_id = "test_ep_999"
        test_title = "The Quantum Leap: AI in 2026"
        test_topic = "Quantum AI"
        test_script = "Hello and welcome to FirasAi. Today we are talking about Quantum Computing..."
        test_research = {"stats": ["1. Quantum power is up 1000%"], "quotes": ["AI is quantum."]}
        test_show_notes = {"hook": "The quantum shift is here.", "takeaways": ["Quantum leverage."]}
        
        db.cache_episode(
            episode_id=test_episode_id,
            title=test_title,
            topic=test_topic,
            status="Draft",
            script=test_script,
            research=test_research,
            show_notes=test_show_notes
        )
        print("✅ Episode successfully cached in SQLite.")
        
        # Verify Retrieval
        cached = db.get_cached_episodes(1)
        if len(cached) > 0 and cached[0]["id"] == test_episode_id:
            print(f"✅ Verified Data Retrieval: Found cached episode: '{cached[0]['title']}'")
        else:
            raise Exception("Retrieved data does not match cached data.")
            
    except Exception as e:
        print(f"❌ Database Phase Failed: {e}")
        return False

    # 2. Test Audio Generation & Mastering Engine
    print("\n--- Phase 2: Testing Audio Generation & Master Mixing (pydub & ffmpeg) ---")
    try:
        # Create a mock 3-second voiceover segment (using pure sine wave/silence to avoid API calls)
        print("🔊 Generating mock voiceover (5 seconds)...")
        voiceover = AudioSegment.silent(duration=5000) # 5 seconds
        os.makedirs("data", exist_ok=True)
        voice_path = "data/test_voiceover.mp3"
        voiceover.export(voice_path, format="mp3")
        print(f"✅ Mock voiceover saved to: {voice_path} ({os.path.getsize(voice_path)} bytes)")
        
        # Create a mock 10-second background music track
        print("🎵 Generating mock background music track (10 seconds)...")
        music = AudioSegment.silent(duration=10000) + 10 # 10 seconds of background pad
        music_path = "data/calm_music.mp3"
        music.export(music_path, format="mp3")
        print(f"✅ Mock background music saved to: {music_path} ({os.path.getsize(music_path)} bytes)")
        
        # Test Mixing
        print("🎛️ Running master mixer...")
        config = Config()
        audio_tool = AudioTool(config)
        
        master_path = "data/test_master.mp3"
        final_master = audio_tool.mix_voice_and_music(
            voice_path=voice_path,
            music_path=music_path,
            output_path=master_path,
            music_volume_db=-10
        )
        
        if final_master and os.path.exists(final_master) and os.path.getsize(final_master) > 0:
            print(f"✅ Audio Mastering Complete! Final mixed MP3 saved at: {final_master} ({os.path.getsize(final_master)} bytes)")
        else:
            raise Exception("Mixed master file is missing or empty.")
            
    except Exception as e:
        print(f"❌ Audio Phase Failed: {e}")
        print("💡 Ensure FFMPEG is installed on your local computer to process MP3 files.")
        return False

    # Clean up test database
    try:
        if os.path.exists("data/test_firasai.db"):
            os.remove("data/test_firasai.db")
    except:
        pass

    print("\n🎉 ALL LOCAL VALIDATION TESTS PASSED SUCCESSFULLY!")
    print("Your SQLite Cache and Audio Mastering Engine are 100% operational.")
    return True

if __name__ == "__main__":
    run_local_validation_test()
