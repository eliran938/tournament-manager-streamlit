# קובץ data_manager.py
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# הלינק הישיר לגוגל שיטס שלך
SHEET_URL = st.secrets["google_sheets"]["sheet_url"]

def get_connection():
    """פונקציית עזר שיוצרת את החיבור לגוגל"""
    return st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    """קורא נתונים מהענן, שומר בזיכרון ל-60 שניות כדי למנוע קריסת API"""
    conn = get_connection()
    # ttl=60 ימנע קריאות מיותרות ויגן עלינו מחסימות של גוגל
    df = conn.read(spreadsheet=SHEET_URL, worksheet=sheet_name, ttl=60)
    
    if 'team_a' in df.columns:
        df['team_a'] = df['team_a'].astype(str).str.strip()
        df['team_b'] = df['team_b'].astype(str).str.strip()
    if 'field' in df.columns:
        df['field'] = df['field'].astype(str).str.strip()
        
    return df

def save_data(df, sheet_name):
    """שומר לענן ומנקה את זיכרון המטמון כדי שהמערכת תמשוך נתונים טריים"""
    conn = get_connection()
    conn.update(spreadsheet=SHEET_URL, worksheet=sheet_name, data=df)
    st.cache_data.clear() # חובה! מכריח את המערכת לקרוא מחדש רק אחרי ששמרנו

def add_to_audit_log(username, action_description):
    """מוסיף שורה חדשה ללוג הפעולות"""
    conn = get_connection()
    
    # מנסים למשוך את הלוג הקיים
    try:
        df_log = conn.read(spreadsheet=SHEET_URL, worksheet="audit_log")
    except Exception:
        # אם הלשונית עדיין לא קיימת או ריקה, נייצר טבלה בסיסית מראש
        df_log = pd.DataFrame(columns=["timestamp", "user", "action"])
        
    # מייצרים את השורה החדשה (חותמת זמן, שם המשתמש, ומה הוא עשה)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_row = pd.DataFrame([{
        "timestamp": now, 
        "user": username, 
        "action": action_description
    }])
    
    # מדביקים את השורה החדשה לתחתית הטבלה הקיימת ושומרים לענן
    df_log = pd.concat([df_log, new_row], ignore_index=True)
    conn.update(spreadsheet=SHEET_URL, worksheet="audit_log", data=df_log)

def add_to_access_log(display_name, settlement, role, competition_name, tour_id, username="", visitor_token=""):
    """
    רושם כל כניסה לאפליקציה:
    אורח / צוות, שם תצוגה, יישוב, תחרות, ושעת כניסה.
    """
    conn = get_connection()

    try:
        df_log = conn.read(spreadsheet=SHEET_URL, worksheet="access_log")
    except Exception:
        df_log = pd.DataFrame(columns=[
            "timestamp",
            "competition_name",
            "tour_id",
            "role",
            "display_name",
            "settlement",
            "username",
            "visitor_token"
        ])

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_row = pd.DataFrame([{
        "timestamp": now,
        "competition_name": competition_name,
        "tour_id": tour_id,
        "role": role,
        "display_name": display_name,
        "settlement": settlement,
        "username": username,
        "visitor_token": visitor_token
    }])

    df_log = pd.concat([df_log, new_row], ignore_index=True)
    conn.update(spreadsheet=SHEET_URL, worksheet="access_log", data=df_log)


def find_recent_guest_by_token(visitor_token, competition_name, minutes=60):
    """
    בודק האם visitor_token כבר נכנס לאותה תחרות בשעה האחרונה.
    אם כן — מחזיר את פרטי האורח כדי לא לבקש ממנו להירשם שוב.
    """
    if not visitor_token:
        return None

    conn = get_connection()

    try:
        df_log = conn.read(spreadsheet=SHEET_URL, worksheet="access_log")
    except Exception:
        return None

    if df_log.empty or "visitor_token" not in df_log.columns:
        return None

    try:
        df_log["timestamp"] = pd.to_datetime(df_log["timestamp"], errors="coerce")
        cutoff_time = datetime.now() - pd.Timedelta(minutes=minutes)

        matches = df_log[
            (df_log["visitor_token"].astype(str) == str(visitor_token))
            & (df_log["competition_name"].astype(str) == str(competition_name))
            & (df_log["role"].astype(str) == "guest")
            & (df_log["timestamp"] >= cutoff_time)
        ]

        if matches.empty:
            return None

        latest = matches.sort_values(by="timestamp").iloc[-1]

        return {
            "display_name": latest.get("display_name", "אורח"),
            "settlement": latest.get("settlement", ""),
            "visitor_token": latest.get("visitor_token", visitor_token)
        }
    except Exception:
        # אם יש שגיאה כלשהי בפורמט התאריכים, לא קורסים - פשוט מחזירים שאין זיהוי
        return None

def find_recent_staff_by_token(staff_token, competition_name, minutes=60):
    """
    Restores a staff login by a temporary session token.
    The token is random and expires by time; no password is stored in the URL.
    """
    if not staff_token:
        return None

    conn = get_connection()

    try:
        df_log = conn.read(spreadsheet=SHEET_URL, worksheet="staff_sessions")
    except Exception:
        return None

    if df_log.empty or "staff_session" not in df_log.columns:
        return None

    try:
        df_log["timestamp"] = pd.to_datetime(df_log["timestamp"], errors="coerce")
        cutoff_time = datetime.now() - pd.Timedelta(minutes=minutes)

        matches = df_log[
            (df_log["staff_session"].astype(str) == str(staff_token))
            & (df_log["competition_name"].astype(str) == str(competition_name))
            & (df_log["timestamp"] >= cutoff_time)
        ]

        if matches.empty:
            return None

        latest = matches.sort_values(by="timestamp").iloc[-1]

        username = str(latest.get("username", "")).strip()
        if not username:
            username = str(latest.get("display_name", "")).strip()

        if not username:
            return None

        return {
            "username": username,
            "staff_token": latest.get("staff_session", staff_token)
        }
    except Exception:
        return None

def add_staff_session(username, competition_name, tour_id, staff_token):
    """
    Stores a small staff restore record.
    This intentionally avoids scanning access_log, which can grow large.
    """
    conn = get_connection()

    try:
        df_sessions = conn.read(spreadsheet=SHEET_URL, worksheet="staff_sessions")
    except Exception:
        df_sessions = pd.DataFrame(columns=[
            "timestamp",
            "competition_name",
            "tour_id",
            "username",
            "staff_session"
        ])

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    new_row = pd.DataFrame([{
        "timestamp": now,
        "competition_name": competition_name,
        "tour_id": tour_id,
        "username": username,
        "staff_session": staff_token
    }])

    df_sessions = pd.concat([df_sessions, new_row], ignore_index=True)
    conn.update(spreadsheet=SHEET_URL, worksheet="staff_sessions", data=df_sessions)

def get_staff_credentials():
    """מושך את רשימת אנשי הצוות מהשיטס למילון"""
    try:
        df = load_data("staff_users")
        # מוודא שאין רווחים מיותרים בטעות בהקלדה בגיליון
        df['username'] = df['username'].astype(str).str.strip()
        df['password'] = df['password'].astype(str).str.strip()
        return dict(zip(df['username'], df['password']))
    except Exception:
        # If staff_users cannot be loaded, do not allow a hardcoded fallback login.
        return {}
