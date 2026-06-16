# קובץ: ui_components.py
# מטרה: קובץ זה מרכז את כל רכיבי התצוגה (UI) של האפליקציה.
# הפרדה זו מאפשרת לך, כמפתח, לעצב את המסכים במקום אחד מרוכז, 
# מבלי ללכת לאיבוד בתוך לולאות הלוגיקה של חישוב התוצאות.

import streamlit as st

def apply_rtl_styling():
    """
    CSS מרכזי של האפליקציה.

    החלוקה כאן:
    1. RTL כללי
    2. שדות קלט וסיסמה
    3. תיבות בחירה / dropdown
    4. כפתורים
    5. תצוגת משחקים
    6. טבלאות בתים
    7. התאמות מובייל
    """
    st.markdown("""
        <style>

        /* =========================================================
           1. RTL כללי
           אחראי על יישור כללי לימין בכל האפליקציה.
        ========================================================= */
        body, p, div, h1, h2, h3, h4, h5, h6, span, label, li, .stMarkdown {
            direction: rtl !important;
            text-align: right !important;
        }


        /* =========================================================
           2. שדות טקסט וסיסמה
           משפיע על:
           - שם משתמש
           - סיסמה
           - שם תצוגה
           - סיסמת מנהל

           רקע התיבות נשלט בפועל דרך config.toml:
           secondaryBackgroundColor="#EAF7FF"
        ========================================================= */
        div[data-testid="stTextInput"] input {
            direction: rtl !important;
            text-align: right !important;
            border: 2px solid #111111 !important;
            border-radius: 8px !important;
            color: #000000 !important;
            font-size: 16px !important;
            font-weight: 500 !important;
        }

        div[data-testid="stTextInput"] input::placeholder {
            color: #777777 !important;
            font-size: 13px !important;
            opacity: 0.85 !important;
        }


        /* =========================================================
           3. Selectbox / Dropdown
           משפיע על: בחירת יישוב ותוצאות משחקים
        ========================================================= */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] {
            background-color: #bcf6f5 !important;
            border: 2px solid #111111 !important;
            border-radius: 8px !important;
            direction: rtl !important;
            min-height: 35px !important; /* שומר על תיבה צרה וקומפקטית במחשב */
        }

        /* העלמת החץ כדי שהמספר יוכל לתפוס את האמצע */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] svg {
            display: none !important;
        }

        /* ביטול המרווח הפנימי של החץ */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            padding-right: 0px !important;
            padding-left: 0px !important;
        }

        /* כפיית מרכוז, צבע וגודל על כל טקסט בתוך התיבה - מנצח את ה-RTL הכללי */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] * {
            text-align: center !important;
            justify-content: center !important;
            color: #000000 !important;
            font-weight: 900 !important;
            font-size: 20px !important; /* גודל ברירת מחדל למחשב */
        }
        
        /* רשימת האפשרויות הנפתחת */
        div[data-baseweb="popover"] ul,
        div[data-baseweb="popover"] li {
            direction: rtl !important;
            text-align: center !important;
            font-size: 18px !important;
            background-color: #ffffff !important;
            color: #000000 !important;
        }

          
        /* =========================================================
           4. כפתורים
           משפיע על כל כפתורי Streamlit.
        ========================================================= */
        .stButton button {
            border-radius: 8px !important;
            font-weight: 700 !important;
            width: auto !important;
            min-width: 72px !important;
            padding-left: 12px !important;
            padding-right: 12px !important;
        }


        /* =========================================================
           5. תצוגת משחקים
           אחראי על:
           - שורת כותרת המשחק: שעה / טורניר / שלב
           - שמות קבוצות לפני הזנת תוצאה
           - שמות קבוצות אחרי שיש תוצאה
           - המקף בין תוצאות
        ========================================================= */

        /* שורת מידע על המשחק: שעה | טורניר | בית */
        .match-header {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #333333;
            text-align: right !important;
        }

        /* שם קבוצה לפני הזנת תוצאה */
        .team-name {
            font-size: 28px;
            font-weight: 900;
            text-align: center !important;
            line-height: 1.4;
            padding-top: 6px;
            white-space: nowrap;
        }

        /* שם קבוצה אחרי שיש תוצאה */
        .team-name-result {
            font-size: 30px;
            font-weight: 900;
            line-height: 1.4;
            white-space: nowrap;
        }

        /* המקף בין שתי תיבות הזנת התוצאה */
        .score-separator {
            font-size: 24px;
            font-weight: 900;
            text-align: center !important;
            padding-top: 4px;
        }
        
        .pending-match-line {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 34px;
            text-align: center !important;
            direction: rtl !important;
            font-family: inherit !important;
            margin-top: 4px;
            margin-bottom: 4px;
            flex-wrap: wrap;
        }

        .pending-team-name {
            font-size: 30px;
            font-weight: 900;
            line-height: 1.4;
            font-family: inherit !important;
            color: #000000;
        }

        .vs-text {
            font-size: 22px;
            font-weight: 900;
            color: #D00000;
            font-family: inherit !important;
            letter-spacing: 1px;
        }

        .pending-text {
            font-size: 18px;
            font-weight: 700;
            color: #999999;
            font-family: inherit !important;
        }
                
        

        /* השורה שבה מוצגת תוצאה קיימת */
        .match-result-line {
            text-align: center !important;
            margin-top: 4px;
            margin-bottom: 4px;
        }

        /* המקף בתוצאה קיימת, למשל: 1 - 0 */
        .score-separator-inline {
            font-size: 24px;
            font-weight: 900;
            color: #000000;
        }


        /* =========================================================
           6. טקסטים קטנים / הערות
        ========================================================= */
        .helper-text {
            color: #666666;
            font-size: 14px;
            margin-bottom: 8px;
        }


        /* =========================================================
           7. טבלאות בתים
           אחראי על:
           - המשפט מעל הטבלה
           - מסגרת הטבלה
           - כותרות עמודות
           - שמות קבוצות בטבלה
           - סימון מקום ראשון ושני
        ========================================================= */

        /* המשפט מעל כל טבלה */
        .standings-helper {
            direction: rtl !important;
            text-align: right !important;
            color: #444444;
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        /* הטבלה עצמה */
        .standings-table {
            direction: rtl !important;
            text-align: center !important;
            width: 100%;
            border-collapse: collapse;
            border: 3px solid #111111;
            margin-bottom: 24px;
            background-color: white;
        }

        /* כותרות העמודות */
        .standings-table th {
            background-color: #DDEEFF;
            color: black;
            font-size: 20px;
            font-weight: 900;
            text-align: center !important;
            border: 2px solid #111111;
            padding: 10px;
        }

        /* תאי הטבלה */
        .standings-table td {
            color: black;
            font-size: 18px;
            font-weight: 700;
            text-align: center !important;
            border: 1px solid #333333;
            padding: 10px;
        }

        /* שם הקבוצה בתוך הטבלה */
        .standings-table .standings-team-name {
            font-size: 24px;
            font-weight: 900;
            text-align: right !important;
        }

        /* מקום ראשון */
        .standings-table .qualified-first td {
            background-color: #8EF0A0;
        }

        /* מקום שני */
        .standings-table .qualified-second td {
            background-color: #D9FBDD;
        }
                



        /* =========================================================
   8. התאמות למסכי טלפון
   כל מה שכאן משפיע רק על מסכים צרים.
   אם משהו גדול מדי בפלאפון — משנים כאן.
========================================================= */
@media screen and (max-width: 600px) {

        /* =======================================================
        מובייל - שורת הזנת תוצאה
        תיקון לפי אבחון DevTools:
        team-name תפס 334px מתוך 358px, לכן מגבילים את עמודות השמות.
        ======================================================= */

        /* תופסים רק את שורת העריכה של המשחק */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) {
            display: flex !important;
            flex-wrap: nowrap !important;
            align-items: center !important;
            width: 100% !important;
            max-width: 100% !important;
            gap: 2px !important;
            overflow: visible !important;
        }

        /* כל הילדים הישירים של השורה */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) > div {
            min-width: 0 !important;
            padding-left: 0px !important;
            padding-right: 0px !important;
            margin-left: 0px !important;
            margin-right: 0px !important;
            overflow: visible !important;
        }

        /* ילד 1 וילד 5: שמות הקבוצות */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) > div:nth-child(1),
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) > div:nth-child(5) {
            flex: 1 1 0 !important;
            width: auto !important;
            min-width: 0 !important;
            max-width: calc((100% - 120px) / 2) !important;
        }

        /* ילד 2 וילד 4: תיבות התוצאה */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) > div:nth-child(2),
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) > div:nth-child(4) {
            flex: 0 0 48px !important;
            width: 48px !important;
            min-width: 48px !important;
            max-width: 48px !important;
        }

        /* ילד 3: המקף */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) > div:nth-child(3) {
            flex: 0 0 16px !important;
            width: 16px !important;
            min-width: 16px !important;
            max-width: 16px !important;
        }

        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) .team-name {
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;

            /* כאן מגדילים את שמות הקבוצות */
            font-size: 19px !important;
            font-weight: 900 !important;
            line-height: 1.15 !important;

            white-space: normal !important;
            overflow-wrap: break-word !important;
            word-break: normal !important;
            text-align: center !important;
            padding-top: 1px !important;
        }

        /* ה-selectbox עצמו */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) div[data-testid="stSelectbox"] {
            width: 48px !important;
            min-width: 48px !important;
            max-width: 48px !important;
            margin: 0 auto !important;
        }

        /* גוף התיבה */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) div[data-baseweb="select"] {
            width: 48px !important;
            min-width: 48px !important;
            max-width: 48px !important;
            min-height: 36px !important;
            height: 36px !important;
            padding: 0 !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
        }

        /* האזור הפנימי של המספר */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) div[data-baseweb="select"] > div {
            width: 100% !important;
            min-width: 0 !important;
            height: 100% !important;
            padding: 0 !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* המספר עצמו */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) div[data-baseweb="select"] span {
            color: #000000 !important;
            font-size: 18px !important;
            font-weight: 900 !important;
            line-height: 36px !important;
            text-align: center !important;
        }

        /* הסתרת החץ */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) div[data-baseweb="select"] svg {
            display: none !important;
        }

        /* המקף */
        div[data-testid="stHorizontalBlock"]:has(.team-name):has(.score-separator) .score-separator {
            font-size: 18px !important;
            line-height: 1 !important;
            padding-top: 0px !important;
            text-align: center !important;
        }

        .match-header {
            font-size: 13px !important;
            margin-bottom: 6px !important;
        }

        .team-name {
            font-size: 17px !important;
            line-height: 1.15 !important;
            white-space: normal !important;
            padding-top: 1px !important;
            text-align: center !important;
            word-break: normal !important;
            overflow-wrap: anywhere !important;
        }

        .team-name-result {
            font-size: 21px !important;
            line-height: 1.25 !important;
            white-space: normal !important;
        }

        .score-separator {
            font-size: 18px !important;
            padding-top: 1px !important;
            text-align: center !important;
        }

        .match-result-line {
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }

        .score-separator-inline {
            font-size: 18px !important;
        }

        .pending-match-line {
            gap: 18px !important;
            margin-top: 2px !important;
            margin-bottom: 2px !important;
        }

        .pending-team-name {
            font-size: 21px !important;
            line-height: 1.25 !important;
        }

        .vs-text {
            font-size: 17px !important;
            color: #D00000 !important;
        }

        .pending-text {
            font-size: 14px !important;
            color: #AAAAAA !important;
            margin-right: 0px !important;
        }

        .stButton button {
            font-size: 13px !important;
            padding: 4px 8px !important;
            width: auto !important;
            min-width: 64px !important;
        }

        .standings-helper {
            font-size: 13px !important;
        }

        .standings-table th {
            font-size: 13px !important;
            padding: 6px !important;
        }

        .standings-table td {
            font-size: 13px !important;
            padding: 6px !important;
        }

        .standings-table .standings-team-name {
            font-size: 15px !important;
            white-space: normal !important;
        }
                
        
    }

        </style>
    """, unsafe_allow_html=True)


def render_page_header(title, subtitle=None):
    """
    פונקציה מודולרית שמציירת את הכותרת הראשית של העמוד.
    במקום לכתוב st.title שוב ושוב, אנחנו משתמשים בפונקציה הזו.
    """
    st.title(title)
    
    if subtitle:
        st.markdown(f"<h3 style='color: gray;'>{subtitle}</h3>", unsafe_allow_html=True)
        
    st.markdown("---")


def get_game_badge_html(tour_cat, stage_name):
    """
    פונקציה זו מייצרת את ה'תג' החזותי של המשחק (למשל: 'טורניר ד - בית א').
    היא אחראית אך ורק על הצבעים והנראות (HTML).
    """
    t_color = "#1E90FF" if 'ד' in tour_cat else "#8A2BE2" if 'ה' in tour_cat else "#008B8B" if 'ו' in tour_cat else "#4682B4"
    s_color = "#FF1493" if 'א' in stage_name else "#4B0082" if 'ב' in stage_name else "#A0522D" if 'חצי' in stage_name else "#2F4F4F"
    
    return f"<span style='color:{t_color}; font-weight:bold;'>{tour_cat}</span> - <span style='color:{s_color}; font-weight:bold;'>{stage_name}</span>"


def render_standings_table(df_stage):
    """
    מציגה טבלת בית מעוצבת ב-HTML מלא:
    - שומרת על RTL
    - בלי כפילות טבלאות
    - מקום ראשון ושני מסומנים בירוק
    - שמות קבוצות וכותרות גדולים וברורים
    """
    import streamlit as st

    df_display = df_stage.drop(columns=['stage'], errors='ignore').copy()

    df_display = df_display.rename(columns={
        'team': 'קבוצה',
        'matches': 'משחקים',
        'goals_for': 'זכות',
        'goals_against': 'חובה',
        'goal_diff': 'הפרש',
        'points': 'נקודות'
    })

    desired_cols = ['קבוצה', 'משחקים', 'זכות', 'חובה', 'הפרש', 'נקודות']
    actual_cols = [col for col in desired_cols if col in df_display.columns]
    df_for_table = df_display[actual_cols].reset_index(drop=True)

    st.markdown(
        "<div class='standings-helper'>🏆 הקבוצות שיסיימו במקום הראשון והשני יעלו לשלב הבא.</div>",
        unsafe_allow_html=True
    )

    html = """
    <table class="standings-table">
        <thead>
            <tr>
    """

    for col in df_for_table.columns:
        html += f"<th>{col}</th>"

    html += """
            </tr>
        </thead>
        <tbody>
    """

    for row_idx, row in df_for_table.iterrows():
        if row_idx == 0:
            row_class = "qualified-first"
        elif row_idx == 1:
            row_class = "qualified-second"
        else:
            row_class = ""

        html += f"<tr class='{row_class}'>"

        for col in df_for_table.columns:
            value = row[col]
            if col == 'קבוצה':
                html += f"<td class='standings-team-name'>{value}</td>"
            else:
                html += f"<td>{value}</td>"

        html += "</tr>"

    html += """
        </tbody>
    </table>
    """

    st.markdown(html, unsafe_allow_html=True)


def is_score_filled(score):
    """
    בודקת האם ערך תוצאה באמת הוזן.
    0 הוא תוצאה חוקית.
    ריק / NaN / מחרוזת ריקה / 'nan' אינם תוצאה.
    """
    import pandas as pd

    if pd.isna(score):
        return False

    score_str = str(score).strip().lower()

    if score_str in ["", "nan", "none"]:
        return False

    return True

def has_match_result(score_a, score_b):
    """
    משחק נחשב כשוחק רק אם שתי התוצאות מולאו בפועל.
    חשוב: 0-0 הוא כן תוצאה חוקית, אבל רק אם שני האפסים באמת הוזנו.
    """
    return is_score_filled(score_a) and is_score_filled(score_b)


def get_score_numbers(score_a, score_b):
    """
    מחזירה את התוצאות כמספרים שלמים אחרי שווידאנו שיש תוצאה.
    """
    return int(float(score_a)), int(float(score_b))


def format_display_score(score_a, score_b):
    """
    מחזירה תצוגת תוצאה.
    אם המשחק לא שוחק — לא מחזירה 0-0 מזויף.
    """
    if not has_match_result(score_a, score_b):
        return "טרם שוחק"

    sa, sb = get_score_numbers(score_a, score_b)
    return f"{sa} - {sb}"

def get_score_data(score_a, score_b):
    """
    מחזירה טאפל: (טקסט_להצגה, ערך_a, ערך_b)
    מטפלת בערכים ריקים בצורה בטוחה.
    """
    import pandas as pd
    if pd.isna(score_a) or pd.isna(score_b):
        return "טרם שוחק", 0, 0
    
    a, b = int(float(score_a)), int(float(score_b))
    return f"{a} - {b}", a, b

def get_player_flag_html(player_name, country_code):
    """
    מחזירה תגית HTML עם תמונת הדגל מהשרת החיצוני ושם השחקן.
    """
    return f"""
    <div style="background-color: #EAF7FF; padding: 12px; border-radius: 8px; border: 1px solid #111111; display: inline-block; font-size: 18px; font-weight: bold; margin-bottom: 10px;">
        <img src="https://flagcdn.com/24x18/{country_code}.png" style="vertical-align: middle; margin-left: 8px; box-shadow: 0px 0px 3px rgba(0,0,0,0.3);"> 
        {player_name}
    </div>
    """

def render_app_footer():
    """
    מציג חתימת פיתוח ופרטי קשר בתחתית האפליקציה.
    בלי HTML, כדי למנוע מצב שתגיות <div> מוצגות כטקסט.
    """
    import streamlit as st
    from urllib.parse import quote

    developer_name = "אלירן מרדכי"
    phone_display = "050-824-4707"
    phone_whatsapp = "972508244707"
    email = "eliran938@gmail.com"

    main_text = f"© כל הזכויות שמורות | פותח על ידי {developer_name}"
    promo_text = "להצעות ייעול ושאלות ניתן ליצור קשר-"

    message_text = "היי אלירן,בקשר לאפליקציית ניהול הטורניר. רציתי לשאול/להציע...."

    whatsapp_link = f"https://wa.me/{phone_whatsapp}?text={quote(message_text)}"

    email_subject = quote("שאלה על האפליקציה")
    email_body = quote(message_text)
    email_link = f"mailto:{email}?subject={email_subject}&body={email_body}"

    st.markdown("---")
    st.markdown(f"**{main_text}**")
    st.caption(promo_text)
    st.markdown(
        f"[📲 WhatsApp]({whatsapp_link}) &nbsp; | &nbsp; "
        f"[✉️ {email}]({email_link}) &nbsp; | &nbsp; "
        f"📞 {phone_display}"
    )

    