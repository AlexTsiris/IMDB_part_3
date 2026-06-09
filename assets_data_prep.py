import ast
import numpy as np
import pandas as pd

# עמודות שגורמות לזליגת נתונים - לא יכנסו למודל
LEAKAGE_COLUMNS = ["averageRating", "numVotes", "BoxOffice"]


def count_actors(actors_raw):
    # סופר כמה שחקנים יש ברשימה
    if pd.isna(actors_raw):
        return 0
    try:
        actors_list = ast.literal_eval(actors_raw)
        return len(actors_list)
    except (ValueError, SyntaxError):
        return 0


def clean_genres(genres_raw):
    # ניקוי סוגריים וגרשיים: ['Drama'] -> Drama
    if pd.isna(genres_raw):
        return ""
    cleaned = genres_raw.replace("[", "").replace("]", "")
    cleaned = cleaned.replace("'", "").replace('"', "")
    parts = [part.strip() for part in cleaned.split(",")]
    return ",".join(parts)


def prepare_data(df):
    # פונקציה זו מקבלת DataFrame גולמי ומחזירה את הפיצ'רים למודל
    movies_df = df.copy()

    # מוחקים עמודות שגורמות לזליגת נתונים
    movies_df = movies_df.drop(columns=LEAKAGE_COLUMNS, errors="ignore")

    # הגנה: אם חסרה עמודה ניצור אותה כריקה
    expected_cols = [
        "genres", "startYear", "runtimeMinutes", "lead_actors_ids",
        "primaryTitle", "Language", "Country", "budget"
    ]
    for col in expected_cols:
        if col not in movies_df.columns:
            movies_df[col] = np.nan

    # ניקוי ז'אנרים
    movies_df["genres"] = movies_df["genres"].apply(clean_genres)

    # startYear = 0 זו טעות בנתונים
    movies_df["startYear"] = movies_df["startYear"].replace(0, np.nan)

    # פיצ'ר: כמות ז'אנרים
    movies_df["num_genres"] = movies_df["genres"].apply(
        lambda g: len(g.split(",")) if g else 0
    )

    # פיצ'ר: ז'אנר ראשי
    movies_df["main_genre"] = movies_df["genres"].apply(
        lambda g: g.split(",")[0] if g else "Unknown"
    )

    # פיצ'ר: סיווג לפי משך הסרט
    runtime_bins   = [0, 70, 85, 100, 120, 150, 400]
    runtime_labels = [1, 2, 3, 4, 5, 6]
    movies_df["runtime_bin"] = pd.cut(
        movies_df["runtimeMinutes"], bins=runtime_bins, labels=runtime_labels
    ).astype("float")

    # פיצ'ר: יחס משך הסרט / מספר ז'אנרים
    movies_df["runtime_per_genre"] = np.where(
        movies_df["num_genres"] > 0,
        movies_df["runtimeMinutes"] / movies_df["num_genres"],
        np.nan
    )

    # פיצ'ר: כמה שחקנים בסרט
    movies_df["num_actors"] = movies_df["lead_actors_ids"].apply(count_actors)

    # פיצ'ר: האם אין שחקנים (בינארי)
    movies_df["is_no_cast"] = (movies_df["num_actors"] == 0).astype(int)

    # פיצ'ר: כמה מילים בשם הסרט
    movies_df["title_word_count"] = (
        movies_df["primaryTitle"].fillna("").apply(lambda t: len(t.split()))
    )

    # פיצ'ר: האם יש נקודתיים בשם הסרט
    movies_df["title_has_colon"] = (
        movies_df["primaryTitle"].fillna("").str.contains(":").astype(int)
    )

    # פיצ'ר: האם השפה אנגלית
    movies_df["is_english"] = (movies_df["Language"] == "English").astype(int)

    # פיצ'ר: האם הסרט מארה"ב
    movies_df["is_us"] = (movies_df["Country"] == "United States").astype(int)

    # פיצ'ר: האם קיים תקציב
    movies_df["has_budget"] = movies_df["budget"].notna().astype(int)

    feature_columns = [
        "startYear", "runtimeMinutes",
        "num_genres", "main_genre",
        "runtime_bin", "runtime_per_genre",
        "num_actors", "is_no_cast",
        "title_word_count", "title_has_colon",
        "is_english", "is_us",
        "has_budget",
    ]

    # בדיקה: לוודא שאין זליגת נתונים
    assert not (set(LEAKAGE_COLUMNS) & set(feature_columns)), "Leakage column detected!"

    return movies_df[feature_columns]
