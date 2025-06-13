from flask import Flask, render_template, request, redirect, flash, get_flashed_messages
import os
import mysql.connector
from datetime import datetime
import base64
import sys

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

app = Flask(__name__, 
           template_folder=resource_path('templates'),
           static_folder=resource_path('static'))
app.secret_key = os.urandom(24)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ambika@Bhaskar22",
    database="trading_journal"
)
cursor = db.cursor()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/form")
def form():
    return render_template("form.html")

@app.route("/submit", methods=["POST"])
def submit():
    data = request.form

    def encode_image(file_field, asset_name, trade_entered_date, label):
        file = request.files.get(file_field)
        if file and file.filename:
            folder = os.path.join("static", "charts")
            os.makedirs(folder, exist_ok=True)
            date_str = trade_entered_date.replace('-', '')
            safe_asset_name = asset_name.replace(' ', '_')
            filename = f"{safe_asset_name}_{date_str}_{label}.png"
            file_path = os.path.join(folder, filename)
            file.save(file_path)
            return base64.b64encode(open(file_path, "rb").read()).decode("utf-8")
        return None

    trade_style = data.get("trade_style", "Swing")
    trade_entered_date = data.get("trade_entered_date", "0000-00-00")
    trade_entered_day = data.get("trade_entered_day", "")
    trade_entered_time = data.get("trade_entered_time", "")
    trade_exit_date = data.get("trade_exit_date", "")
    trade_exit_day = data.get("trade_exit_day", "")
    trade_exit_time = data.get("trade_exit_time", "")
    asset_class = data.get("asset_class", "")
    asset_name = data.get("asset_name", "")
    trade_type = data.get("trade_type", "Forward Test")
    strategy_name = data.get("strategy_name", "")
    position_side = data.get("position_side", "Long")
    quantity = int(data.get("quantity", 0)) if data.get("quantity", "").strip() else 0
    entry_signal = data.get("entry_signal", "")
    entry_difficulty = data.get("entry_difficulty", "Medium")
    stop_level = data.get("stop_level", "")
    stop_percent = float(data.get("stop_percent", 0.0)) if data.get("stop_percent", "").strip() else 0.0
    target_level = data.get("target_level", "")
    target_percent = float(data.get("target_percent", 0.0)) if data.get("target_percent", "").strip() else 0.0
    partial_target = data.get("partial_target", "")
    traded_target_percent = float(data.get("traded_target_percent", 0.0)) if data.get("traded_target_percent", "").strip() else 0.0
    trade_result = data.get("trade_result", "Win")
    pnl = float(data.get("pnl", 0.0)) if data.get("pnl", "").strip() else 0.0
    expected_rr = float(data.get("expected_rr", 0.0)) if data.get("expected_rr", "").strip() else 0.0
    actual_rr = float(data.get("actual_rr", 0.0)) if data.get("actual_rr", "").strip() else 0.0

    # Encode images
    pic_1min = encode_image("pic_1min", asset_name, trade_entered_date, "1min")
    pic_3min = encode_image("pic_3min", asset_name, trade_entered_date, "3min")
    pic_5min = encode_image("pic_5min", asset_name, trade_entered_date, "5min")
    pic_15min = encode_image("pic_15min", asset_name, trade_entered_date, "15min")
    pic_1H = encode_image("pic_1H", asset_name, trade_entered_date, "1H")
    pic_1D = encode_image("pic_1D", asset_name, trade_entered_date, "1D")
    pic_1W = encode_image("pic_1W", asset_name, trade_entered_date, "1W")

    query = """
    INSERT INTO trades (
        trade_style, trade_entered_date, trade_entered_day, trade_entered_time,
        trade_exit_date, trade_exit_day, trade_exit_time, asset_class, asset_name,
        trade_type, strategy_name, position_side, quantity, entry_signal,
        entry_difficulty, stop_level, stop_percent, target_level, target_percent,
        partial_target, traded_target_percent, trade_result, pnl, expected_rr, 
        actual_rr, pic_1min, pic_3min, pic_5min, pic_15min, pic_1H, pic_1D, pic_1W,
        notes, mistakes, key_takeaways)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

    values = (
        trade_style,
        trade_entered_date,
        trade_entered_day,
        trade_entered_time,
        trade_exit_date,
        trade_exit_day,
        trade_exit_time,
        asset_class,
        asset_name,
        trade_type,
        strategy_name,
        position_side,
        quantity,
        entry_signal,
        entry_difficulty,
        stop_level,
        stop_percent,
        target_level,
        target_percent,
        partial_target,
        traded_target_percent,
        trade_result,
        pnl,
        expected_rr,
        actual_rr,
        pic_1min,
        pic_3min,
        pic_5min,
        pic_15min,
        pic_1H,
        pic_1D,
        pic_1W,
        data.get("notes", ""),
        data.get("mistakes", ""),
        data.get("key_takeaways", "")
    )

    cursor.execute(query, values)
    db.commit()

    flash("Trade uploaded successfully!")  # Flash the success message
    return redirect("/")

@app.route("/review", methods=["GET", "POST"])
def review():
    cursor.execute("SELECT DISTINCT strategy_name FROM trades")
    strategies = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT trade_type FROM trades")
    trade_types = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT trade_style FROM trades")
    trade_styles = [row[0] for row in cursor.fetchall()]

    selected_strategy = request.form.get("strategy")
    selected_trade_type = request.form.get("trade_type")
    selected_trade_style = request.form.get("trade_style")
    start_date = request.form.get("start_date")
    end_date = request.form.get("end_date")

    query = "SELECT * FROM trades WHERE 1=1"
    values = []

    if selected_strategy:
        query += " AND strategy_name = %s"
        values.append(selected_strategy)
    if selected_trade_type:
        query += " AND trade_type = %s"
        values.append(selected_trade_type)
    if selected_trade_style:
        query += " AND trade_style = %s"
        values.append(selected_trade_style)
    if start_date and end_date:
        query += " AND trade_entered_date BETWEEN %s AND %s"
        values.extend([start_date, end_date])

    # Order by trade_entered_date and trade_entered_time
    query += " ORDER BY trade_entered_date DESC, trade_entered_time DESC"

    cursor.execute(query, values)
    trades = cursor.fetchall()
    no_data = len(trades) == 0
    columns = [col[0] for col in cursor.description]

    return render_template("review.html", trades=trades, columns=columns, strategies=strategies,
                           trade_types=trade_types, trade_styles=trade_styles, no_data=no_data,
                           selected_strategy=selected_strategy,
                           selected_trade_type=selected_trade_type,
                           selected_trade_style=selected_trade_style,
                           start_date=start_date, end_date=end_date)

if __name__ == "__main__":
    app.run(debug=True)
