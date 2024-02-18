from fastapi import FastAPI
import json



app = FastAPI()





@app.post("/update_config/")
async def update_config(data: dict):
    
    with open("CONFIG.json", mode = "w+") as f:
        json.dump(data, f)


@app.get("/get_config/")
async def get_config ():
    """
    return the current config file
    """
    with open("CONFIG.json", mode = "r") as f:
        config = json.load(f)

    return config




if __name__ == "__main__":
    import uvicorn
    import subprocess

    subprocess.Popen(["python", "scanner.py"])

    ip = "0.0.0.0" 
    port_n = 5000
    
    uvicorn.run(app, host=ip, port=port_n)
