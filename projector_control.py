import dearpygui.dearpygui as dpg
import configparser
from pypjlink import Projector

#config 

def read_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

projector_count = read_config()['General']['BeamerCount']
power_on_startup = read_config()['General']['autostartbeamers']


def change_power(sender, app_data, user_data):
    beamer, state = user_data.split("+")
    with Projector.from_address(read_config()[f'{beamer}']['addr']) as projector:
        projector.authenticate(read_config()[f'{beamer}']['password'])
        projector.set_power(state)


def power_switch_all(sender, app_data, user_data):
    for x in range(int(projector_count)):
        change_power(sender, app_data, f'Beamer{str(x+1)}+{user_data}')


def check_power_status():
    for x in range(int(projector_count)):
        try:
            with Projector.from_address(read_config()[f'Beamer{str(x+1)}']['addr']) as projector:
                projector.authenticate(read_config()[f'Beamer{str(x+1)}']['password'])
                dpg.set_value(f"status{x+1}", projector.get_power())
        except TimeoutError:
            dpg.set_value(f"status{x+1}", "offline")

dpg.create_context()
dpg.create_viewport(title='projector control', width=540, height=300)

for x in range(int(projector_count)):
    with dpg.window(label=f"beamer {str(x+1)}", pos=(130*x,0)):
        dpg.add_text("power status: ")
        dpg.add_text(label=f"status{x+1}", default_value="offline", tag=f"status{x+1}")
        dpg.add_button(label="power on", callback=change_power, user_data=f'Beamer{str(x+1)}+on')
        dpg.add_button(label="power off", callback=change_power, user_data=f'Beamer{str(x+1)}+off')

with dpg.window(label="all beamers", pos=(0,130)):
    dpg.add_button(label="power on", callback=power_switch_all, user_data="on")
    dpg.add_button(label="power off", callback=power_switch_all, user_data="off")


if power_on_startup == "True":
    power_switch_all('', '', user_data='on')
    


dpg.setup_dearpygui()
dpg.show_viewport()

frame_count = 0
while dpg.is_dearpygui_running():
    # insert here any code you would like to run in the render loop
    # you can manually stop by using stop_dearpygui()
    if frame_count == 300:
        frame_count = 0
        check_power_status()
    frame_count += 1
    dpg.render_dearpygui_frame()


dpg.destroy_context()
