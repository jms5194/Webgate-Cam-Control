<img width="668" alt="Main App GUI" src="https://github.com/user-attachments/assets/018fd17e-eb93-45a2-9c5e-eb65cc4f9611">

Webgate Cam Control is a GUI interface for remote control of Webgate C1080PBM/K1080PB (and probably other) security cameras. It seems that the protocol Webgate uses is loosely based on Pelco-D, so at least the menu controls should work on other Pelco-D compatible systems. 

Before you can use this software, you need to configure your cameras for the desired baud rate and RS485 ID in the menus of the camera. Most Webgate cameras should support either 9600 or 57600 baud, so either of those are generally good choices. 

You can connect your RS485 connection directly to the Webgate camera, or use a CoC(Control over Coax) connection to the camera with a repeater/injector such as the Webgate RP102P, or the JSSD RPX8. 

The UI is generally self-explanatory- you select an interface (on MacOS this will be usually be listed as something like /dev/cu.usbserial if you are using a USB-RS485 adaptor). I've had plenty of luck on MacOS with the D-Tech USB-Serial adaptor. 

<a href="https://www.amazon.com/gp/product/B0195ZD3P4/ref=ppx_yo_dt_b_search_asin_title?ie=UTF8&psc=1">D-Tech USB Serial Adaptor</a>

Then you select a baud rate, and a camera ID. Pressing enter will bring up the OSD on the selected camera's output. 

You can name your cameras via the preferences window:

<img width="351" alt="Preferences UI Window" src="https://github.com/user-attachments/assets/13839ef6-49f5-4fbe-ba62-32886d304b6e">

And that's about it. 


