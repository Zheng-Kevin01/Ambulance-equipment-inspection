--ZH　Taiwan --
# 救護車和消防車設備巡檢系統 By Z.W.Y 

---最新版本 V1.5.0---

本系統開發目的為協助臺灣本地政府救護單位或民間救護單位,執行器材系統化管理及優化定期巡檢便利性,未來將持續開發同步到雲端及行動裝置應用端

# 前置作業

請先安裝可運行Python之開發環境
安裝套件!pip install fastapi uvicorn python-multipart paddleocr opencv-python
請先確認本地WIFI IPv4位址 -- CMD [ipconfig] --
確保行動裝置端連接和伺服器相同的WIFI



1.於桌面創建一個資料夾C:\Users\user\Desktop\NAME

2.在資料夾中創建[templates]並載入資料圖片C:\Users\user\Desktop\NAME\templates

3.使用WIN+R呼叫命令單元cmd,指定目標資料夾[cd]指定專案資料夾位址
[cd cd Desktop\NAME][若要確認是否切換可輸dir確認目錄]

4.啟動本地端伺服器[uvicorn NAME:app --host 0.0.0. --reload] 

5.中止伺服器 [ Ctrl+C ]

# 程式運轉

--行動裝置端--http://192.168.xxx.xxx:8000

--本地端-- http://127.0.0.1:8000

# 更新日誌

V1.2.0更新內容 

1.UI介面優化

2.新增更多相片上傳,參考資料相片資料夾化

--V1.5.0更新內容-- 

1.行動裝置端可於同局域網內連線上本系統

2.UI介面優化

3.新增單位/人員登入設置及車輛選擇


# 若有未詳盡事項或疑問歡迎聯絡
E-MAIL zheng.wan.yi.kavin@gmail.com

--本程式僅支援繁體中文版--

!!本程式禁止營利及商業用途!!



--EN--
# Ambulance and Fire truck Equipment Inspection System By Z.W.Y

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

4. Start the local server: [uvicorn NAME:app --host 0.0.0. --reload]

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
