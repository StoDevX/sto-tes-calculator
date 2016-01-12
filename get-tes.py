#!/usr/bin/python
# coding=utf-8

import re
import os
import sys
import json
from datetime import datetime
from urlparse import parse_qs

from ordereddict import OrderedDict
import requests
from bs4 import BeautifulSoup as bs


MONTHS = [
    'june', 'july', 'august',
    'september', 'october', 'november', 'december',
    'january', 'february', 'march', 'april', 'may',
]


def sort_month_names(month_name):
    return MONTHS.index(month_name.lower())


DATE_REGEX = re.compile(ur'(?P<month>[A-Z]{3}) (?P<day>\d+), (?P<year>\d{4})', re.IGNORECASE)
SHORT_MONTH_NAMES = [
    'jan',
    'feb',
    'mar',
    'apr',
    'may',
    'jun',
    'jul',
    'aug',
    'sep',
    'oct',
    'nov',
    'dec',
]


def parse_date(tes_date_string):
    # example: Sep 10, 2015
    # example: May 24, 2016
    match = DATE_REGEX.match(tes_date_string)
    if not match:
        raise ValueError('Invalid date assumptions!')
    groups = match.groupdict()
    year = int(groups['year'])
    # the +1 is because it wants months between 1..12
    month = SHORT_MONTH_NAMES.index(groups['month'].lower()) + 1
    day = int(groups['day'])
    return datetime(year, month, day)


def get_jobs(username, password):
    tes_base = 'https://www.stolaf.edu/apps/tes/'
    login_url = 'https://www.stolaf.edu/apps/tes/index.cfm?fuseaction=login.processLogin'
    login_error = 'http://www.stolaf.edu/apps/tes/index.cfm?fuseaction=login.login&error=1'

    credentials = {'username': username, 'password': password}

    s = requests.Session()
    resp = s.post(login_url, data=credentials)
    if resp.url == login_url or resp.url == login_error:
        print('uh oh – we didn\'t manage to log in!')
        print(resp.text)
        sys.exit(0)

    soup = bs(resp.text, 'html.parser')
    table = soup.find(id='hor-minimalist-d')
    job_data = [job_data.find_all('td') for job_data in table.find_all('tr')]

    jobs_list = [{
        'job': job[0].get_text(),
        'href': job[0].a['href'],
        'boss': job[1].get_text(),
        'start': parse_date(job[2].get_text()),
        'end': parse_date(job[3].get_text()),
        'rate': float(job[4].get_text()[1:]),
    } for job in job_data]

    jobs = {}
    for job in jobs_list:
        jobs[job['job']] = job

    for name, data in jobs.items():
        hours_page = s.get(tes_base + data['href'])
        hours_soup = bs(hours_page.text, 'html.parser')
        current, prior = hours_soup.select('.entry-content > table')

        data['hours'] = {}

        # get current month's hours
        current_months = current.find_all('tr')[1:]
        for month in current_months:
            cells = month.find_all('td')
            month_name = cells[0].get_text().split(' ')[0]
            month_hours = float(cells[2].get_text().strip())
            data['hours'][month_name] = month_hours

        # get previous hours
        prior_months = prior.find_all('tr')[1:]
        for month in prior_months:
            cells = month.find_all('td')
            month_name = cells[0].get_text().split(' ')[0]
            month_hours = float(cells[1].get_text().strip())
            data['hours'][month_name] = month_hours

        del data['href']

    return jobs.values()


def process_jobs(jobs):
    work_award = 2300

    for job in jobs:
        job['worked'] = sum(job['hours'].values())
        job['earned'] = job['rate'] * job['worked']

    hours_worked_overall = sum([j['worked'] for j in jobs])
    amount_earned_overall = sum([j['earned'] for j in jobs])

    avg_rate = sum([j['rate'] for j in jobs]) / len(jobs)
    max_hours = work_award / avg_rate
    remaining_hours = max_hours - hours_worked_overall

    now = datetime.today()
    end_date = max([j['end'] for j in jobs])

    timediff = end_date - now
    weeks_until_work_end = timediff.days / 7

    hours_to_work_per_week = remaining_hours / weeks_until_work_end

    grouped_by_month = OrderedDict({})
    for job in jobs:
        for monthName in sorted(job['hours'], key=sort_month_names):
            if monthName not in grouped_by_month:
                grouped_by_month[monthName] = {}
            grouped_by_month[monthName][job['job']] = job['hours'][monthName]

    for monthName in grouped_by_month:
        grouped_by_month[monthName]['_total'] = sum(grouped_by_month[monthName].values())

    data = {
        'hours_to_work_per_week': hours_to_work_per_week,
        'amount_earned_overall': amount_earned_overall,
        'weeks_until_work_end': weeks_until_work_end,
        'hours_worked_overall': hours_worked_overall,
        'grouped_by_month': grouped_by_month,
        'remaining_hours': remaining_hours,
        'work_award': work_award,
        'max_hours': max_hours,
        'jobs': jobs,
    }

    return data


def to_html(data):
    hours_to_work_per_week = data['hours_to_work_per_week']
    amount_earned_overall = data['amount_earned_overall']
    hours_worked_overall = data['hours_worked_overall']
    weeks_until_work_end = data['weeks_until_work_end']
    grouped_by_month = data['grouped_by_month']
    remaining_hours = data['remaining_hours']
    work_award = data['work_award']
    max_hours = data['max_hours']
    jobs = data['jobs']

    html = ''
    newline = '\n'

    html += '<main>' + newline
    html += '<ul>' + newline
    html += '<li>' + newline
    html += 'Hours:' + newline

    html += '<ul class="months">' + newline
    for month, monthData in grouped_by_month.items():
        html += '<li>' + newline
        html += '<details>' + newline
        html += '<summary><x-key>%s:</x-key> %.2f hours</summary>\n' % (month, monthData['_total'])
        html += '<ul>' + newline
        for job_name, hours in monthData.items():
            if job_name[0] != '_':
                html += '<li>%s: %.2f hours</li>\n' % (job_name, hours)
        html += '</ul>' + newline
        html += '</details>' + newline
        html += '</li>' + newline

    html += '<li>' + newline
    html += '<details>' + newline
    html += '<summary><x-key>Total:</x-key> %.2f hours</summary>\n' % hours_worked_overall
    html += '<ul>' + newline
    for job in jobs:
        html += '<li>%s: %.2f hours</li>\n' % (job['job'], sum(job['hours'].values()))
    html += '</ul>' + newline
    html += '</details>' + newline
    html += '</li>' + newline

    html += '</ul>' + newline
    html += '</li>' + newline

    html += '<li>' + newline
    html += 'Rates:' + newline
    html += '<ul class="months">' + newline
    for job in jobs:
        html += '<li>%s: $%.2f / hour</li>' % (job['job'], job['rate']) + newline
    html += '</ul>' + newline
    html += '</li>' + newline

    html += '<li>Work Award: $%d</li>\n' % work_award
    html += '<li>Amount Earned: $%d</li>\n' % amount_earned_overall
    html += '<li>Weeks Until End of Jobs: %d weeks (including breaks)</li>\n' % weeks_until_work_end
    html += '<li>Total Hours Needed: %.2f hours</li>\n' % max_hours
    html += '<li>Hours Remaining: %.2f hours</li>\n' % remaining_hours
    html += '<li>Hours Per Week: %.2f hours</li>\n' % hours_to_work_per_week

    html += '</ul>' + newline
    html += '</main>' + newline

    return html


def date_handler(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return None


def to_json(data):
    return json.dumps(data,
                      default=date_handler,
                      sort_keys=True,
                      separators=(',', ': '),
                      indent=4)


def cgi_bin_main():
    data = sys.stdin.read()
    # print data

    print 'Content-type: text/html; charset=UTF-8\n'

    print '<meta name="viewport" content="width=device-width">'
    print '<style>'
    print '''
        body {
            font-family: sans-serif;
            max-width: 40em;
            margin: 1em auto;
        }
        x-key {
            font-weight: bold;
        }
        li {
            padding: 0.25em 0;
            list-style: none;
        }
        summary {
            cursor: pointer;
        }
        ul {
            padding-left: 0;
        }
        ul ul {
            padding-left: 2em;
        }
        main {
            margin: 0 1em;
        }
    '''
    print '</style>'
    print '<title>Unofficial TES Tool</title>'

    if 'username' not in data or 'password' not in data:
        print '''
            <form action="" method="POST">
                <input placeholder="username" name="username" type="text">
                <br>
                <input placeholder="password" name="password" type="password">
                <br>
                <input type="submit" value="Log in">
            </form>
        '''
        sys.exit(0)

    parsed_data = parse_qs(data)
    username = parsed_data['username'][0].strip()
    password = parsed_data['password'][0].strip()

    print to_html(process_jobs(get_jobs(username, password)))


def cli_main():
    data = sys.stdin.read()

    if not data:
        print 'Usage: ./get-tes.py < credentials.txt'
        print '"credentials.txt" should be a username and password, on separate lines'
        sys.exit(1)

    parsed_data = data.split('\n')
    username = parsed_data[0].strip()
    password = parsed_data[1].strip()

    if not username or not password:
        print 'Please provide both a username and a password'
        sys.exit(1)

    print to_json(process_jobs(get_jobs(username, password)))


if __name__ == '__main__' and 'SERVER_SOFTWARE' in os.environ:
    cgi_bin_main()

elif __name__ == '__main__':
    cli_main()
