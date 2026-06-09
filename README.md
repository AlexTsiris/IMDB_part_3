# Movie Rating Predictor – Part 3

אפליקציית Flask לחיזוי דירוג ממוצע של סרט לפני יציאתו לאקרנים.

## תיאור

הפרויקט עוטף את מודל ה-Random Forest שפותח בחלק 2 בשירות ווב.  
המשתמש ממלא פרטי סרט בטופס, לוחץ **Predict Rating**, ומקבל תחזית בין 1.0 ל-10.0.

## מבנה הקבצים

| קובץ | תיאור |
|------|--------|
| `api.py` | שרת Flask – שתי נקודות קצה: GET `/` ו-POST `/predict` |
| `index.html` | ממשק המשתמש – טופס קלט והצגת תוצאה |
| `assets_data_prep.py` | פונקציית `prepare_data()` מחלק 2 |
| `trained_model.pkl` | מודל Random Forest מאומן |
| `requirements.txt` | כל הספריות הנדרשות |

## התקנה

```bash
# 1. יצירת סביבה וירטואלית
python -m venv venv
venv\Scripts\activate        # Windows

# 2. התקנת ספריות
pip install -r requirements.txt
```

> **חשוב:** המודל נשמר עם **scikit-learn 1.2.2** ו-**Python 3.11**.  
> יש להשתמש באותן גרסאות (Anaconda מכיל אותן).

## הפעלה

```bash
python api.py
```

לאחר מכן פתח דפדפן בכתובת: **http://localhost:5000**

## שדות הקלט

| שדה | חובה | טווח / פורמט |
|-----|------|--------------|
| שם הסרט (`primaryTitle`) | כן | טקסט חופשי |
| ז'אנרים (`genres`) | כן | מופרדים בפסיק, לדוגמה: `Action,Drama` |
| שנת יציאה (`startYear`) | כן | 1900 – 2030 |
| משך הסרט (`runtimeMinutes`) | כן | 1 – 400 דקות |
| שפה (`Language`) | לא | לדוגמה: `English`, `Hebrew` |
| מדינת ייצור (`Country`) | לא | לדוגמה: `United States` |
| שחקנים ראשיים (`lead_actors_ids`) | לא | רשימת מזהים, לדוגמה: `['nm0000138']` |
| תקציב (`budget`) | לא | מספר בדולרים |

## שמות חברי הצוות

- אלכסנדר צירס
