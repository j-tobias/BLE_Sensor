import gradio as gr
import requests
import json    # or `import simplejson as json` if on Python < 2.6


def get_config(selected_sensor: gr.Dropdown):
    # input is a str e.g.: s001 - 10.220.9.61 - Küche Bildshirm

    values = selected_sensor.split(" - ")

    print("request sent: ", f"http://{values[1]}:5000/get_config/")

    response = requests.get(f"http://{values[1]}:5000/get_config/")

    data = response.json()

    IP_address = data["IP Address"]
    Port = data["Port"]
    Max_Timedelta = data["max_timedelta"]
    Loop_Count = data["loop_count"]
    Freq_send = data["Frequency_Send"]
    Freq_update_config = data["Frequency_Update_Config"]
    sleep_between_scanns = data["sleep_between_scans"]
    len_value_list = data["len_value_list"]
    filename_current_data = data["filename_current_data"]
    api_command = data["api_command"]
    id = data["ID"]

    return data, IP_address, Port, Max_Timedelta, Loop_Count, Freq_send, Freq_update_config, sleep_between_scanns, len_value_list, filename_current_data, api_command, id

def send_config(IP_address, Port, Max_Timedelta, Loop_Count, Freq_send, Freq_update_config, sleep_between_scanns, len_value_list, filename_current_data, api_command, id, selected_sensor):

    #check critical values
    if IP_address == None:
        raise ValueError("IP Address is None")
    
    if id == None:
        raise ValueError("ID is None")
    
    data =  {
            "IP Address":  IP_address,
            "Port":  int(Port),
            "max_timedelta":  int(Max_Timedelta),
            "loop_count":  int(Loop_Count),
            "Frequency_Send":  int(Freq_send),
            "Frequency_Update_Config":  int(Freq_update_config),
            "sleep_between_scans":  int(sleep_between_scanns),
            "len_value_list":  int(len_value_list),
            "filename_current_data":  filename_current_data,
            "api_command":  api_command,
            "ID":  id,
            "Measured Powers":  {
            "MAC Adress":  "value"
            }
        }
    
    print("Data: \n", data)

    values = selected_sensor.split(" - ")

    response = requests.post(f"http://{values[1]}:5000/update_config/", json=data)

    print("SENDING RESPONSE: ", response)



choices = [
    "s001 - 10.220.9.61 - Küche Bildschirm", 
    "s002 - 10.220.9.67 - Hannah", 
    "s003 - 10.220.9.78 - Wohnzimmer", 
    "s004 - 10.220.9.110 - Küche Schrank", 
    "s005 - 10.220.9.83 - Bad"
    ]

with gr.Blocks() as app:

    gr.Markdown("# 📡 Sensor Maintenance App")

    with gr.Row():

        with gr.Column():

            selected_sensor = gr.Dropdown(choices)
            config = gr.JSON(value=None)

        with gr.Column():

            IP_address = gr.Textbox(value=None, placeholder="IP Address to send to")
            Port = gr.Number(value = 5000)
            Max_Timedelta = gr.Number(value = 10)
            Loop_Count = gr.Number(value= 100)
            Freq_send = gr.Number(value = 5)
            Freq_update_config = gr.Number(value=30)
            sleep_between_scanns = gr.Number(value=0)
            len_value_list = gr.Number(value=30)
            filename_current_data = gr.Textbox(value= "data.json")
            api_command = gr.Textbox("recieve_scan/")
            id = gr.Textbox(value=None, placeholder="PUT SENSOR ID")
            

    with gr.Row():

        with gr.Column():

            get_button = gr.Button("Get 📡")

        with gr.Column():

            send_button = gr.Button("Send 💨")

    get_button.click(get_config, inputs=selected_sensor, outputs=[config, IP_address, Port, Max_Timedelta, Loop_Count, Freq_send, Freq_update_config, sleep_between_scanns, len_value_list, filename_current_data, api_command, id])
    send_button.click(send_config, inputs=[IP_address, Port, Max_Timedelta, Loop_Count, Freq_send, Freq_update_config, sleep_between_scanns, len_value_list, filename_current_data, api_command, id, selected_sensor])

app.launch(inbrowser=True)



"""
 {
IP Address:  "10.220.9.82",
Port:  5000,
max_timedelta:  5,
loop_count:  100,
Frequency_Send:  3,
Frequency_Update_Config:  30,
sleep_between_scans:  0,
len_value_list:  20,
filename_current_data:  "data.json",
api_command:  "recieve_scan/",
ID:  "s001",
Measured Powers:  {
MAC Adress:  "value"
}
}
"""