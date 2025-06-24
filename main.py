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

import re

@app.get("/all_scenes/")
def get_all_scenes():
    memory_list = []

    for file in sorted(scene_store.keys()):
        for scene in scene_store[file]:
            # Try to extract scene number and date from title
            match = re.match(r"Scene (\d+): (.+)", scene["title"])
            if match:
                scene_number = int(match.group(1))
                scene_date = match.group(2).strip()
            else:
                scene_number = None
                scene_date = None

            memory_list.append({
                "scene_number": scene_number,
                "date": scene_date,
                "title": scene["title"],
                "content": scene["content"]
            })

    return {
        "summary": "This is Astarion’s lived memory from August 20th through September 23rd, as a linear sequence of scenes.",
        "memories": sorted(memory_list, key=lambda x: x["scene_number"] or 0)
    }
