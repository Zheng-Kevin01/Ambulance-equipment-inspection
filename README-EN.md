# Ambulance and Fire truck Equipment Inspection System By Z.W.Y

[ZH Taiwan](README.md) [EN]

---Latest Version V1.5.0---

The purpose of this system is to assist local government or private emergency medical services units in Taiwan in implementing systematic equipment management and optimizing the convenience of regular inspections. Future development will continue to include cloud and mobile device applications.

# Preparation

Please install a Python development environment first.
Install Packages: !pip install fastapi uvicorn python-multipart paddleocr opencv-python
Please first confirm your local Wi-Fi IPv4 address -- CMD [ipconfig] -- 
Ensure your mobile device is connected to the same Wi-Fi network as the server.

1. Create a folder on the desktop: C:\Users\user\Desktop\NAME

2. Create a folder named [templates] in the folder and load the image: C:\Users\user\Desktop\NAME\templates

3. Use WIN+R to open the command prompt (cmd), specify the target folder: [cd] to specify the project folder address

[cd cd Desktop\NAME] [To confirm whether to switch, type dir to confirm the directory]

4. Start the local server:
  [uvicorn NAME:app --host 0.0.0. --reload] or
  
  [uvicorn main:app --host 0.0.0.0 --port 8000]
  
--System Webpage-- [http://127.0.0.1:8000]

5. Stop the server: [Ctrl+C] 

# Program Operation

--Mobile Devices-- http://192.168.xxx.xxx:8000

--Local end--  http://127.0.0.1:8000  

# Update Log

--V1.2.0 Update Notes--

1. UI interface optimization

2. Added more photo uploads and consolidated reference photos into folders

--V1.5.0 Update Notes--

1. Mobile devices can now connect to this system from within the same local area network.

2. UI interface optimization

3. Added unit/personnel login settings and vehicle selection


# For any questions or further details, please contact us via 
E-MAIL: zheng.wan.yi.kavin@gmail.com

--This program only supports Traditional Chinese version--

!!This program is prohibited for commercial or profit-making purposes!!
