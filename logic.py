# קובץ logic.py
import pandas as pd
from config import WIN_POINTS, TIE_POINTS, LOSS_POINTS

def filter_by_tournament(df_games, tournament_name):
    """
    מסנן את הלו"ז המלא לפי הטורניר הנבחר בקישור.
    """
    # שינוי לעמודה הנכונה: competition_name במקום tournament_name
    if 'competition_name' in df_games.columns:
        # נוודא שהסינון לא נופל על רווחים מיותרים או מרכאות כפולות שמגיעות מה-CSV
        df_games['competition_name'] = df_games['competition_name'].astype(str).str.replace('"', '').str.strip()
        return df_games[df_games['competition_name'] == tournament_name]
    return df_games

def calculate_standings(df_games):
    """
    מחשב את טבלת הבתים. מציג את כל הקבוצות עם 0 נקודות גם לפני שהתחילו לשחק.
    """
    # סינון רק למשחקי שלב הבתים
    group_games = df_games[df_games['stage'].astype(str).str.contains('בית', na=False)]
    standings = {}
    
    # 1. הקמת טבלה: עוברים על כל המשחקים, ויוצרים "כרטיס קבוצה" עם 0 נקודות לכל מי שמופיעה
    for index, row in group_games.iterrows():
        stage = str(row['stage']).strip()
        ta = str(row['team_a']).strip()
        tb = str(row['team_b']).strip()
        
        if ta and ta != 'nan' and ta not in standings:
            standings[ta] = {'stage': stage, 'team': ta, 'points': 0, 'goals_for': 0, 'goals_against': 0, 'matches': 0}
        if tb and tb != 'nan' and tb not in standings:
            standings[tb] = {'stage': stage, 'team': tb, 'points': 0, 'goals_for': 0, 'goals_against': 0, 'matches': 0}

    # 2. סינון משחקים ששוחקו בפועל כדי לעדכן נקודות
    played_games = group_games.dropna(subset=['score_a', 'score_b'])
    
    for index, row in played_games.iterrows():
        ta = str(row['team_a']).strip()
        tb = str(row['team_b']).strip()
        
        try:
            sa = int(float(row['score_a']))
            sb = int(float(row['score_b']))
        except (ValueError, TypeError):
            continue 
            
        if ta in standings and tb in standings:
            standings[ta]['matches'] += 1
            standings[tb]['matches'] += 1
            standings[ta]['goals_for'] += sa
            standings[ta]['goals_against'] += sb
            standings[tb]['goals_for'] += sb
            standings[tb]['goals_against'] += sa
            
            # חלוקת נקודות לפי ניצחון/הפסד/תיקו מתוך ה-config
            from config import WIN_POINTS, TIE_POINTS, LOSS_POINTS
            if sa > sb:
                standings[ta]['points'] += WIN_POINTS
                standings[tb]['points'] += LOSS_POINTS
            elif sa < sb:
                standings[tb]['points'] += WIN_POINTS
                standings[ta]['points'] += LOSS_POINTS
            else:
                standings[ta]['points'] += TIE_POINTS
                standings[tb]['points'] += TIE_POINTS

    if not standings:
        return pd.DataFrame()

    # חישוב הפרש שערים
    for team in standings:
        standings[team]['goal_diff'] = standings[team]['goals_for'] - standings[team]['goals_against']

    df_standings = pd.DataFrame(standings.values())    
    # 1. מיון ראשוני לפי: בית -> נקודות -> הפרש שערים -> שערי זכות
    df_standings = df_standings.sort_values(
        by=['stage', 'points', 'goal_diff', 'goals_for'], 
        ascending=[True, False, False, False] 
    ).reset_index(drop=True)
    
    # 2. לוגיקת ראש בראש כשובר שוויון סופי בהחלט 
    # (מופעלת רק אם יש שוויון *מוחלט* בנקודות, הפרש שערים ושערי זכות בין 2 קבוצות)
    for stage in df_standings['stage'].unique():
        stage_mask = df_standings['stage'] == stage
        stage_indices = df_standings[stage_mask].index.tolist()
        
        i = 0
        while i < len(stage_indices) - 1:
            idx1 = stage_indices[i]
            idx2 = stage_indices[i+1]
            
            # שולפים את כל הנתונים הרלוונטיים לשובר השוויון
            pts1 = df_standings.at[idx1, 'points']
            gd1 = df_standings.at[idx1, 'goal_diff']
            gf1 = df_standings.at[idx1, 'goals_for']
            
            pts2 = df_standings.at[idx2, 'points']
            gd2 = df_standings.at[idx2, 'goal_diff']
            gf2 = df_standings.at[idx2, 'goals_for']
            
            # בודקים שוויון *מוחלט* בכל שלושת הפרמטרים
            if pts1 == pts2 and gd1 == gd2 and gf1 == gf2:
                # מוודאים שזה לא שוויון משולש (3 קבוצות עם נתונים זהים לחלוטין)
                if i + 2 < len(stage_indices) and (df_standings.at[stage_indices[i+2], 'points'] == pts1 and 
                                                   df_standings.at[stage_indices[i+2], 'goal_diff'] == gd1 and 
                                                   df_standings.at[stage_indices[i+2], 'goals_for'] == gf1):
                    while i < len(stage_indices) - 1 and df_standings.at[stage_indices[i+1], 'points'] == pts1:
                        i += 1
                    continue
                
                # מצאנו בדיוק שתי קבוצות עם שוויון מוחלט בכל הפרמטרים. נבדוק את המשחק הישיר ביניהן.
                team1 = df_standings.at[idx1, 'team']
                team2 = df_standings.at[idx2, 'team']
                
                match = played_games[
                    ((played_games['team_a'] == team1) & (played_games['team_b'] == team2)) |
                    ((played_games['team_a'] == team2) & (played_games['team_b'] == team1))
                ]
                
                if not match.empty:
                    row = match.iloc[0]
                    try:
                        # מזהים כמה שערים הבקיעה כל אחת במפגש הישיר
                        score1 = float(row['score_a']) if row['team_a'] == team1 else float(row['score_b'])
                        score2 = float(row['score_b']) if row['team_a'] == team1 else float(row['score_a'])
                        
                        # אם הקבוצה שמתחת (team2) למעשה ניצחה את הראשונה, מחליפים ביניהן בטבלה
                        if score2 > score1:
                            temp = df_standings.loc[idx1].copy()
                            df_standings.loc[idx1] = df_standings.loc[idx2]
                            df_standings.loc[idx2] = temp
                    except (ValueError, TypeError):
                        pass
            i += 1

    return df_standings

def update_knockout_stages(df):
    """
    פונקציה זו רצה על כל מסד הנתונים ומבצעת "יישור קו" של כל שלבי הנוקאאוט.
    היא פותרת את בעיית "מצב הביניים" (Cascade Reset):
    - אם שלב הבתים מלא -> משבצת קבוצות לחצי גמר.
    - אם משחק בבית בוטל/נערך -> מוחקת מיד את שיבוצי חצי הגמר והגמר של אותו טורניר.
    - אם חצאי הגמר הסתיימו -> משבצת מנצחות לגמר.
    - אם חצי גמר בוטל -> מוחקת את הגמר.
    """
    import pandas as pd
    
    # עוברים על כל טורניר (שכבת גיל) בנפרד
    tournaments = df['tournament_name'].dropna().unique()

    for tour in tournaments:
        # סינון משחקי הטורניר הנוכחי (למשל: "טורניר ה'")
        tour_mask = df['tournament_name'] == tour
        df_tour = df[tour_mask]

        # יצירת מסננים לפי שלבים עבור הטורניר הנוכחי
        group_mask = tour_mask & df['stage'].astype(str).str.contains('בית', na=False)
        semi_mask = tour_mask & df['stage'].astype(str).str.contains('חצי', na=False)
        final_mask = tour_mask & (df['stage'].astype(str).str.strip() == 'גמר')

        df_group = df[group_mask]
        
        # --- שלב 1: בדיקת שלב הבתים ועדכון חצאי הגמר ---
        if not df_group.empty:
            # האם כל משחקי הבתים שוחקו? (לכולם יש תוצאה חוקית)
            group_completed = df_group['score_a'].notna().all() and df_group['score_b'].notna().all()

            if group_completed:
                # הבתים הסתיימו! נחשב מיקומים ונעלה לחצי הגמר
                standings = calculate_standings(df_tour)
                group_a = standings[standings['stage'].astype(str).str.strip() == 'בית א']
                group_b = standings[standings['stage'].astype(str).str.strip() == 'בית ב']

                # נוודא שיש לפחות שתי קבוצות בכל בית (למניעת קריסות אם חסר נתון)
                if len(group_a) >= 2 and len(group_b) >= 2:
                    a1, a2 = group_a.iloc[0]['team'], group_a.iloc[1]['team']
                    b1, b2 = group_b.iloc[0]['team'], group_b.iloc[1]['team']
                    # נשלוף את שורות חצי הגמר מהדאטה ונסדר כרונולוגית (הראשון והשני)
                    semi_indices = df[semi_mask].sort_values(by='time').index

                    if len(semi_indices) == 2:
                        # שיבוץ חצי הגמר הראשון (מקום 1 בית א' נגד מקום 2 בית ב')
                        df.at[semi_indices[0], 'team_a'] = a1
                        df.at[semi_indices[0], 'team_b'] = b2
                        # שיבוץ חצי הגמר השני (מקום 1 בית ב' נגד מקום 2 בית א')
                        df.at[semi_indices[1], 'team_a'] = b1
                        df.at[semi_indices[1], 'team_b'] = a2
            else:
                # שלב הבתים חסר או שאופס בו משחק (Cascade Reset)
                # נרוקן בכוח גם את חצי הגמר וגם את הגמר!
                for col in ['team_a', 'team_b', 'score_a', 'score_b']:
                    df.loc[semi_mask, col] = float('nan')
                    df.loc[final_mask, col] = float('nan')
                # מדלגים לטורניר הבא - אין טעם לבדוק חצאי גמר שכרגע רוקנו
                continue

        # --- שלב 2: בדיקת חצאי הגמר ועדכון הגמר ---
        df_semi = df[semi_mask]
        if not df_semi.empty:
            # האם שני חצאי הגמר הסתיימו?
            semi_completed = df_semi['score_a'].notna().all() and df_semi['score_b'].notna().all()
            # נוודא שבכלל יש קבוצות שמשובצות שם (אם זה כרגע אופס, שלא ננסה לקרוא)
            teams_assigned = df_semi['team_a'].notna().all() and df_semi['team_b'].notna().all()

            if semi_completed and teams_assigned and len(df_semi) == 2:
                # חצאי הגמר הסתיימו - קובעים מי עלה לגמר
                df_semi_sorted = df_semi.sort_values(by='time')
                s1, s2 = df_semi_sorted.iloc[0], df_semi_sorted.iloc[1]

                w1 = s1['team_a'] if float(s1['score_a']) > float(s1['score_b']) else s1['team_b']
                w2 = s2['team_a'] if float(s2['score_a']) > float(s2['score_b']) else s2['team_b']

                final_indices = df[final_mask].index
                if len(final_indices) >= 1:
                    df.at[final_indices[0], 'team_a'] = w1
                    df.at[final_indices[0], 'team_b'] = w2
            else:
                # חצאי הגמר חסרים או שאופסו בהם תוצאות
                # נאפס את הקבוצות והתוצאות של משחק הגמר בלבד
                for col in ['team_a', 'team_b', 'score_a', 'score_b']:
                    df.loc[final_mask, col] = float('nan')

    return df