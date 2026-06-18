# קובץ app.py
import streamlit as st
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import uuid
import random

# ייבוא הקבצים המודולריים שלנו
import config
import ui_components
import data_manager
import logic

# 1. הגדרות דף בסיסיות
st.set_page_config(page_title="ניהול טורניר", layout="wide", page_icon="🏆")

ui_components.apply_rtl_styling()

# 2. ניהול מצב התחברות (Session State)
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['username'] = "אורח"

if 'viewer_registered' not in st.session_state:
    st.session_state['viewer_registered'] = False
    st.session_state['viewer_name'] = ""
    st.session_state['viewer_settlement'] = ""
    st.session_state['visitor_token'] = ""

if 'staff_session_token' not in st.session_state:
    st.session_state['staff_session_token'] = ""

if 'show_refresh_success' not in st.session_state:
    st.session_state['show_refresh_success'] = False

if 'nickname_rerolls_left' not in st.session_state:
    st.session_state['nickname_rerolls_left'] = config.MAX_NICKNAME_REROLLS

if 'current_nickname' not in st.session_state:
    st.session_state['current_nickname'] = random.choice(list(config.PLAYER_NICKNAMES_DICT.keys()))

# Auto-refresh is activated only after URL tokens are restored.
# Staff members are never force-refreshed, so score entry is not interrupted.

# 3. זיהוי הטורניר מהקישור (URL)
# אם לא נכתב כלום בקישור, נניח שמדובר בבית אל לצורך בדיקות
tour_id = st.query_params.get("tour", "beit_el") 
tour_name = config.TOURNAMENTS.get(tour_id, "טורניר כללי")

# ניסיון שחזור אורח לפי visitor_token מהקישור
visitor_from_url = st.query_params.get("visitor", "")

if (
    not st.session_state['logged_in']
    and not st.session_state['viewer_registered']
    and visitor_from_url
):
    recent_guest = data_manager.find_recent_guest_by_token(
        visitor_token=visitor_from_url,
        competition_name=tour_name,
        minutes=60
    )

    if recent_guest:
        st.session_state['viewer_registered'] = True
        st.session_state['viewer_name'] = recent_guest["display_name"]
        st.session_state['viewer_settlement'] = recent_guest["settlement"]
        st.session_state['visitor_token'] = recent_guest["visitor_token"]

staff_session_from_url = st.query_params.get("staff_session", "")

if (
    not st.session_state['logged_in']
    and not st.session_state['viewer_registered']
    and staff_session_from_url
):
    recent_staff = data_manager.find_recent_staff_by_token(
        staff_token=staff_session_from_url,
        competition_name=tour_name,
        minutes=60
    )

    if recent_staff:
        st.session_state['logged_in'] = True
        st.session_state['username'] = recent_staff["username"]
        st.session_state['staff_session_token'] = recent_staff["staff_token"]

# Guests keep passive live updates. Staff refresh manually so score entry is not interrupted.
if not st.session_state['logged_in']:
    st_autorefresh(interval=30000, key="data_refresh")


# מסך פתיחה ראשי — מוצג רק למי שעדיין לא נכנס כאורח או כצוות
if not st.session_state['logged_in'] and not st.session_state['viewer_registered']:
    st.title(f"🏆 ברוכים הבאים לאפליקציית המעקב של {tour_name}")

    st.markdown("### להורים וילדים")
    st.markdown("בחרו יישוב ושם תצוגה כדי לצפות בלו״ז, בטבלאות ובתוצאות בזמן אמת.")

    settlement = st.selectbox(
        "בחר יישוב",
        placeholder="בחר יישוב",
        options=[""] + config.SETTLEMENTS,
        index=0
        
    )

    guest_name_input = st.text_input(
        "שם תצוגה, לא חובה,ניתן להגריל כינוי זמני",
        placeholder=f"אם יישאר ריק, תיקרא: {st.session_state['current_nickname']}"
    )

    st.markdown("#### כינוי זמני")
    current_player = st.session_state['current_nickname']
    country_code = config.PLAYER_NICKNAMES_DICT[current_player]
    st.markdown(ui_components.get_player_flag_html(current_player, country_code), unsafe_allow_html=True)
    col_nick_1, col_nick_2 = st.columns([1, 2])

    with col_nick_1:
        if st.button(
            "🎲 הגרל שחקן אחר",
            disabled=st.session_state['nickname_rerolls_left'] <= 0
        ):
            st.session_state['current_nickname'] = random.choice(list(config.PLAYER_NICKNAMES_DICT.keys()))
            st.session_state['nickname_rerolls_left'] -= 1
            st.rerun()

    with col_nick_2:
        st.caption(f"נשארו {st.session_state['nickname_rerolls_left']} הגרלות")

    if st.button("כניסה לצפייה בתוצאות", type="primary", use_container_width=True):
        if settlement == "":
            st.error("יש לבחור יישוב כדי להיכנס לצפייה.")
        else:
            display_name = guest_name_input.strip()
            if display_name == "":
                display_name = st.session_state['current_nickname']

            visitor_token = str(uuid.uuid4())

            st.session_state['viewer_registered'] = True
            st.session_state['viewer_name'] = display_name
            st.session_state['viewer_settlement'] = settlement
            st.session_state['visitor_token'] = visitor_token

            data_manager.add_to_access_log(
                display_name=display_name,
                settlement=settlement,
                role="guest",
                competition_name=tour_name,
                tour_id=tour_id,
                visitor_token=visitor_token
            )

            st.query_params["visitor"] = visitor_token
            st.rerun()

    st.markdown("---")

    with st.expander("🔒 איזור התחברות לאנשי צוות"):
        username_input = st.text_input("שם משתמש", placeholder="הזן שם משתמש")
        password_input = st.text_input("סיסמה", type="password", placeholder="הזן סיסמה")

        if st.button("התחבר כאיש צוות", type="primary", use_container_width=True):
            staff_users_dict = data_manager.get_staff_credentials()
            if username_input in staff_users_dict and staff_users_dict[username_input] == password_input:
                staff_session_token = str(uuid.uuid4())

                st.session_state['logged_in'] = True
                st.session_state['username'] = username_input
                st.session_state['staff_session_token'] = staff_session_token

                data_manager.add_to_access_log(
                    display_name=username_input,
                    settlement="",
                    role="staff",
                    competition_name=tour_name,
                    tour_id=tour_id,
                    username=username_input,
                    visitor_token=staff_session_token
                )

                data_manager.add_staff_session(
                    username=username_input,
                    competition_name=tour_name,
                    tour_id=tour_id,
                    staff_token=staff_session_token
                )

                st.query_params["staff_session"] = staff_session_token
                st.rerun()
            else:
                st.error("פרטים שגויים, נסה שוב.")

    ui_components.render_app_footer()   
    st.stop()

if ui_components.render_floating_refresh_button():
    st.cache_data.clear()
    st.session_state['show_refresh_success'] = True
    st.rerun()

if st.session_state.get('show_refresh_success'):
    st.toast("הנתונים מעודכנים", icon="✅")
    st.session_state['show_refresh_success'] = False


# פס מצב עליון במקום sidebar
if st.session_state['logged_in']:
    col_status_1, col_status_2 = st.columns([3, 1])

    with col_status_1:
        st.success(f"מחובר כאיש צוות: {st.session_state['username']}")

    with col_status_2:
        if st.button("התנתק"):
            st.session_state['logged_in'] = False
            st.session_state['staff_session_token'] = ""
            if "staff_session" in st.query_params:
                del st.query_params["staff_session"]
            st.session_state['username'] = "אורח"
            st.rerun()

elif st.session_state['viewer_registered']:
    viewer_name = st.session_state['viewer_name']
    settlement = st.session_state['viewer_settlement']
    
    # בודקים אם השם קיים במילון השחקנים שלנו כדי להצמיד לו דגל
    if viewer_name in config.PLAYER_NICKNAMES_DICT:
        country_code = config.PLAYER_NICKNAMES_DICT[viewer_name]
        flag_html = f'<img src="https://flagcdn.com/16x12/{country_code}.png" style="vertical-align: middle; margin-left: 4px; box-shadow: 0px 0px 2px rgba(0,0,0,0.3);">'
        st.markdown(f"<div style='color: gray; font-size: 14px;'>צופה כ־ {flag_html} <b>{viewer_name}</b> | יישוב: {settlement}</div>", unsafe_allow_html=True)
    else:
        # אם הזינו שם חופשי, מציגים רגיל
        st.caption(f"צופה כ־{viewer_name} | יישוב: {settlement}")


if st.session_state['logged_in']:
    with st.expander("⚠️ אזור מנהל מתקדם", expanded=False):
        admin_pass = st.text_input(
            "סיסמת מנהל לאיפוס",
            type="password",
            placeholder="הזן סיסמת מנהל"
        )

        if st.button("איפוס התחרות הנוכחית בלבד"):
            staff_users_dict = data_manager.get_staff_credentials()
            if admin_pass == staff_users_dict.get("admin"):
                df_to_reset = data_manager.load_data("luz_game")

                df_to_reset['competition_name'] = (
                    df_to_reset['competition_name']
                    .astype(str)
                    .str.replace('"', '')
                    .str.strip()
                )

                competition_mask = df_to_reset['competition_name'] == tour_name

                df_to_reset.loc[competition_mask, 'score_a'] = float('nan')
                df_to_reset.loc[competition_mask, 'score_b'] = float('nan')

                knockout_mask = (
                    competition_mask
                    & ~df_to_reset['stage'].astype(str).str.contains('בית', na=False)
                )

                df_to_reset.loc[knockout_mask, 'team_a'] = float('nan')
                df_to_reset.loc[knockout_mask, 'team_b'] = float('nan')

                data_manager.save_data(df_to_reset, "luz_game")

                data_manager.add_to_audit_log(
                    st.session_state['username'],
                    f"איפס את כל נתוני התחרות הנוכחית: {tour_name}"
                )

                st.toast(f"🚨 אופסו רק נתוני {tour_name}")
                st.rerun()
            else:
                st.error("סיסמה שגויה")


st.title(f"🏆 {tour_name}")

# 5. משיכת הנתונים וסינון
try:
    df_all = data_manager.load_data("luz_game")
    # שליחת הנתונים ל"מוח" לסינון לפי הטורניר הרלוונטי
    df_tour = logic.filter_by_tournament(df_all, tour_name)
except Exception as e:
    st.error("❌ שגיאה בטעינת הנתונים מגוגל. ודא שהרשאות השיתוף תקינות.")
    st.write(e) # השורה הזו תחשוף לנו את השגיאה האמיתית!
    st.stop()

# 6. יצירת הלשוניות הראשיות של המערכת
# נחלץ את רשימת המגרשים והטורנירים הייחודיים
fields = [f for f in df_tour['field'].unique() if pd.notna(f) and str(f).strip() != '']
tournaments = [t for t in df_tour['tournament_name'].unique() if pd.notna(t) and str(t).strip() != '']

# בניית כותרות הלשוניות הראשיות: הראשונה מגרשים, והשאר לפי גילאים
main_tab_titles = ["📍 לו\"ז ומגרשים (הזנת תוצאות)"] + [f"🏆 {t}" for t in tournaments]
main_tabs = st.tabs(main_tab_titles)


# === לשונית ראשית 1: לו"ז ומגרשים (תצוגת עבודה וניהול של אנשי הצוות) ===
with main_tabs[0]:
    st.header("⚽ לוז משחקים לפי מגרשים")
    st.info("אנשי צוות: אנא בחרו את המגרש שלכם מתוך הלשוניות כאן למטה כדי לצפות בלוז המעודכן ולהזין תוצאות.")
    
    # יצירת לשוניות פנימיות בתוך המגרשים
    field_tabs = st.tabs(fields)
    for f_idx, field_name in enumerate(fields):
        with field_tabs[f_idx]:
            st.subheader(f"📍 מגרש: {field_name}")
            
            # סינון המשחקים של המגרש הנוכחי ומיון כרונולוגי לפי שעה
            df_field = df_tour[df_tour['field'] == field_name].sort_values(by='time')
            
            # כפתור שמירה גורפת (הכפתור היחיד שדרכו שומרים כעת!)
            if st.session_state['logged_in']:
                if st.button("💾 שמור את כל התוצאות המעודכנות במגרש", key=f"save_bulk_{field_name}"):
                    changes_made = False
                    audit_entries = []

                    for idx, row in df_field.iterrows():
                        if st.session_state.get(f"edit_{idx}", not pd.notna(row['score_a'])):
                            val_a = st.session_state.get(f"a_{idx}")
                            val_b = st.session_state.get(f"b_{idx}")
                            
                            if val_a != "" and val_a is not None and val_b != "" and val_b is not None:
                                df_all.at[idx, 'score_a'] = float(val_a)
                                df_all.at[idx, 'score_b'] = float(val_b)
                                st.session_state[f"edit_{idx}"] = False
                                changes_made = True

                                team_a_name = str(row['team_a']).strip()
                                team_b_name = str(row['team_b']).strip()
                                stage_name_for_log = str(row['stage']).strip()
                                tournament_name_for_log = str(row['tournament_name']).strip()

                                audit_entries.append(
                                    f"עדכן תוצאה במגרש '{field_name}': "
                                    f"{team_a_name} ({val_a}) - ({val_b}) {team_b_name} "
                                    f"| {tournament_name_for_log} - {stage_name_for_log} | שעה {row['time']}"
                                )
                    
                    if changes_made:
                        df_all = logic.update_knockout_stages(df_all)
                        data_manager.save_data(df_all, "luz_game")

                        for audit_entry in audit_entries:
                            data_manager.add_to_audit_log(
                                st.session_state['username'],
                                audit_entry
                            )

                        st.toast("✅ כל התוצאות נשמרו בהצלחה!")
                        st.rerun()
            
            st.divider()
            
            for idx, row in df_field.iterrows():
                ta = str(row['team_a']).strip()
                tb = str(row['team_b']).strip()
                stage_name = str(row['stage']).strip()
                tour_cat = str(row['tournament_name']).strip()
                
                df_this_tour = df_tour[df_tour['tournament_name'] == tour_cat]
                

                has_result = ui_components.has_match_result(row['score_a'], row['score_b'])
                
                # קבלת תגית המשחק מהקובץ המודולרי
                game_info_html = ui_components.get_game_badge_html(tour_cat, stage_name)
                
                if ta == 'nan' or tb == 'nan' or ta == '' or tb == '':
                    st.markdown(f"🕒 **{row['time']}** | {game_info_html} | ⏳ **ממתין לשיבוץ קבוצות**", unsafe_allow_html=True)
                    st.divider()
                    continue
                    
                # --- תצוגת מנהל ---
                if st.session_state['logged_in']:
                    edit_key = f"edit_{idx}"
                    if edit_key not in st.session_state:
                        st.session_state[edit_key] = not has_result
                        
                    if has_result and not st.session_state[edit_key]:
                        
                        # פונקציה עזר קטנה להמרת תוצאה בצורה בטוחה (אפשר להוסיף אותה בתחילת ה-app.py או פשוט להשתמש בזה inline):
                        # במקום כל החישובים של sa, sb וה-if-ים המסובכים:
                        score_display = ui_components.format_display_score(row['score_a'], row['score_b'])
                        sa = int(float(row['score_a']))
                        sb = int(float(row['score_b']))

                        color_a = "green" if sa > sb else "red" if sa < sb else "orange"
                        color_b = "green" if sb > sa else "red" if sb < sa else "orange"
                        
                        # שורת התוצאה במרכז, בלי כפתורים לידה
                        st.markdown(
                            f"<div class='match-header'>✅ 🕒 <b>{row['time']}</b> | {game_info_html}</div>"
                            f"<div class='match-result-line'>"
                            f"<span class='team-name-result' style='color:{color_a};'>{ta} ({sa})</span>"
                            f" <span class='score-separator-inline'>-</span> "
                            f"<span class='team-name-result' style='color:{color_b};'>({sb}) {tb}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                        # שורת כפתורים נפרדת: ימין ושמאל
                        with st.expander("⚙️ פעולות", expanded=False):
                            if st.button("✏️ ערוך תוצאה", key=f"btn_edit_{idx}"):
                                st.session_state[edit_key] = True
                                st.rerun()

                            if st.button("🗑️ בטל תוצאה", key=f"btn_del_{idx}"):
                                df_all.at[idx, 'score_a'] = float('nan')
                                df_all.at[idx, 'score_b'] = float('nan')

                                df_all = logic.update_knockout_stages(df_all)
                                data_manager.save_data(df_all, "luz_game")

                                data_manager.add_to_audit_log(
                                    st.session_state['username'],
                                    f"ביטל תוצאה במגרש '{field_name}': {ta} ({sa}) - ({sb}) {tb} | {tour_cat} - {stage_name} | שעה {row['time']}"
                                )

                                st.toast("🗑️ תוצאת המשחק נמחקה והטורניר סונכרן!")
                                st.rerun()
                    else:
                        # חלוקה מחדש ל-5 עמודות קלאסיות ללא כפתור שמירה בודד
                        # שורה ראשונה: פרטי המשחק
                        st.markdown(
                            f"<div class='match-header'>🕒 <b>{row['time']}</b> | {game_info_html}</div>",
                            unsafe_allow_html=True
                        )

                        # שורה שנייה: קבוצות ותוצאה
                        cols = st.columns([1.4, 0.28, 0.08, 0.28, 1.4], gap="small")

                        cols[0].markdown(
                            f"<div class='team-name'>{ta}</div>",
                            unsafe_allow_html=True
                        )

                        options = [""] + [str(n) for n in range(21)]

                        val_a = str(int(float(row['score_a']))) if pd.notna(row['score_a']) and str(row['score_a']) != 'nan' else ""
                        val_b = str(int(float(row['score_b']))) if pd.notna(row['score_b']) and str(row['score_b']) != 'nan' else ""

                        idx_a = options.index(val_a) if val_a in options else 0
                        idx_b = options.index(val_b) if val_b in options else 0

                        cols[1].selectbox(
                            "שערי קבוצה א",
                            options=options,
                            index=idx_a,
                            key=f"a_{idx}",
                            label_visibility="collapsed"
                        )

                        cols[2].markdown(
                            "<div class='score-separator'>-</div>",
                            unsafe_allow_html=True
                        )

                        cols[3].selectbox(
                            "שערי קבוצה ב",
                            options=options,
                            index=idx_b,
                            key=f"b_{idx}",
                            label_visibility="collapsed"
                        )

                        cols[4].markdown(
                            f"<div class='team-name'>{tb}</div>",
                            unsafe_allow_html=True
                        )
                            
  
                
                # --- תצוגת אורח ---
                else:
                    if has_result:
                        # פונקציה עזר קטנה להמרת תוצאה בצורה בטוחה (אפשר להוסיף אותה בתחילת ה-app.py או פשוט להשתמש בזה inline):
                            # במקום כל החישובים של sa, sb וה-if-ים המסובכים:
                        score_display = ui_components.format_display_score(row['score_a'], row['score_b'])
                        sa = int(float(row['score_a']))
                        sb = int(float(row['score_b']))

                        color_a = "green" if sa > sb else "red" if sa < sb else "orange"
                        color_b = "green" if sb > sa else "red" if sb < sa else "orange"
                        st.markdown(
                            f"<div class='match-header'>✅ 🕒 <b>{row['time']}</b> | {game_info_html}</div>"
                            f"<div class='match-result-line'>"
                            f"<span class='team-name-result' style='color:{color_a};'>{ta} ({sa})</span>"
                            f" <span class='score-separator-inline'>-</span> "
                            f"<span class='team-name-result' style='color:{color_b};'>({sb}) {tb}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<div class='match-header'>🕒 <b>{row['time']}</b> | {game_info_html}</div>"
                            f"<div class='pending-match-line'>"
                            f"<span class='pending-team-name'>{ta}</span>"
                            f"<span class='vs-text'>VS</span>"
                            f"<span class='pending-team-name'>{tb}</span>"
                            f"<span class='pending-text'>טרם שוחק</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                
                st.divider()

# === לשוניות ראשיות נוספות: חלוקה לפי טורנירים (תצוגת צופים להורים וילדים) ===
for t_idx, tour_name_local in enumerate(tournaments):
    with main_tabs[t_idx + 1]:
        st.header(f"🏆 {tour_name_local}")
        
        # סינון הנתונים הרלוונטיים רק לשכבת הגיל הספציפית הזו
        df_this_tour = df_tour[df_tour['tournament_name'] == tour_name_local]
        
        # --- חלק 1: טבלאות הבתים של הטורניר הנוכחי בלבד ---
        st.subheader("📊 מצב טבלאות הבתים")
        df_standings = logic.calculate_standings(df_this_tour)
        
        if df_standings.empty:
            st.info("אין נתוני בתים להצגה עבור טורניר זה.")
        else:
            stages = df_standings['stage'].unique()
            for stage in stages:
                st.markdown(f"#### {stage}")
                df_stage = df_standings[df_standings['stage'] == stage]
                
                # רנדור הטבלה דרך קובץ התצוגה שלנו
                ui_components.render_standings_table(df_stage)
                
        st.divider()
        
        # --- חלק 2: שלבי נוקאאוט (חצי גמר וגמר) של הטורניר הנוכחי בלבד ---
        # --- חלק 2: שלבי נוקאאוט (חצי גמר וגמר) של הטורניר הנוכחי בלבד ---
        st.subheader("🏁 שלבי הכרעה (חצי גמר וגמר)")
        
        # סינון לשלבים שאינם "בית"
        df_knockout = df_this_tour[~df_this_tour['stage'].astype(str).str.contains('בית', na=False)].sort_values(by='time')
        
        if df_knockout.empty:
            st.info("לא נמצאו משחקי חצי גמר או גמר לטורניר זה בלוח המשחקים.")
        else:
            # בדיקה האם כל משחקי הבתים של הטורניר הנוכחי הסתיימו
            group_games = df_this_tour[df_this_tour['stage'].astype(str).str.contains('בית', na=False)]
            is_group_done = group_games['score_a'].notna().all() if not group_games.empty else False
            status_text = "" if is_group_done else "<br><small style='color:gray;'>*(שלב הבתים טרם הסתיים)*</small>"
            
            # --- התיקון הקריטי להצלבה ---
            # שימוש בהשוואה מוחלטת (==) כדי שהאות 'ב' במילה 'בית' לא תהרוס את הסינון
            # שליפת קבוצות חצי הגמר
            group_a = df_standings[df_standings['stage'].astype(str).str.strip() == 'בית א']
            group_b = df_standings[df_standings['stage'].astype(str).str.strip() == 'בית ב']
            
            a1 = group_a.iloc[0]['team'] if len(group_a) > 0 else "מקום 1 בית א'"
            a2 = group_a.iloc[1]['team'] if len(group_a) > 1 else "מקום 2 בית א'"
            b1 = group_b.iloc[0]['team'] if len(group_b) > 0 else "מקום 1 בית ב'"
            b2 = group_b.iloc[1]['team'] if len(group_b) > 1 else "מקום 2 בית ב'"
            
            semi_counter = 0 
            df_semi_games = df_knockout[df_knockout['stage'].astype(str).str.contains('חצי', na=False)].sort_values(by='time')
            
            for idx, row in df_knockout.iterrows():
                ta = str(row['team_a']).strip()
                tb = str(row['team_b']).strip()
                stage_name = str(row['stage']).strip()
                field_name = str(row['field']).strip()
                
                game_header = f"🕒 **{row['time']}** | {stage_name} | 📍 מגרש: {field_name}"
                is_tbd = (ta == 'nan' or tb == 'nan' or ta == '' or tb == '')
                
                if is_tbd:
                    if 'חצי' in stage_name:
                        matchup = f"{a1} מול {b2}" if semi_counter == 0 else f"{b1} מול {a2}"
                        semi_counter += 1
                        prefix = "✅ **נקבע לחצי הגמר:**" if is_group_done else "🔮 **תמונת מצב משוערת:**"
                        st.markdown(f"{game_header} | {prefix} **{matchup}** {status_text}", unsafe_allow_html=True)
                    elif stage_name == 'גמר':
                        # תחזית לגמר המבוססת על האם חצאי הגמר הסתיימו
                        if len(df_semi_games) == 2 and df_semi_games['score_a'].notna().all() and df_semi_games['score_b'].notna().all():
                            s1 = df_semi_games.iloc[0]
                            w1 = str(s1['team_a']).strip() if float(s1['score_a']) > float(s1['score_b']) else str(s1['team_b']).strip()
                            s2 = df_semi_games.iloc[1]
                            w2 = str(s2['team_a']).strip() if float(s2['score_a']) > float(s2['score_b']) else str(s2['team_b']).strip()
                            st.markdown(f"{game_header} | ✅ **משחק הגמר:** **{w1} מול {w2}**", unsafe_allow_html=True)
                        else:
                            st.markdown(f"{game_header} | ⏳ **ממתין למנצחות בשלבי חצי הגמר**", unsafe_allow_html=True)
                else:
                    has_result = ui_components.has_match_result(row['score_a'], row['score_b'])

                    if has_result:
                        sa = int(float(row['score_a']))
                        sb = int(float(row['score_b']))

                        color_a = "green" if sa > sb else "red" if sa < sb else "orange"
                        color_b = "green" if sb > sa else "red" if sb < sa else "orange"

                        st.markdown(
                            f"✅ {game_header} | "
                            f"<span class='team-name-result' style='color:{color_a};'>{ta} ({sa})</span> - "
                            f"<span class='team-name-result' style='color:{color_b};'>({sb}) {tb}</span>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"🕒 {game_header} | **{ta} מול {tb}** | טרם שוחק",
                            unsafe_allow_html=True
                        )
                st.divider()
ui_components.render_app_footer()
