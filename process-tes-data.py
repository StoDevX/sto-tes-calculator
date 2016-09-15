import datetime
import json
import sys
import re

SHORT_MONTH_NAMES = [
    'jan', 'feb', 'mar', 'apr', 'may', 'jun',
    'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
]

LONG_MONTH_NAMES = [
    'january', 'february', 'march', 'april', 'may',
    'june', 'july', 'august', 'september', 'october',
    'november', 'december',
]

def parse_date_from_job_overview(tes_date_string):
    # example: Sep 10, 2015
    # example: May 24, 2016
    DATE_REGEX = re.compile(r'(?P<month>[a-z]{3}) (?P<day>\d+), (?P<year>\d{4})', re.IGNORECASE)
    match = DATE_REGEX.match(tes_date_string.lower())
    if not match:
        raise ValueError('Invalid date assumptions! (for %s)' % tes_date_string)
    groups = match.groupdict()
    year = int(groups['year'])
    # the +1 is because `datetime` wants months between 1..12
    month = SHORT_MONTH_NAMES.index(groups['month']) + 1
    day = int(groups['day'])
    return datetime.datetime(year, month, day)


def parse_date_from_timecard_entry(tes_date_string, year):
    # example: Wed, Sep 7
    # example: Sat, Sep 3
    DATE_REGEX = re.compile(r'(?P<weekday>[a-z]{3}), (?P<month>[a-z]{3}) (?P<day>\d+)', re.IGNORECASE)
    match = DATE_REGEX.match(tes_date_string.lower())
    if not match:
        raise ValueError('Invalid date assumptions! (for %s)' % tes_date_string)
    groups = match.groupdict()
    # the +1 is because `datetime` wants months between 1..12
    month = SHORT_MONTH_NAMES.index(groups['month']) + 1
    day = int(groups['day'])
    return datetime.datetime(year, month, day)


def parse_dates_from_pay_period(tes_date_string):
    # example: September 3, 2016 - September 7, 2016
    # example: August 6, 2016 - August 19, 2016

    dates = tes_date_string.lower().split(' - ')
    DATE_REGEX = re.compile(r'(?P<month>[a-z]+) (?P<day>\d+), (?P<year>\d{4})', re.IGNORECASE)
    results = {}
    for i, date_string in enumerate(dates):
        match = DATE_REGEX.match(date_string)
        if not match:
            raise ValueError('Invalid date assumptions! (for %s, specifically %s)' % (tes_date_string, date_string))
        groups = match.groupdict()
        year = int(groups['year'])
        # the +1 is because `datetime` wants months between 1..12
        month = LONG_MONTH_NAMES.index(groups['month']) + 1
        day = int(groups['day'])
        if i is 0:
            results['from'] = datetime.datetime(year, month, day)
        elif i is 1:
            results['to'] = datetime.datetime(year, month, day)
    return results


def timestring_to_datetime(time_str, date):
    # example: "2:00 PM",
    # example: "12:30 PM"
    # example: "10:10 AM"
    TIME_REGEX = re.compile(r'(?P<hour>\d+):(?P<minute>\d{2}) (?P<ordinal>AM|PM)')
    match = TIME_REGEX.match(time_str.upper())
    if not match:
        raise ValueError('Invalid date assumptions! (for %s)' % time_str)
    groups = match.groupdict()
    hour = int(groups['hour'])
    if groups['ordinal'] == 'PM' and hour is not 12:
        hour += 12
    minute = int(groups['minute'])

    date = date.replace(hour=hour)
    date = date.replace(minute=minute)
    return date

def entry_to_date(entry_pair, date):
    return {
        'from': timestring_to_datetime(entry_pair[0], date),
        'to': timestring_to_datetime(entry_pair[1], date),
    }


def entries_to_dates(hours_entry, year):
    date = hours_entry['Date']
    entries = hours_entry['Entries']
    day = parse_date_from_timecard_entry(date, year)
    return [entry_to_date(entry, day) for entry in entries]

def checkAllSame(iterator):
   return len(set(iterator)) <= 1


def process_data(data):
    for job in data['jobs']:
        job['Rate'] = float(job['Rate'][1:])
        job['Start'] = parse_date_from_job_overview(job['Start'])
        job['End'] = parse_date_from_job_overview(job['End'])
        for card in job['Timecards']:
            card['Pay Period'] = parse_dates_from_pay_period(card['Pay Period'])
            if not checkAllSame([date.year for date in card['Pay Period'].values()]):
                raise ValueError('not all dates are from the same year! {}'.format(json.dumps(job)))
            year = card['Pay Period']['from'].year

            card['Total Hours'] = float(card['Total Hours'])

            card['Entries'] = [entries_to_dates(hours_entry, year) for hours_entry in card['Hours']]
            card['Entries'] = [entry for entry in card['Entries'] if entry]
            del card['Hours']

    return data


def date_handler(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return None


def to_json(data):
    return json.dumps(data,
                      default=date_handler,
                      sort_keys=True,
                      separators=(',', ': '),
                      indent=4)

def main():
    jobs = json.load(sys.stdin)
    work_award = sys.argv[2] if len(sys.argv) >= 2 else 2300

    if not jobs:
        print('Usage:')
        print('python3 fetch-tes-data.py | python3 process-tes-data.py [AWARD=2300]')
        print('python3 fetch-tes-data.py > tes.json && python3 process-tes-data.py [AWARD=2300] < tes.json')
        sys.exit(1)

    data = {
        'award': work_award,
        'jobs': jobs,
    }

    print(to_json(process_data(data)))


if __name__ == '__main__':
    main()
