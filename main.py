from moviepy.editor import *
import reddit, screenshot, time, subprocess, random, configparser, sys, math
from os import listdir
from os.path import isfile, join, exists

class Script:
    def __init__(self, url, title_audio_clip=None):
        self.url = url
        self.titleSCFile = None  # To store the screenshot file path
        self.titleAudioClip = title_audio_clip  # To store the audio clip path
        self.frames = []  # To store comment frames

    def getDuration(self):
        # Placeholder for actual implementation to get the duration of the script
        return 10

    def getFileName(self):
        # Placeholder for actual implementation to get the file name
        return "output_filename"

def createVideo():
    config = configparser.ConfigParser()
    config.read('config.ini')
    outputDir = config["General"]["OutputDirectory"]

    startTime = time.time()

    # Get script from reddit
    # If a post id is listed, use that. Otherwise query top posts
    if len(sys.argv) == 2:
        script = reddit.getContentFromId(outputDir, sys.argv[1])
    else:
        postOptionCount = int(config["Reddit"]["NumberOfPostsToSelectFrom"])
        script = reddit.getContent(outputDir, postOptionCount)
    fileName = script.getFileName()

    # Create screenshots
    screenshot.getPostScreenshot(fileName, script)
    print(f"Title screenshot file: {script.titleSCFile}")

    # Setup background clip
    bgDir = config["General"]["BackgroundDirectory"]
    bgPrefix = config["General"]["BackgroundFilePrefix"]
    bgFiles = [f for f in listdir(bgDir) if isfile(join(bgDir, f))]
    bgCount = len(bgFiles)

    if bgCount == 1:
        bgIndex = 0  # Use the only available video
    elif bgCount > 1:
        bgIndex = random.randint(0, bgCount - 1)
    else:
        raise ValueError("No background videos available")

    backgroundVideo = VideoFileClip(
        filename=f"{bgDir}/{bgPrefix}{bgIndex}.mp4", 
        audio=False).subclip(0, script.getDuration())
    w, h = backgroundVideo.size

    def __createClip(screenShotFile, audioClip, marginSize):
        if not screenShotFile:
            raise FileNotFoundError(f"Screenshot file not found: {screenShotFile}")
        if not exists(screenShotFile):
            raise FileNotFoundError(f"Screenshot file not found: {screenShotFile}")
        imageClip = ImageClip(
            screenShotFile,
            duration=audioClip.duration
            ).set_position(("center", "center"))
        imageClip = imageClip.resize(width=(w-marginSize))
        videoClip = imageClip.set_audio(audioClip)
        videoClip.fps = 1
        return videoClip

    # Create video clips
    print("Editing clips together...")
    clips = []
    marginSize = int(config["Video"]["MarginSize"])
    clips.append(__createClip(script.titleSCFile, script.titleAudioClip, marginSize))
    print(f"Title Screenshot: {script.titleSCFile}")

    for comment in script.frames:
        print(f"Comment Screenshot: {comment.screenShotFile}")
        clips.append(__createClip(script.titleSCFile, comment.audioClip, marginSize))

    # Merge clips into single track
    contentOverlay = concatenate_videoclips(clips).set_position(("center", "center"))

    # Compose background/foreground
    final = CompositeVideoClip(
        clips=[backgroundVideo, contentOverlay], 
        size=backgroundVideo.size).set_audio(contentOverlay.audio)
    final.duration = script.getDuration()
    final.set_fps(backgroundVideo.fps)

    # Write output to file
    print("Rendering final video...")
    bitrate = config["Video"]["Bitrate"]
    threads = config["Video"]["Threads"]
    outputFile = f"{outputDir}/{fileName}.mp4"
    final.write_videofile(
        outputFile, 
        codec='mpeg4',
        threads=threads, 
        bitrate=bitrate
    )
    print(f"Video completed in {time.time() - startTime}")

    # Preview in VLC for approval before uploading
    if config["General"].getboolean("PreviewBeforeUpload"):
        vlcPath = config["General"]["VLCPath"]
        p = subprocess.Popen([vlcPath, outputFile])
        print("Waiting for video review. Type anything to continue")
        wait = input()

    print("Video is ready to upload!")
    print(f"Title: {script.title}  File: {outputFile}")
    endTime = time.time()
    print(f"Total time: {endTime - startTime}")

if __name__ == "__main__":
    createVideo()