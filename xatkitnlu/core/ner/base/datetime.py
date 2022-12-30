from datetime import datetime
from zoneinfo import ZoneInfo

from dateparser.search import search_dates

from xatkitnlu.utils.utils import replace_value_in_sentence
from xatkitnlu.core.nlp_configuration import NlpConfiguration


relative_time_parser = ['relative-time']
date_parsers = ['custom-formats', 'absolute-time']


def ner_datetime(sentence: str, configuration: NlpConfiguration) -> tuple[str, str, dict]:
    matched_frag: str = None
    matched_dt: datetime = None

    timezone = ZoneInfo(configuration.timezone)
    now = datetime.now(tz=timezone).replace(microsecond=0)

    date_match, relative_time_match = False, False

    relative_time_matches: list[tuple[str, datetime]] = search_datetimes(sentence, now, configuration.country,
                                                                         relative_time_parser)
    if relative_time_matches is not None:
        matched_frag, matched_dt = relative_time_matches[0]
        relative_time_match = True
    else:
        date_matches: list[tuple[str, datetime]] = search_datetimes(sentence, now, configuration.country, date_parsers)
        if date_matches is not None:
            matched_frag, matched_dt = date_matches[0]
            date_match = True

    if matched_frag is None or matched_dt is None:
        return None, None, None

    formatted_frag = matched_dt.isoformat()
    datetime_params_info: dict[str, bool]
    if date_match:
        datetime_params_info = set_datetime_params_info_datetime(sentence, configuration)
    else:
        datetime_params_info = set_datetime_params_info_relative_time(matched_frag, configuration)
    sentence = replace_value_in_sentence(sentence, matched_frag, formatted_frag)
    return sentence, formatted_frag, datetime_params_info


def set_datetime_params_info_datetime(sentence: str, configuration: NlpConfiguration) -> dict[str, bool]:
    test_datetime_1 = datetime(year=2001, month=1, day=1, hour=1, minute=1, second=1)
    test_datetime_2 = datetime(year=2002, month=2, day=2, hour=2, minute=2, second=2)
    dt1: datetime = search_datetimes(sentence, test_datetime_1, configuration.country, date_parsers)[0][1]
    dt2: datetime = search_datetimes(sentence, test_datetime_2, configuration.country, date_parsers)[0][1]
    # Since sometimes the time is set to 00:00:00 by default, we consider that if this happens, it is because the time
    # is not explicitly said in the sentence
    time_is_zero = dt1.hour == 0 and dt1.minute == 0 and dt1.second == 0 and dt2.hour == 0 and dt2.minute == 0 and dt2.second == 0
    return set_datetime_params_info(dt1.year == dt2.year,
                                    dt1.month == dt2.month,
                                    dt1.day == dt2.day,
                                    dt1.hour == dt2.hour and not time_is_zero,
                                    dt1.minute == dt2.minute and not time_is_zero,
                                    dt1.second == dt2.second and not time_is_zero)


def set_datetime_params_info_relative_time(date_text: str, configuration: NlpConfiguration) -> dict[str, bool]:
    w_Y = {
        'en': ['year', 'years'],
        'ca': ['any', 'anys'],
        'es': ['año', 'años']
    }
    w_MO = {
        'en': ['month', 'months'],
        'ca': ['mes', 'mes'],
        'es': ['mes', 'mes']
    }
    w_D = {
        'en': ['day', 'days'],
        'ca': ['dia', 'dies'],
        'es': ['día', 'dia', 'días', 'dias']
    }
    w_H = {
        'en': ['hour', 'hours'],
        'ca': ['hora', 'hores'],
        'es': ['hora', 'horas']
    }
    w_MI = {
        'en': ['minute', 'minutes'],
        'ca': ['minut', 'minuts'],
        'es': ['minuto', 'minutos']
    }
    w_S = {
        'en': ['second', 'seconds'],
        'ca': ['segon', 'segons'],
        'es': ['segundo', 'segundos']
    }

    if any(w in date_text for w in w_S[configuration.country]):
        return set_datetime_params_info(year=True, month=True, day=True, hour=True, minute=True, second=True)
    elif any(w in date_text for w in w_MI[configuration.country]):
        return set_datetime_params_info(year=True, month=True, day=True, hour=True, minute=True, second=False)
    elif any(w in date_text for w in w_H[configuration.country]):
        return set_datetime_params_info(year=True, month=True, day=True, hour=True, minute=False, second=False)
    elif any(w in date_text for w in w_D[configuration.country]):
        return set_datetime_params_info(year=True, month=True, day=True, hour=False, minute=False, second=False)
    elif any(w in date_text for w in w_MO[configuration.country]):
        return set_datetime_params_info(year=True, month=True, day=False, hour=False, minute=False, second=False)
    elif any(w in date_text for w in w_Y[configuration.country]):
        return set_datetime_params_info(year=True, month=False, day=False, hour=False, minute=False, second=False)
    else:
        # today, tomorrow...
        return set_datetime_params_info(year=True, month=True, day=True, hour=False, minute=False, second=False)


def set_datetime_params_info(year: bool, month: bool, day: bool, hour: bool, minute: bool, second: bool) -> dict[str, bool]:
    return {
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'minute': minute,
        'second': second
    }


def search_datetimes(sentence: str, relative_base: datetime, language: str, parsers: list[str]) -> list[tuple[str, datetime]]:
    date_order = 'MDY'
    if language == 'es' or language == 'ca':
        date_order = 'DMY'

    sett = {'PREFER_DAY_OF_MONTH': 'current', # current / first / last
            'PREFER_DATES_FROM': 'current_period', # current_period, past, future
            'RETURN_AS_TIMEZONE_AWARE': True,
            'RELATIVE_BASE': relative_base,
            'DATE_ORDER': date_order,
            'PARSERS': parsers}
    matches: list[tuple[str, datetime]] = search_dates(sentence,
                                                       languages=[language],
                                                       settings=sett)
    return matches
