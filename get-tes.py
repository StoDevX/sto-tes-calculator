#!/usr/bin/python
# coding=utf-8

import os
import sys
import inspect
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
        'start': job[2].get_text(),
        'end': job[3].get_text(),
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

    # print('hours_worked_overall', hours_worked_overall)
    # print('amount_earned_overall', amount_earned_overall)

    avg_rate = sum([j['rate'] for j in jobs]) / len(jobs)
    max_hours = work_award / avg_rate
    remaining_hours = max_hours - hours_worked_overall

    # print('avg_rate', avg_rate)
    # print('max_hours', max_hours)
    # print('remaining_hours', remaining_hours)

    now = datetime.today()
    graduation = datetime(2016, 5, 29)

    timediff = graduation - now
    weeks_until_graduation = timediff.days / 7

    hours_to_work_per_week = remaining_hours / weeks_until_graduation

    # print('weeks_until_graduation', weeks_until_graduation)
    # print('hours_to_work_per_week', hours_to_work_per_week)

    grouped_by_month = OrderedDict({})
    for job in jobs:
        for monthName in sorted(job['hours'], key=sort_month_names):
            if monthName not in grouped_by_month:
                grouped_by_month[monthName] = {}
            grouped_by_month[monthName][job['job']] = job['hours'][monthName]

    # print(grouped_by_month)

    print '<main>'
    print '<ul>'
    print '<li>'
    print 'Hours:'

    print '<ul class="months">'
    for month, monthData in grouped_by_month.items():
        worked_this_month = sum(monthData.values())
        print '<li>'
        print '<details>'
        print '<summary><x-key>%s:</x-key> %.2f hours</summary>' % (month, worked_this_month)
        print '<ul>'
        for n, hours in monthData.items():
            print '<li>%s: %.2f hours</li>' % (n, hours)
        print '</ul>'
        print '</details>'
        print '</li>'

    print '<li>'
    print '<details>'
    print '<summary><x-key>Total:</x-key> %.2f hours</summary>' % hours_worked_overall
    print '<ul>'
    for job in jobs:
        print '<li>%s: %.2f hours</li>' % (job['job'], sum(job['hours'].values()))
    print '</ul>'
    print '</details>'
    print '</li>'

    print '</ul>'
    print '</li>'

    print '<li>'
    print 'Rates:'
    print '<ul class="months">'
    for job in jobs:
        print '<li>%s: $%.2f / hour</li>' % (job['job'], job['rate'])
    print '</ul>'
    print '</li>'

    print '<li>Work Award: $%d</li>' % work_award
    print '<li>Weeks Until Graduation: %d weeks (including breaks)</li>' % weeks_until_graduation
    print '<li>Total Hours Needed: %.2f hours</li>' % max_hours
    print '<li>Hours Remaining: %.2f hours</li>' % remaining_hours
    print '<li>Hours Per Week: %.2f hours</li>' % hours_to_work_per_week

    print '</ul>'
    print '</main>'

    return jobs


def print_jobs(jobs):
    return json.dumps(list(jobs),
                      sort_keys=True,
                      separators=(',', ': '),
                      indent=4)


if __name__ == '__main__':
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
                <input placeholder="password" name="password" type="password">
                <input type="submit" value="Log in">
            </form>
        '''
        sys.exit(0)

    parsed_data = parse_qs(data)
    username = parsed_data['username'][0].strip()
    password = parsed_data['password'][0].strip()

    process_jobs(get_jobs(username, password))
