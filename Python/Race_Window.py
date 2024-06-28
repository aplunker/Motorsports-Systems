# Wyoming Motorsports | University of Wyoming Department of Computer Science
# Austin Plunekrt | Luke Stevens | Derek Walton
# Spring 2024
# Python 3.11
# Dependencies:
#     pip install dearpygui
# 
# ToDo:

import serial
import serial.tools.list_ports
import pynmea2 
from geopy.distance import geodesic
from datetime import datetime, time

# main function
def Race_Window(dpg, shift_point, font_resolution):
    throttle_position = 0
    battery_heat = 0
    ice_heat = 0
    charge_level = 0
    GLV_charge = 0
    gear = 0
    try:
        for pinfo in serial.tools.list_ports.comports():
            if 'Serial Port' in pinfo.description:
                print("Arduino is in " + pinfo.device)
                arduinoCom = pinfo.device
            if 'Serial Device' in pinfo.description:
                print("GPS is in " + pinfo.device)
                GPSCom = pinfo.device
        GPS = serial.Serial(port=GPSCom, baudrate=4800, timeout=1)
        arduino = serial.Serial(port=arduinoCom, baudrate=9600, timeout=.1) 
    except:
        print("USB COM FAILURE")
        return 0
    latitude1 = "NA"
    latitude2 = "NA"
    longitude1 = "NA"
    longitude2 = "NA"
    time1 = "NA"
    time2 = "NA"
    #rect variables
    rpm = 0
    #speed variable 
    mph = 0
    string_mph = "000"
    # other variables
    height = dpg.get_viewport_height()
    width = dpg.get_viewport_width()
    width_border = width*0.075
    bar_height = height/8

    # draw the dashes for the rpm box
    def draw_dashes():
        dashes = []
        for i in range(0, shift_point+1, 1):
            dash_point = width*(i/shift_point)
            if(dash_point == width):
                dash_point -= 2
            elif(dash_point == 0):
                dash_point = 2
            dash_end = 0
            dash_start = bar_height + bar_height/2
            dashes.append(dpg.draw_line((dash_point, dash_start), (dash_point, dash_end), color=(255, 255, 255, 255), thickness=4, parent="Window"))
        # dashes.append(dpg.draw_line((width*0.7, height/4.2), (width*0.7, height/1.5), color=(255, 255, 255, 255), thickness=8, parent="Window"))
        return dashes
    # draw the rpm box
    def draw_rpm():
        # current functionality only goes into last bar when over threshold, meaning we are over the shift point
        bar_width = width*((int)(rpm*shift_point)/shift_point)
        upper_left = [0, 0]
        lower_right = [upper_left[0] + bar_width, upper_left[1] + bar_height]
        color = (255*(pow(rpm,2.5)), 255*(1-pow(rpm,2.5)), 0, 255)
        return dpg.draw_rectangle(upper_left, lower_right, color=color, fill=color, parent="Window")
    # draw the numbers, so speed
    def draw_numbers():
        upper_left_y = height/8
        upper_left_x = (width/4.77)
        dpg.delete_item(dpg.get_alias_id("speed"))
        dpg.add_text(default_value=string_mph,tag="speed",pos=[upper_left_x,upper_left_y], parent="Window")
        dpg.bind_item_font(font=dpg.get_alias_id("vera_bold"), item=dpg.get_alias_id("speed"))
        # upper_left_x = (width/1.4)
        # dpg.delete_item(dpg.get_alias_id("gear"))
        # dpg.add_text(default_value=string_mph,tag="gear",pos=[upper_left_x,upper_left_y], parent="Window")
        # dpg.bind_item_font(font=dpg.get_alias_id("vera_bold"), item=dpg.get_alias_id("gear"))
    def draw_heats():
        upper_left_y = height/1.2
        upper_left_x = width/4
        radius = height/16
        color = (255*battery_heat, 255*(1-battery_heat), 0, 255)
        heats = []
        heats.append(dpg.draw_circle(tag="battery_heat",center=[upper_left_x,upper_left_y], parent="Window",fill=color,color=color, radius=radius))
        heats.append(dpg.add_text(parent="Window", pos=(upper_left_x - radius - 17, upper_left_y - radius*2), default_value="Bat heat", tag="Bat heat text"))
        dpg.bind_item_font(font=dpg.get_alias_id("vera_normal"), item=dpg.get_alias_id("Bat heat text"))
        upper_left_x = width - (width/4)
        color = (255*ice_heat, 255*(1-ice_heat), 0, 255)
        heats.append(dpg.draw_circle(tag="ice_heat",center=[upper_left_x,upper_left_y], parent="Window",fill=color,color=color, radius=radius))
        heats.append(dpg.add_text(parent="Window", pos=(upper_left_x - radius - 17, upper_left_y - radius*2), default_value="ICE heat", tag="Ice heat text"))
        dpg.bind_item_font(font=dpg.get_alias_id("vera_normal"), item=dpg.get_alias_id("Ice heat text"))
        return heats
    
    draw_numbers() # draw before to instaciate numbers


    # render loop for the GUI
    while dpg.is_dearpygui_running():
        # stop by using stop_dearpygui()
        #MPH code
        # check if port is ready for new data. Avoid getting hung up on readline
        if GPS.in_waiting > 0:
            # Read a line of data from the GPSial port
            line = GPS.readline().decode(encoding='utf-8', errors='ignore').strip()

            # Check if the line is a valid NMEA sentence
            if line.startswith('$GPGGA'):
                try:
                    # Parse the NMEA sentence
                    msg = pynmea2.parse(line)
                    print(msg)
                    if(str(msg).split(",")[6] == "0"):
                        print("GPS has no signal")
                    else:
                        # Extract GPS data
                        latitude1 = msg.latitude
                        longitude1 = msg.longitude
                        time1 = float(str(msg).split(",")[1])
                        if(latitude2 != "NA" and longitude2 != "NA" and time2 != "NA"):
                            # Calculate distance between two positions (in meters)
                            distance = geodesic((latitude1, longitude1), (latitude2, longitude2)).meters
                            # Calculate time difference (in seconds)
                            time_difference = time1 - time2
                            # Calculate speed
                            mph = round(abs((distance / time_difference) * 2.23694))
                        time2 = time1
                        longitude2 = longitude1
                        latitude2 = latitude1
                except:
                    print("GPS error")
        if arduino.in_waiting > 0:
            line = arduino.readline().decode(encoding='ascii', errors='ignore').strip()
            print(line)
            try:
                # upper and lower bounds will be defined soon
                throttle_position = (float(str(line).split(",")[0]) - 1)/2.1
                if(throttle_position < 0):
                    throttle_position = 0
                ice_heat = float(str(line).split(",")[1])
                if(ice_heat >= 4.05):
                    ice_heat = 1
                elif(ice_heat >= 3.95):
                    ice_heat = 0.5
                else:
                    ice_heat = 0
                rpm = (float(str(line).split(",")[2])/1000)/shift_point
                charge_level = (float(str(line).split(",")[3]))/5
                GLV_charge = (float(str(line).split(",")[4]) - 10)/4.5
                if(GLV_charge < 0):
                    GLV_charge = 0
                mode_switch = int(str(line).split(",")[5])
                if(mode_switch == 1):
                    return 1
            except:
                print("arduino error")
        # set scale so the numbers are 2/3 the hight of the screen
        dpg.set_global_font_scale((height*(2/3))/font_resolution) 
        # pad mph so it is always three didgits
        if(mph<10):
            string_mph = "00" + str(mph)
        elif(mph<100):
            string_mph = "0" + str(mph)
        else:
            string_mph = str(mph)
        # string_gear = str(gear)
        # if the screen changes size (happens in first couple of frames for some reason) 
        if(width != dpg.get_viewport_width() or height != dpg.get_viewport_height()):
            return 0
        else:
            #update the speed, size didnt change so no re draw
            dpg.set_value("speed", string_mph)
            # dpg.set_value("gear", string_gear)
        # draw rpm bar
        rpm_bar = draw_rpm()
        # draw dahses for rpm bar
        dashes = draw_dashes()
        # draw heat circles
        heats = draw_heats()
        # render the frame
        dpg.render_dearpygui_frame() 
        # delete all the stuff drawn every frame
        dpg.delete_item(rpm_bar)
        for dash in dashes:
            dpg.delete_item(dash)
        for heat in heats:
            dpg.delete_item(heat)

    dpg.destroy_context()
