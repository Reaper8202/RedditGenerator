from gtts import gTTS
import os

voiceoverDir = "Voiceovers"

def create_voice_over(fileName, text):
    if not os.path.exists(voiceoverDir):
        os.makedirs(voiceoverDir)
    
    filePath = os.path.join(voiceoverDir, f"{fileName}.mp3")
    print(f"Saving voiceover to: {filePath}")
    
    tts = gTTS(text=text, lang='en')
    tts.save(filePath)
    
    # Check if the file was created successfully
    if os.path.isfile(filePath):
        print(f"File saved successfully: {filePath}")
    else:
        print(f"Failed to save file: {filePath}")
    
    return filePath

# Example usage
if __name__ == "__main__":
    fileName = "example"
    text = "This is an example text for voiceover."
    voiceover_path = create_voice_over(fileName, text)
    print(f"Voiceover created and saved to: {voiceover_path}")
