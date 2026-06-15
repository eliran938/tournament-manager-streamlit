import pandas as pd

file_name = 'beit-el-2026.xlsx'

print("--- מתחיל בהשוואה בין הלוז החזותי לטבלה השטוחה ---")

# 1. קריאת שתי הלשוניות מהאקסל
df_flat = pd.read_excel(file_name, sheet_name='luz_game')
df_visual = pd.read_excel(file_name, sheet_name='luz_beit_el')

# 2. ניקוי רווחים מיותרים בטבלה השטוחה (למניעת שגיאות קטנות של רווח)
df_flat['field'] = df_flat['field'].astype(str).str.strip()
df_flat['time'] = df_flat['time'].astype(str).str.strip().str[:5] # חיתוך לפורמט שעות ודקות (למשל 16:00)
df_flat['team_a'] = df_flat['team_a'].astype(str).str.strip()
df_flat['team_b'] = df_flat['team_b'].astype(str).str.strip()

errors = []

# 3. מעבר על כל שורה ושורה בלו"ז החזותי
for index, row in df_visual.iterrows():
    # השעה נמצאת בעמודה הראשונה
    time_val = str(row.iloc[0]).strip()
    
    # נדלג על שורות ריקות או שורות כותרת (שאין בהן נקודתיים של שעה)
    if ':' not in time_val:
        continue
        
    time_val = time_val[:5] # חיתוך לפורמט 16:00
    
    # נעבור על זוגות עמודות בלו"ז החזותי (שמייצגות קבוצה א' וקבוצה ב' באותו מגרש)
    # עמודות 1+2 (מגרש 1), עמודות 3+4 (מגרש 2) וכו'
    for i in range(1, len(df_visual.columns), 2):
        if i + 1 < len(df_visual.columns):
            team_a = str(row.iloc[i]).strip()
            team_b = str(row.iloc[i+1]).strip()
            
            # אם יש קבוצות בתאים האלו (ולא תאים ריקים)
            if team_a != 'nan' and team_b != 'nan' and team_a != '' and team_b != '':
                
                # נסנן החוצה בינתיים את השמות הזמניים של משחקי הגמר (1 תכלת, 2 צהוב וכו')
                if 'תכלת' in team_a or 'צהוב' in team_a or 'אדום' in team_a or 'ירוק' in team_a:
                    continue
                
                # שם המגרש נמצא בכותרת העליונה של אותה עמודה
                field_name = str(df_visual.columns[i]).strip()
                
                # עכשיו מחפשים את המשחק הזה בטבלה השטוחה
                # אנחנו בודקים את שני הכיוונים (גם א' נגד ב' וגם ב' נגד א')
                match = df_flat[
                    ((df_flat['team_a'] == team_a) & (df_flat['team_b'] == team_b)) |
                    ((df_flat['team_a'] == team_b) & (df_flat['team_b'] == team_a))
                ]
                
                if match.empty:
                    errors.append(f"❌ המשחק: {team_a} נגד {team_b} (מופיע בחזותי ב-{time_val} במגרש '{field_name}') לא נמצא בטבלה השטוחה!")
                else:
                    # המשחק קיים! עכשיו נבדוק שהשעה והמגרש תואמים במדויק
                    flat_time = match.iloc[0]['time']
                    flat_field = match.iloc[0]['field']
                    
                    if flat_time != time_val or flat_field != field_name:
                        errors.append(f"⚠️ אי התאמה במשחק {team_a} נגד {team_b}:\n   בלוז החזותי: שעה {time_val}, מגרש '{field_name}'\n   בטבלה השטוחה: שעה {flat_time}, מגרש '{flat_field}'\n")

# 4. הדפסת התוצאות
if len(errors) == 0:
    print("\n✅ מדהים! כל המשחקים משלב הבתים בלוז החזותי תואמים לחלוטין לשעה ולמגרש בטבלה השטוחה. אין פספוסים!")
else:
    print("\nמצאתי את הפערים הבאים:")
    for error in errors:
        print(error)
        
print("\n--- סיום השוואה ---")