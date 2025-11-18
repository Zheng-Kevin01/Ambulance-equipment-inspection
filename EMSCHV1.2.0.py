from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse
import cv2
import numpy as np
import shutil
import os
import base64
from typing import List

app = FastAPI()

TEMPLATE_DIR = "templates"   # templates 資料夾（放不同設備、多張 template）
MAX_UPLOAD = 5               # 上傳上限
THRESHOLD = 0.6              # 模板比對門檻（可調整）

# -------------------------
# helper: load templates
# -------------------------
def load_templates():
    """
    讀取 templates/ 內所有圖片，
    回傳 dict: { template_name (no ext) : gray_image }
    e.g. 'aed_1' : ndarray
    """
    templates = {}
    if not os.path.exists(TEMPLATE_DIR):
        return templates
    for filename in os.listdir(TEMPLATE_DIR):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            path = os.path.join(TEMPLATE_DIR, filename)
            img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                name = os.path.splitext(filename)[0]
                templates[name] = img
    return templates

# -------------------------
# helper: encode image to base64 for HTML display
# -------------------------
def imencode_to_base64(img_bgr, ext=".jpg"):
    """
    img_bgr: BGR image (numpy)
    returns base64 string (no data: prefix)
    """
    success, encoded = cv2.imencode(ext, img_bgr)
    if not success:
        return None
    b64 = base64.b64encode(encoded.tobytes()).decode("utf-8")
    return b64

# -------------------------
# root: upload form (mobile-friendly)
# -------------------------
@app.get("/", response_class=HTMLResponse)
def index():
    return """
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>救護車設備 AI 檢查</title>
        <style>
          body { font-family: Arial, Helvetica, sans-serif; padding:20px; background:#f4f7fb; color:#111; }
          .container { max-width:720px; margin:0 auto; }
          h1 { text-align:center; margin-bottom:6px; }
          p.lead { text-align:center; color:#555; margin-top:4px; }
          .card { background:#fff; padding:18px; border-radius:10px; box-shadow:0 6px 18px rgba(18,24,40,0.08); margin-top:18px; }
          input[type=file] { width:100%; padding:8px; }
          button.primary { background:#1e88ff; color:#fff; border:none; padding:12px 18px; border-radius:8px; font-size:16px; width:100%; }
          small { color:#777; display:block; margin-top:8px; text-align:center; }
        </style>
      </head>
      <body>
        <div class="container">
          <h1>🚑 救護車設備 AI 查驗系統</h1>
          <p class="lead">請上傳車內照片（最多 5 張），系統會自動檢查 templates 資料夾內的設備</p>

          <div class="card">
            <form action="/upload" enctype="multipart/form-data" method="post">
              <input type="file" name="files" accept="image/*" multiple required>
              <br><br>
              <button class="primary" type="submit">上傳並開始檢測</button>
              <small>提示：建議每張照片包含多個設備的整體景象以提高檢測效率。</small>
            </form>
          </div>

          <div style="text-align:center; margin-top:12px; color:#666;">
            <small>Templates 資料夾：<code>templates/</code> （命名範例：<code>aed_1.jpg</code>、<code>oxygen_1.jpg</code>）</small>
          </div>
        </div>
      </body>
    </html>
    """

# -------------------------
# main upload endpoint
# -------------------------
@app.post("/upload", response_class=HTMLResponse)
async def upload(files: List[UploadFile] = File(...)):
    # 限制上傳數量
    if len(files) == 0:
        return "<h3>❌ 請上傳至少一張圖片</h3>"
    if len(files) > MAX_UPLOAD:
        return f"<h3>❌ 最多上傳 {MAX_UPLOAD} 張圖片</h3>"

    # 載入 templates
    templates = load_templates()
    if not templates:
        return "<h3>❌ templates 資料夾中沒有模板圖片，請先放入模板。</h3>"

    # 組織 templates 依設備 (以 '_' 前綴當設備群組)
    # e.g. 'aed_1' -> device 'aed'
    device_templates = {}
    for tname, timg in templates.items():
        device = tname.split("_")[0] if "_" in tname else tname
        device_templates.setdefault(device, []).append((tname, timg))

    # 處理每一張上傳圖片
    card_html = ""
    for idx, upload_file in enumerate(files, start=1):
        # 儲存上傳暫存
        tmp_path = f"uploaded_{idx}.jpg"
        with open(tmp_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)

        # 讀取彩圖與灰度圖
        img_color = cv2.imread(tmp_path, cv2.IMREAD_COLOR)
        img_gray = cv2.cvtColor(img_color, cv2.COLOR_BGR2GRAY)

        # 準備每個設備的檢測結果與紀錄最佳匹配（max_val）
        device_results = {}
        device_bestboxes = {}  # device -> (top_left, bottom_right, max_val, matched_template_name)

        for device, tlist in device_templates.items():
            best_val = -1.0
            best_loc = None
            best_tshape = None
            best_template_name = None

            for tname, timg in tlist:
                try:
                    # 如果 template 大於圖片，跳過
                    if timg.shape[0] > img_gray.shape[0] or timg.shape[1] > img_gray.shape[1]:
                        continue

                    res = cv2.matchTemplate(img_gray, timg, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

                    if max_val > best_val:
                        best_val = max_val
                        best_loc = max_loc
                        best_tshape = timg.shape
                        best_template_name = tname
                except Exception as e:
                    # 忽略某些模板可能發生的錯誤
                    continue

            # 判定是否存在（以最佳相似度判定）
            detected = best_val >= THRESHOLD
            device_results[device] = {
                "detected": bool(detected),
                "score": float(best_val) if best_val is not None else 0.0,
                "template": best_template_name
            }
            if detected and best_loc and best_tshape:
                top_left = best_loc
                h, w = best_tshape
                bottom_right = (top_left[0] + w, top_left[1] + h)
                device_bestboxes[device] = (top_left, bottom_right, best_val, best_template_name)

        # 在彩圖上畫出藍框 (BGR = (255, 0, 0))
        out_img = img_color.copy()
        for device, boxinfo in device_bestboxes.items():
            top_left, bottom_right, best_val, tname = boxinfo
            color = (255, 0, 0)  # 藍色（BGR）
            cv2.rectangle(out_img, top_left, bottom_right, color, 3)
            label = f"{device} ({best_val:.2f})"
            # put label background
            (lx, ly), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
            cv2.rectangle(out_img, (top_left[0], max(0, top_left[1]-25)), (top_left[0]+lx, top_left[1]), color, -1)
            cv2.putText(out_img, label, (top_left[0], top_left[1]-6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 2)

        # encode output image to base64 for embedding
        b64 = imencode_to_base64(out_img, ext=".jpg")
        if b64 is None:
            preview_html = "<p>無法產生預覽圖</p>"
        else:
            preview_html = f'<img src="data:image/jpeg;base64,{b64}" style="max-width:94%; border-radius:8px; box-shadow:0 6px 18px rgba(18,24,40,0.08);">'

        # build results table rows
        rows_html = ""
        # ensure consistent ordering
        for device, info in sorted(device_results.items()):
            ok = info["detected"]
            color = "#1e88ff" if ok else "#ff4d4f"  # 藍 or 紅
            status = "✔ 存在" if ok else "✘ 缺少"
            score = info.get("score", 0.0)
            tmpl = info.get("template", "")
            rows_html += f"""
            <tr>
              <td style="padding:8px 12px;">{device}</td>
              <td style="padding:8px 12px; color:{color}; font-weight:700;">{status}</td>
              <td style="padding:8px 12px;">{score:.2f}</td>
              <td style="padding:8px 12px;">{tmpl}</td>
            </tr>
            """

        # assemble card for this image
        card_html += f"""
        <div style="background:#fff; border-radius:12px; padding:14px; margin-bottom:18px; box-shadow:0 6px 18px rgba(18,24,40,0.06);">
          <div style="display:flex; gap:12px; flex-direction:column;">
            <div style="text-align:left; font-size:14px; color:#333; font-weight:700; margin-bottom:8px;">📸 圖片 {idx}: {upload_file.filename}</div>
            <div style="text-align:center;">{preview_html}</div>

            <div style="margin-top:12px; overflow:auto;">
              <table style="width:100%; border-collapse:collapse;">
                <thead>
                  <tr style="background:#f0f4ff;">
                    <th style="text-align:left; padding:10px;">設備名稱</th>
                    <th style="text-align:left; padding:10px;">檢測結果</th>
                    <th style="text-align:left; padding:10px;">相似度</th>
                    <th style="text-align:left; padding:10px;">使用模板</th>
                  </tr>
                </thead>
                <tbody>
                  {rows_html}
                </tbody>
              </table>
            </div>
          </div>
        </div>
        """

    # 最終回傳整頁 HTML（卡片式）
    html = f"""
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>檢測結果</title>
        <style>
          body {{ font-family: Arial, Helvetica, sans-serif; background:#f4f7fb; padding:18px; }}
          .container {{ max-width:920px; margin:0 auto; }}
          .topbar {{ display:flex; justify-content:space-between; align-items:center; }}
          a.button {{ background:#1e88ff; color:#fff; padding:10px 14px; border-radius:8px; text-decoration:none; }}
        </style>
      </head>
      <body>
        <div class="container">
          <div class="topbar" style="margin-bottom:18px;">
            <div><h2>🔎 檢測結果總覽</h2></div>
            <div><a class="button" href="/">⬅ 返回上傳</a></div>
          </div>
          {card_html}
          <div style="text-align:center; margin-top:18px; color:#666;">
            <small>templates 資料夾：<code>{TEMPLATE_DIR}/</code> ，Threshold：{THRESHOLD}</small>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
