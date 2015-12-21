#!/usr/bin/env python3

import requests
import sys
import json
from bs4 import BeautifulSoup as bs


def get_data(username, password):
    tes_base = 'https://www.stolaf.edu/apps/tes/'
    login_url = 'https://www.stolaf.edu/apps/tes/index.cfm?fuseaction=login.processLogin'
    login_error = 'http://www.stolaf.edu/apps/tes/index.cfm?fuseaction=login.login&error=1'

    credentials = {'username': username, 'password': password}

    s = requests.Session()
    resp = s.post(login_url, data=credentials)
    if resp.url == login_url or resp.url == login_error:
        print('uh oh – we didn\'t manage to log in!', file=sys.stderr)
        print(resp.text, file=sys.stderr)
        sys.exit(0)

    # print('logged in successfully', file=sys.stderr)

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

    jobs = {job['job']: job for job in jobs_list}

    for name, data in jobs.items():
        hours_page = s.get(tes_base + data['href'])
        hours_soup = bs(hours_page.text, 'html.parser')
        current, prior = hours_soup.select('.entry-content > table')
        # print(stuff)

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

    return json.dumps(list(jobs.values()),
                      sort_keys=True,
                      separators=(',', ': '),
                      indent=4)


if __name__ == '__main__':
    with open('./credentials.txt', 'r') as creds:
        user, pword = creds.read().split()
        print(get_data(user, pword))
