from fastapi import FastAPI, Body
from fastapi.responses import JSONResponse
from env.environment import SupportEnv
from env.models import Action

app = FastAPI()
env = SupportEnv()

@app.get("/")
def root():
    return JSONResponse({
        "message": "Support Triage Environment API",
        "status": "running",
        "endpoints": {
            "reset": "GET/POST /reset",
            "step": "POST /step",
            "grade": "POST /grade",
            "docs": "/docs"
        }
    })

@app.get("/reset")
@app.post("/reset")
def reset():
    obs = env.reset()
    return JSONResponse({"observation": obs.model_dump()})

@app.post("/step")
def step(action: dict = Body(..., example={"action_type": "classify", "value": "high"})):
    try:
        # Convert dict to Action object
        action_obj = Action(
            action_type=action.get("action_type", "respond"),
            value=action.get("value", "")
        )
        # Step the environment
        result = env.step(action_obj)
        return result
    except Exception as e:
        return {"error": str(e), "observation": None, "reward": 0.0, "done": True, "info": {}}

@app.post("/grade")
def grade(task_name: str = Body(..., embed=True)):
    """
    Compute the grade for the current episode.
    
    Returns a score strictly between 0 and 1.
    """
    try:
        score = env.grade(task_name)
        return JSONResponse({
            "task": task_name,
            "score": float(score),
            "valid": 0 < score < 1
        })
    except Exception as e:
        return JSONResponse({
            "error": str(e),
            "task": task_name,
            "score": 0.01
        }, status_code=400)

def main():
    """Main entry point for running the server"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()