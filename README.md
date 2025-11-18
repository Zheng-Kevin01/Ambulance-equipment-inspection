# 救護車和消防車設備巡檢系統 By Z.W.Y 

[ZH Taiwan]  [EN](READMEEN.md)

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
