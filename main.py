from fastapi import FastAPI, UploadFile, File
from typing import List, Dict

app = FastAPI()

# Store scenes in memory
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

@app.get("/all_scenes/")
def get_all_scenes():
    all_scenes = []
    for file in sorted(scene_store.keys()):
        for scene in scene_store[file]:
            all_scenes.append({
                "file": file,
                "title": scene["title"],
                "content": scene["content"]
            })
    return {"scenes": all_scenes}
