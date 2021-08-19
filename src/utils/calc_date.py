from datetime import date, timedelta

def plus_weeks_from_today(weeks: int) -> date:
    today = date.today()
    t_weeks = timedelta(weeks=weeks)

    result_date = today + t_weeks   
    return result_date