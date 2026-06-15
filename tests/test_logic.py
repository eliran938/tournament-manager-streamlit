import pandas as pd
import logic


def make_basic_tournament_df():
    return pd.DataFrame([
        # בית א
        {
            "competition_name": "טורניר בית אל (בנימין)",
            "tournament_name": "טורניר ד",
            "stage": "בית א",
            "time": "10:00",
            "field": "1",
            "team_a": "אריות",
            "team_b": "נשרים",
            "score_a": 2,
            "score_b": 0,
        },
        {
            "competition_name": "טורניר בית אל (בנימין)",
            "tournament_name": "טורניר ד",
            "stage": "בית א",
            "time": "10:20",
            "field": "1",
            "team_a": "אריות",
            "team_b": "זאבים",
            "score_a": 1,
            "score_b": 1,
        },
        {
            "competition_name": "טורניר בית אל (בנימין)",
            "tournament_name": "טורניר ד",
            "stage": "בית א",
            "time": "10:40",
            "field": "1",
            "team_a": "נשרים",
            "team_b": "זאבים",
            "score_a": 0,
            "score_b": 3,
        },

        # בית ב
        {
            "competition_name": "טורניר בית אל (בנימין)",
            "tournament_name": "טורניר ד",
            "stage": "בית ב",
            "time": "11:00",
            "field": "2",
            "team_a": "ברקים",
            "team_b": "כרישים",
            "score_a": 1,
            "score_b": 0,
        },
        {
            "competition_name": "טורניר בית אל (בנימין)",
            "tournament_name": "טורניר ד",
            "stage": "בית ב",
            "time": "11:20",
            "field": "2",
            "team_a": "ברקים",
            "team_b": "פנתרים",
            "score_a": 2,
            "score_b": 2,
        },
        {
            "competition_name": "טורניר בית אל (בנימין)",
            "tournament_name": "טורניר ד",
            "stage": "בית ב",
            "time": "11:40",
            "field": "2",
            "team_a": "כרישים",
            "team_b": "פנתרים",
            "score_a": 0,
            "score_b": 1,
        },

        # חצאי גמר — בהתחלה ריקים
        {
            "competition_name": "טורניר בית אל (בנימין)",
            "tournament_name": "טורניר ד",
            "stage": "חצי גמר",
            "time": "12:00",
            "field": "1",
            "team_a": float("nan"),
            "team_b": float("nan"),
            "score_a": float("nan"),
            "score_b": float("nan"),
        },
        {
            "competition_name": "טורניר בית אל (בנימין)",
            "tournament_name": "טורניר ד",
            "stage": "חצי גמר",
            "time": "12:20",
            "field": "2",
            "team_a": float("nan"),
            "team_b": float("nan"),
            "score_a": float("nan"),
            "score_b": float("nan"),
        },

        # גמר
        {
            "competition_name": "טורניר בית אל (בנימין)",
            "tournament_name": "טורניר ד",
            "stage": "גמר",
            "time": "13:00",
            "field": "1",
            "team_a": float("nan"),
            "team_b": float("nan"),
            "score_a": float("nan"),
            "score_b": float("nan"),
        },
    ])


def test_calculate_standings_orders_teams_correctly():
    df = make_basic_tournament_df()

    standings = logic.calculate_standings(df)

    group_a = standings[standings["stage"] == "בית א"]
    group_b = standings[standings["stage"] == "בית ב"]

    assert group_a.iloc[0]["team"] == "זאבים"
    assert group_a.iloc[1]["team"] == "אריות"

    assert group_b.iloc[0]["team"] == "ברקים"
    assert group_b.iloc[1]["team"] == "פנתרים"


def test_update_knockout_assigns_semifinals_when_groups_done():
    df = make_basic_tournament_df()

    updated = logic.update_knockout_stages(df)

    semis = updated[updated["stage"].str.contains("חצי", na=False)].sort_values("time")

    assert semis.iloc[0]["team_a"] == "זאבים"
    assert semis.iloc[0]["team_b"] == "פנתרים"

    assert semis.iloc[1]["team_a"] == "ברקים"
    assert semis.iloc[1]["team_b"] == "אריות"


def test_update_knockout_clears_semis_if_group_result_deleted():
    df = make_basic_tournament_df()

    updated = logic.update_knockout_stages(df)

    # עכשיו מוחקים תוצאה אחת מבית א
    updated.loc[0, "score_a"] = float("nan")
    updated.loc[0, "score_b"] = float("nan")

    updated_again = logic.update_knockout_stages(updated)

    semis = updated_again[updated_again["stage"].str.contains("חצי", na=False)]
    final = updated_again[updated_again["stage"] == "גמר"]

    assert semis["team_a"].isna().all()
    assert semis["team_b"].isna().all()
    assert final["team_a"].isna().all()
    assert final["team_b"].isna().all()


def test_update_knockout_assigns_final_after_semis_done():
    df = make_basic_tournament_df()
    updated = logic.update_knockout_stages(df)

    semis_index = updated[updated["stage"].str.contains("חצי", na=False)].sort_values("time").index

    # חצי גמר 1: זאבים מנצחים את פנתרים
    updated.loc[semis_index[0], "score_a"] = 2
    updated.loc[semis_index[0], "score_b"] = 1

    # חצי גמר 2: אריות מנצחים את ברקים
    updated.loc[semis_index[1], "score_a"] = 0
    updated.loc[semis_index[1], "score_b"] = 1

    updated = logic.update_knockout_stages(updated)

    final = updated[updated["stage"] == "גמר"].iloc[0]

    assert final["team_a"] == "זאבים"
    assert final["team_b"] == "אריות"