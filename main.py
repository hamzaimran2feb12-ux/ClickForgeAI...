from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
import subprocess, uuid, re, os

app=FastAPI(title="ClipForge AI", version="0.9.0")
BASE=Path(__file__).resolve().parent
UPLOADS=BASE/"uploads"; OUTPUTS=BASE/"outputs"
UPLOADS.mkdir(exist_ok=True); OUTPUTS.mkdir(exist_ok=True)
MAX_BYTES=250*1024*1024
ALLOWED={".mp4",".mov",".mkv",".webm"}

def ffmpeg_check():
    for tool in ("ffmpeg","ffprobe"):
        if not shutil_which(tool): raise HTTPException(503, f"{tool} is not installed on the server")
def shutil_which(name):
    import shutil; return shutil.which(name)

@app.get("/health")
def health():
    return {"ok":True,"service":"ClipForge AI"}

@app.get("/",response_class=HTMLResponse)
def home():
    return (BASE.parent/"web"/"index.html").read_text(encoding="utf-8")

@app.get("/manifest.json")
def manifest():
    return FileResponse(BASE.parent/"manifest.json",media_type="application/manifest+json")

@app.post("/api/clips")
async def make_clips(video:UploadFile=File(...)):
    ffmpeg_check()
    ext=Path(video.filename or "video.mp4").suffix.lower()
    if ext not in ALLOWED: raise HTTPException(400,"Unsupported video type. Use MP4, MOV, MKV or WebM.")
    src=UPLOADS/(uuid.uuid4().hex+ext)
    size=0
    try:
        with src.open("wb") as f:
            while True:
                chunk=await video.read(1024*1024)
                if not chunk: break
                size+=len(chunk)
                if size>MAX_BYTES: raise HTTPException(413,"Upload exceeds 250 MB limit.")
                f.write(chunk)
        probe=subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","default=noprint_wrappers=1:nokey=1",str(src)],capture_output=True,text=True,timeout=60)
        if probe.returncode: raise HTTPException(400,"Unable to read video. Please try a valid video file.")
        duration=float(probe.stdout.strip())
        if duration<8: raise HTTPException(400,"Video must be at least 8 seconds long.")
        # Select three evenly distributed candidate windows (starter heuristic, not trained AI).
        seg=min(45,max(12,duration/4)); count=min(3,max(1,int(duration//8)))
        starts=[max(0,(duration-seg)*i/(count-1)) for i in range(count)] if count>1 else [0]
        result=[]
        for i,start in enumerate(starts):
            name=f"{src.stem}_clip{i+1}.mp4"; dest=OUTPUTS/name
            cmd=["ffmpeg","-hide_banner","-loglevel","error","-y","-ss",str(start),"-i",str(src),"-t",str(seg),"-vf","scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920","-c:v","libx264","-preset","veryfast","-crf","23","-c:a","aac","-b:a","128k","-movflags","+faststart",str(dest)]
            r=subprocess.run(cmd,capture_output=True,timeout=900)
            if r.returncode==0 and dest.exists(): result.append({"name":name,"url":"/api/download/"+name,"start":round(start,2),"duration":round(seg,2)})
        if not result: raise HTTPException(500,"Clip export failed. Check server logs and FFmpeg installation.")
        return {"clips":result,"note":"Export complete. Candidate moments were selected using a simple time-distribution heuristic; AI highlight ranking and captioning are not yet enabled."}
    finally:
        src.unlink(missing_ok=True)

@app.get("/api/download/{filename}")
def download(filename:str):
    if not re.fullmatch(r"[A-Za-z0-9_.-]+",filename): raise HTTPException(400,"Invalid filename")
    path=OUTPUTS/filename
    if not path.exists() or path.parent!=OUTPUTS: raise HTTPException(404,"Clip not found")
    return FileResponse(path,media_type="video/mp4",filename=filename)
