ZH　Taiwan 
# AI救護車設備巡檢系統 --本地端-- V1.0    By Z.W.Y 

本系統開發目的為協助臺灣本地政府救護單位或民間救護單位,執行器材系統化管理及優化定期巡檢便利性,未來將持續開發同步到雲端及行動裝置應用端

--前置作業--
請先安裝可運行Python之開發環境
安裝套件!pip install fastapi uvicorn python-multipart paddleocr opencv-python


1.於桌面創建一個資料夾C:\Users\user\Desktop\NAME

2.在資料夾中創建[templates]並載入資料圖片C:\Users\user\Desktop\NAME\templates

3.使用WIN+R呼叫命令單元cmd,指定目標資料夾[cd]指定專案資料夾位址
[cd cd Desktop\NAME][若要確認是否切換可輸dir確認目錄]

4.啟動本地端伺服器[uvicorn NAME:app --reload] 

--系統網頁--[http://127.0.0.1:8000]

5.中止伺服器 [ Ctrl+C ]

--本程式僅支援繁體中文版--

若有未詳盡事項或疑問歡迎聯絡
E-MAIL zheng.wan.yi.kavin@gmail.com

!!本程式禁止營利及商業用途!!


EN
# AI Ambulance Equipment Inspection System --Local Server-- V1.0 By Z.W.Y

The purpose of this system is to assist local government or private emergency medical services units in Taiwan in implementing systematic equipment management and optimizing the convenience of regular inspections. Future development will continue to include cloud and mobile device applications.

--Preparation-- Please install a Python development environment first.
Install Packages: !pip install fastapi uvicorn python-multipart paddleocr opencv-python

1. Create a folder on the desktop: C:\Users\user\Desktop\NAME

2. Create a folder named [templates] in the folder and load the image: C:\Users\user\Desktop\NAME\templates

3. Use WIN+R to open the command prompt (cmd), specify the target folder: [cd] to specify the project folder address

[cd cd Desktop\NAME] [To confirm whether to switch, type dir to confirm the directory]

4. Start the local server: [uvicorn NAME:app --reload]

--System Webpage-- [http://127.0.0.1:8000]

5. Stop the server: [Ctrl+C] 

--This program only supports Traditional Chinese version--

For any questions or further details, please contact us via email: zheng.wan.yi.kavin@gmail.com

!!This program is prohibited for commercial or profit-making purposes!!
