from os import rename, remove, path
from download import download
from pathHelper import *
from subprocessHelper import *
import subprocess, random


loglevel = "error"

def getDur(f):
	return eval(subprocess.getoutput(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", f]))

def autotune(base, over, filename, strength = 75, reformatAudio = True, hz = 48000):
	strength = max(1, min(strength, 512))
	if reformatAudio:
		baseDur = getDur(base)
		loud_run(["ffmpeg", "-y", "-hide_banner", "-loglevel", loglevel, "-i", base, "-ac", "1", "-ar", hz, base := chExt(addPrefix(absPath(base), 'AT_'), 'wav')])
		loud_run(["ffmpeg", "-y", "-hide_banner", "-loglevel", loglevel, "-i", over, "-ac", "1", "-ar", hz, '-t', str(baseDur), over := chExt(addPrefix(absPath(over), 'AT_'), 'wav')])
	silent_run(["autotune.exe", '-b', strength, base, over, filename])
	if reformatAudio:
		remove(base)
		remove(over)

randDigits = lambda: str(random.random()).replace('.', '') 

def autotuneURL(filename, URL, replaceOriginal = True):
	directory = path.split(path.abspath(filename))[0]
	downloadName = f"{directory}/download_{randDigits()}.wav"
	result = download(downloadName, URL, video = False, duration = 2 * 60)
	if result:
		wavName = f'{directory}/vidAudio_{randDigits()}.wav'
		loud_run(["ffmpeg", "-hide_banner", "-loglevel", loglevel, "-i", filename, "-ac", "1", wavName])
		autotuneName = f'{directory}/autotune_{randDigits()}.wav'
		autotune(wavName, downloadName, autotuneName)
		remove(downloadName)
		remove(wavName)
		exportName = f"{directory}/{randDigits()}{path.splitext(filename)[1]}"
		loud_run(["ffmpeg", "-hide_banner", "-loglevel", loglevel, "-i", filename, "-i", autotuneName, "-map", "0:v", "-map", "1:a", "-ac", "1", exportName])
		remove(autotuneName)
		if replaceOriginal:
			remove(filename)
			rename(exportName, filename)
			return filename
		return exportName
	else:
		return [f"Error downloading {URL}"]