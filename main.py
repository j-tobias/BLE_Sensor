from fastapi import FastAPI
import json



app = FastAPI()





@app.post("/update_config/")
async def update_config(data: dict):
    
    with open("CONFIG.json", mode = "W") as f:
        json.dump(data, f)


@app.get("/get_config/")
def get_config ():
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

    ip = "10.220.9.76"
    port_n = 5000
    
    uvicorn.run(app, host=ip, port=port_n)
