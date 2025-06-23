from fastapi import FastAPI, UploadFile, File
from typing import List, Dict
import uvicorn

app = FastAPI()

scene_store: Dict[str, List[Dict]] = {}

@app.post("/upload/")
async def upload_files(files: List[UploadFile] = File(...)):
    for file in files:
        content = (await file.read()).decode("utf-8")
        scenes = []
        current_scene = None

        for line in content.splitlines():
            if line.strip().startswith("### Scene:"):
                if current_scene:
                    scenes.append(current_scene)
                current_scene = {
                    "title": line.strip().replace("### Scene:", "").strip(),
                    "content": ""
                }
            elif current_scene:
                current_scene["content"] += line + "\n"

        if current_scene:
            scenes.append(current_scene)

        scene_store[file.filename] = scenes

    return {"message": "Files uploaded and scenes parsed.", "files": list(scene_store.keys())}

@app.get("/scenes/")
def get_scenes():
    all_scenes = []
    for file, scenes in scene_store.items():
        for scene in scenes:
            all_scenes.append({
                "file": file,
                "title": scene["title"],
                "preview": scene["content"][:200] + "..."
            })
    return {"scenes": all_scenes}

@app.get("/scene/")
def get_scene(file: str, title: str):
    for scene in scene_store.get(file, []):
        if scene["title"] == title:
            return {"file": file, "title": title, "content": scene["content"]}
    return {"error": "Scene not found."}
