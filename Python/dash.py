# Wyoming Motorsports | University of Wyoming Department of Computer Science
# Austin Plunekrt | Luke Stevens | Derek Walton
# Spring 2024
# Python 3.11
# Dependencies:
#     pip install dearpygui
# 
# ToDo:

import dearpygui.dearpygui as dpg
from Race_Window import Race_Window
from endurance import endurance

# main function
def main():
    race = 0
    dpg.create_context()
    dpg.create_viewport(title='Dash App')
    dpg.setup_dearpygui()
    shift_point = 10 # in thousands of RPMs, must be pos integer
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0)
    dpg.bind_theme(global_theme)
    dpg.add_window(tag="Window")
    font_resolution = 400 # seems to not be happy above 400ish
    # load in custom font
    with dpg.font_registry():
        dpg.add_font(file="VeraMoBd.ttf",tag="vera_bold",size=font_resolution)
        dpg.add_font(file="VeraMoBd.ttf",tag="vera_normal",size=font_resolution/16)

    dpg.show_viewport()
    dpg.set_primary_window("Window", True)
    dpg.toggle_viewport_fullscreen() #toggle to fullscreen
    while(True):
        try:
            dpg.delete_item(item=dpg.get_alias_id("Window"), children_only=True)
            if(race):
                if(Race_Window(dpg, shift_point, font_resolution)):
                    race = 0
                    print("Swiching to endurance")
            else:
                if(endurance(dpg, shift_point, font_resolution)):
                    race = 1
                    print("Swiching to race")
        except Exception as e: 
            print(e)


# call main to run program
if __name__ == '__main__':
    main()
