from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
import cv2
import numpy as np
import shutil
import os
import base64

app = FastAPI()

TEMPLATE_DIR = "templates"   # 模板資料夾


@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
        <head>
            <title>救護車設備AI查驗平台</title>
        </head>
        <body style="font-family:Arial; text-align:center; padding-top:50px;">

            <h1>救護車設備 AI 查驗系統</h1>
            <p>請上傳車內設備照片,透過AI系統偵測各設備是否存在</p>

            <form action="/upload" enctype="multipart/form-data" method="post">
                <input type="file" name="file" accept="image/*" required>
                <br><br>
                <button type="submit" 
                        style="padding:10px 20px; font-size:16px;">
                    上傳並開始偵測
                </button>
            </form>

        </body>
    </html>
    """


def load_templates():
    """讀取 templates/ 內所有模板圖片"""
    templates = {}
    for filename in os.listdir(TEMPLATE_DIR):
        if filename.lower().endswith((".jpg", ".png", ".jpeg")):
            path = os.path.join(TEMPLATE_DIR, filename)
            img = cv2.imread(path, 0)
            if img is not None:
                name = os.path.splitext(filename)[0]
                templates[name] = img
    return templates


@app.post("/upload", response_class=HTMLResponse)
async def upload(file: UploadFile = File(...)):
    upload_path = "uploaded.jpg"
    with open(upload_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 讀取上傳影像
    img = cv2.imread(upload_path, 0)
    if img is None:
        return "<h2>❌ 上傳圖片讀取失敗</h2>"

    # 載入所有模板
    templates = load_templates()
    if not templates:
        return "<h2>❌ templates 資料夾無模板！</h2>"

    results = {}
    threshold = 0.6

    # 模板比對
    for name, template in templates.items():
        try:
            result = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            loc = np.where(result >= threshold)
            detected = len(loc[0]) > 0
        except:
            detected = False

        results[name] = detected

    # 將上傳圖片轉成 base64 以在 HTML 顯示
    with open(upload_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode("utf-8")

    # 建立設備結果表格
    table_rows = ""
    for name, ok in results.items():
        color = "green" if ok else "red"
        status = "✔ 存在" if ok else "✘ 缺少"
        table_rows += f"""
            <tr>
                <td>{name}</td>
                <td style="color:{color}; font-weight:bold;">{status}</td>
            </tr>
        """

    # 回傳結果頁面
    return f"""
    <html>
        <head>
            <title>AI 檢測結果</title>
        </head>
        <body style="font-family:Arial; padding:40px;">

            <h1>🔍 檢測結果</h1>

            <h3>📸 上傳的圖片：</h3>
            <img src="data:image/jpeg;base64,{encoded}" 
                 style="max-width:400px; border:1px solid #aaa;">

            <h3 style="margin-top:40px;">📋 設備檢測</h3>

            <table border="1" cellpadding="10" 
                style="border-collapse:collapse; margin:auto; min-width:300px;">
                <tr>
                    <th>設備名稱</th>
                    <th>檢測結果</th>
                </tr>
                {table_rows}
            </table>

            <br><br>
            <a href="/" style="font-size:18px;">⬅ 返回上傳頁面</a>

        </body>
    </html>
    """
