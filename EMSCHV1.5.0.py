# EMSCH V1.5.0.py
from fastapi import FastAPI, UploadFile, File, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import cv2
import numpy as np
import shutil
import os
import base64
from typing import List
import json
import sqlite3
from datetime import datetime

app = FastAPI()

# ========== config ==========
TEMPLATE_DIR = "templates"
MAX_UPLOAD = 5
THRESHOLD = 0.6
SESSION_SECRET = "PLEASE_CHANGE_THIS_RANDOM_SECRET"
DB_PATH = "records.db"
# ============================

# add session middleware
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)


# ---------- database ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            division TEXT,
            username TEXT,
            vehicle_type TEXT,
            vehicle_id TEXT,
            results TEXT
        )
        """
    )
    conn.commit()
    conn.close()


def save_record(division, username, vehicle_type, vehicle_id, results_dict):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO records (timestamp, division, username, vehicle_type, vehicle_id, results) VALUES (?, ?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), division, username, vehicle_type, vehicle_id, json.dumps(results_dict, ensure_ascii=False))
    )
    conn.commit()
    conn.close()


def get_recent_records(limit=50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, timestamp, division, username, vehicle_type, vehicle_id, results FROM records ORDER BY id DESC LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


# ---------- helper functions ----------
def load_templates():
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


def imencode_to_base64(img_bgr, ext=".jpg"):
    success, encoded = cv2.imencode(ext, img_bgr)
    if not success:
        return None
    b64 = base64.b64encode(encoded.tobytes()).decode("utf-8")
    return b64


# ---------- routes ----------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if request.session.get("user"):
        return RedirectResponse(url="/upload_form")

    divisions = ["北屯分隊", "南屯分隊", "太平分隊", "清水分隊"]
    options_html = "".join([f"<option value='{d}'>{d}</option>" for d in divisions])

    page = """
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>登入 - 救護車設備 AI</title>
        <style>
          body{font-family:Arial; background:#f4f7fb; padding:18px}
          .box{max-width:420px; margin:40px auto; background:#fff; padding:18px; border-radius:10px; box-shadow:0 6px 18px rgba(18,24,40,0.06)}
          input, select{width:100%; padding:10px; margin-top:8px; border-radius:6px; border:1px solid #ddd}
          button{background:#1e88ff; color:#fff; border:none; padding:12px; border-radius:8px; width:100%; margin-top:12px}
        </style>
      </head>
      <body>
        <div class="box">
          <h2 style="text-align:center">🔐 登入 - 救護車設備 AI</h2>
          <form action="/login" method="post">
            <label>分隊</label>
            <select name="division" required>""" + options_html + """</select>
            <label style="margin-top:8px">隊員姓名</label>
            <input name="username" placeholder="輸入隊員姓名" required>
            <button type="submit">登入</button>
          </form>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(page)


@app.post("/login")
async def login(request: Request, division: str = Form(...), username: str = Form(...)):
    request.session["user"] = username
    request.session["division"] = division
    return RedirectResponse(url="/upload_form", status_code=303)


@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/")


@app.get("/upload_form", response_class=HTMLResponse)
async def upload_form(request: Request):
    if not request.session.get("user"):
        return RedirectResponse(url="/")

    user = request.session["user"]
    division = request.session["division"]

    page = """
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>上傳 - 救護車設備 AI</title>
        <style>
          body{font-family:Arial; background:#f4f7fb; padding:18px}
          .container{max-width:780px; margin:12px auto}
          .card{background:#fff; padding:16px; border-radius:10px; box-shadow:0 6px 18px rgba(18,24,40,0.06)}
          input[type=file]{width:100%}
          .row{display:flex; gap:8px; flex-wrap:wrap}
          select, input[type=text]{flex:1; padding:10px; border-radius:8px; border:1px solid #ddd}
          button.primary{background:#1e88ff; color:#fff; border:none; padding:12px; border-radius:8px; width:100%}
        </style>
      </head>
      <body>
        <div class="container">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
            <div><strong>分隊：</strong>""" + division + """ &nbsp;&nbsp; <strong>隊員：</strong>""" + user + """</div>
            <div><a href="/logout">登出</a></div>
          </div>

          <div class="card">
            <h3>📸 上傳檢查照片 (最多 """ + str(MAX_UPLOAD) + """ 張)</h3>
            <form action="/upload" enctype="multipart/form-data" method="post">
              <div style="margin-bottom:8px;" class="row">
                <select name="vehicle_type" required>
                  <option value="救護車">救護車</option>
                  <option value="消防車">消防車</option>
                </select>
                <input type="text" name="vehicle_id" placeholder="車輛編號 (例如 A1-1)" required>
              </div>
              <input type="file" name="files" accept="image/*" multiple required>
              <br><br>
              <button class="primary" type="submit">上傳並檢查</button>
            </form>
            <small style="color:#666">Templates: """ + TEMPLATE_DIR + """</small>
          </div>

          <div style="text-align:center; margin-top:12px;">
            <a href="/records">查看最近紀錄</a>
          </div>
        </div>
      </body>
    </html>
    """
    return HTMLResponse(page)


@app.post("/upload", response_class=HTMLResponse)
async def upload(request: Request, files: List[UploadFile] = File(...),
                 vehicle_type: str = Form(...), vehicle_id: str = Form(...)):

    if not request.session.get("user"):
        return RedirectResponse(url="/")

    user = request.session["user"]
    division = request.session["division"]

    if len(files) == 0:
        return HTMLResponse("<h3>❌ 請上傳至少一張圖片</h3>")
    if len(files) > MAX_UPLOAD:
        return HTMLResponse("<h3>❌ 最多上傳 {} 張圖片</h3>".format(MAX_UPLOAD))

    templates = load_templates()
    if not templates:
        return HTMLResponse("<h3>❌ templates 資料夾中沒有模板圖片！</h3>")

    device_templates = {}
    for tname, img in templates.items():
        key = tname.split("_")[0]
        device_templates.setdefault(key, []).append((tname, img))

    all_results = {}
    card_html = ""

    for idx, file in enumerate(files, start=1):
        tmp = f"up_{idx}.jpg"
        with open(tmp, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        img = cv2.imread(tmp)
        if img is None:
            continue
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        device_res = {}
        best_boxes = {}

        for device, tlist in device_templates.items():
            best_score = -1
            best_loc = None
            best_shape = None
            best_tname = None

            for tname, tmpl in tlist:
                try:
                    if tmpl.shape[0] > gray.shape[0] or tmpl.shape[1] > gray.shape[1]:
                        continue
                    res = cv2.matchTemplate(gray, tmpl, cv2.TM_CCOEFF_NORMED)
                    _, maxv, _, maxloc = cv2.minMaxLoc(res)
                    if maxv > best_score:
                        best_score = maxv
                        best_loc = maxloc
                        best_shape = tmpl.shape
                        best_tname = tname
                except:
                    continue

            device_res[device] = {
                "score": best_score,
                "detected": best_score >= THRESHOLD,
                "template": best_tname
            }

            if best_score >= THRESHOLD and best_loc and best_shape:
                h, w = best_shape
                best_boxes[device] = (best_loc, (best_loc[0] + w, best_loc[1] + h), best_score)

        out = img.copy()
        for device, (tl, br, score) in best_boxes.items():
            cv2.rectangle(out, tl, br, (255, 0, 0), 2)
            label = "{} ({:.2f})".format(device, score)
            cv2.putText(out, label, (tl[0], tl[1] - 6),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,0,0), 2)

        b64 = imencode_to_base64(out)
        preview = "<img src='data:image/jpeg;base64,{}' style='max-width:94%; border-radius:8px;'>".format(b64)

        # produce table rows
        rows = ""
        for device, info in device_res.items():
            if info["score"] < THRESHOLD:
                continue
            status = "✔" if info["detected"] else "✘"
            rows += "<tr><td>{}</td><td>{}</td><td>{:.2f}</td><td>{}</td></tr>".format(
                device, status, info["score"], info["template"]
            )

        if rows.strip() == "":
            rows = "<tr><td colspan='4' style='padding:8px'>無高相似度結果</td></tr>"

        card_html += """
        <div style="background:#fff; padding:14px; border-radius:10px; margin-bottom:18px;">
          <h3>📸 圖片 {} : {}</h3>
          <div style="text-align:center;">{}</div>
          <table style="width:100%; margin-top:10px; border-collapse:collapse;">
            <thead><tr style="background:#eef3ff"><th>設備</th><th>結果</th><th>相似度</th><th>模板</th></tr></thead>
            <tbody>{}</tbody>
          </table>
        </div>
        """.format(idx, file.filename, preview, rows)

        all_results[file.filename] = device_res

    save_record(division, user, vehicle_type, vehicle_id, all_results)

    page = """
    <html>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>檢測結果</title>
        <style>
          body{font-family:Arial; background:#f4f7fb; padding:18px}
          .container{max-width:900px; margin:0 auto}
          a.btn{background:#1e88ff; color:#fff; padding:10px 14px; border-radius:8px; text-decoration:none}
        </style>
      </head>
      <body>
        <div class="container">
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <h2>🔎 檢測結果總覽</h2>
            <a href="/upload_form" class="btn">返回</a>
          </div>
          """ + card_html + """
        </div>
      </body>
    </html>
    """

    return HTMLResponse(page)


@app.get("/records", response_class=HTMLResponse)
async def records_page(request: Request):
    if not request.session.get("user"):
        return RedirectResponse(url="/")

    rows = get_recent_records(60)

    body = ""
    for r in rows:
        rid, ts, div, user, vtype, vid, data = r
        body += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
            rid, ts, div, user, vtype, vid
        )

    if body == "":
        body = "<tr><td colspan='6'>沒有紀錄</td></tr>"

    page = """
    <html><head>
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>紀錄</title>
      <style>
        body{font-family:Arial; background:#f4f7fb; padding:18px}
        .container{max-width:900px; margin:0 auto}
      </style>
    </head>
    <body>
      <div class="container">
        <h2>📚 近期檢查紀錄</h2>
        <a href="/upload_form">返回</a>
        <table style="margin-top:12px; width:100%; border-collapse:collapse;">
          <thead><tr style="background:#eef3ff"><th>ID</th><th>時間</th><th>分隊</th><th>隊員</th><th>車種</th><th>車號</th></tr></thead>
          <tbody>""" + body + """</tbody>
        </table>
      </div>
    </body>
    </html>
    """
    return HTMLResponse(page)


# init database
init_db()
