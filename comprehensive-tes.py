from bs4 import BeautifulSoup as bs, element as bs4_element
import requests
import re, os, sys, json, copy

s = requests.Session()

def action(title):
    return 'https://www.stolaf.edu/apps/tes/index.cfm?fuseaction={}'.format(title)

def log_in(username, password):
    print('logging in…')
    resp = s.post(action('login.processLogin'), data={
        'username': username,
        'password': password,
        'username_required': 'You must enter a username.',
        'password_required': 'You must enter a password.',
        'Submit': 'Login',
    })

    page = resp.text
    print('logged in.')
    return 'To access this site, you need to login.' not in page


def extract_timecard_entry_from_row(row):
    cells = row.select('td')

    date = cells[0].get_text().strip()
    entry_cells = cells[1:7]

    entries = [cell.get('value', cell.get_text()).strip() for cell in entry_cells]
    paired_entries = list(zip(entries[0::2], entries[1::2]))
    # only return the entries with at least time entered
    paired_entries = [p for p in paired_entries if any(p)]

    return {'Date': date, 'Entries': paired_entries}


def extract_timecard_entry_from_row_pair(row_pair):
    row0_cells = row[0].select('td')
    row1_cells = row[1].select('td')

    date = row0_cells[0].get_text().strip()
    entry_cells = row0_cells[1:7] + row1_cells[1:7]

    entries = [cell.get('value', cell.get_text()).strip() for cell in entry_cells]
    paired_entries = list(zip(entries[0::2], entries[1::2]))
    # only return the entries with at least time entered
    paired_entries = [p for p in paired_entries if any(p)]

    return {'Date': date, 'Entries': paired_entries}


def is_entry_row(tr):
    if 'class' in tr.attrs and tr.attrs['class'] == 'summaryrow':
        # print('bad class')
        return False
    children = [e for e in tr.children if type(e) is bs4_element.Tag]
    if len(children) != 8:
        # print('wrong child count', len(children))
        return False
    # TODO: i think this will fail to return the second row for the multi-row version
    if 'nowrap' not in children[0].attrs:
        # print('not nowrap')
        return False
    return True


def extract_timecard_entries_from_table(table):
    if not table:
        return None

    # make sure to check for tables with 6 in/out pairs
    # where the second set is in the subsequent row

    # ignore the first row
    rows = [row for row in table.select('tr') if is_entry_row(row)]

    if not rows:
        return None

    is_expanded_timesheet = False
    if is_expanded_timesheet:
        rows = zip(rows[0::2], rows[1::2])
        entries = [extract_timecard_entry_from_row_pair(pair) for pair in rows]
    else:
        entries = [extract_timecard_entry_from_row(row) for row in rows]

    return entries


def print_timecard(card):
    return '{Id}: {Pay Period}, totaling {Total Hours} hour(s)'.format(**card)

def get_timecard_details(timecard):
    print('fetching timecard', print_timecard(timecard))
    resp = s.get(action('time.card&card={}'.format(timecard['Id'])))
    soup = bs(resp.text, 'lxml')
    tables = soup.select('.entry-content > form table')
    entries = []
    if tables:
        entries = extract_timecard_entries_from_table(tables[0])

    return entries


def embed_timecard_details(job):
    print('fetching timecard details for', print_job(job))
    j = copy.deepcopy(job)
    for card in j['Timecards']:
        card['Hours'] = get_timecard_details(card)
    return j


def timecard_id_to_url(url):
    # index.cfm?fuseaction=time.card&card=138071
    result = re.search(r'card=(\d+)', url)
    return result.group(1) if result else None


def tablerow_to_timecard_summary(row):
    columns = ['Pay Period', 'Total Hours', '<Blank>']
    cells = row.select('td')
    timecard = dict(zip(columns, cells))

    timecard_info_url = timecard['Pay Period'].find('a').attrs['href']
    timecard_period = timecard['Pay Period'].get_text().strip()

    timecard['Id'] = timecard_id_to_url(timecard_info_url)
    timecard['Pay Period'] = timecard_period

    timecard['Total Hours'] = timecard['Total Hours'].get_text().strip()
    timecard['<Blank>'] = str(timecard['<Blank>']).strip()

    return timecard


def extract_timecard_summaries_from_table(table):
    if not table:
        return None

    return [tablerow_to_timecard_summary(row) for row in table.select('tr')[1:]]


def print_job(job):
    return '{Id}: "{Title}" from {Start} to {End} at {Rate}/hr, with {Supervisor}'.format(**job)

def embed_timecard_summaries(job):
    print('fetching timecard summaries for', print_job(job))
    resp = s.get(action('time.list&job={}'.format(job['Id'])))
    soup = bs(resp.text, 'lxml')
    tables = soup.select('.entry-content > table')
    cards = []
    if tables:
        cards = extract_timecard_summaries_from_table(tables[0])
    j = copy.deepcopy(job)
    j['Timecards'] = cards
    return j


def job_url_to_id(url):
    # index.cfm?fuseaction=time.list&job=27618
    result = re.search(r'job=(\d+)', url)
    return result.group(1) if result else None


def tablerow_to_job(row, is_archived):
    columns = ['Title', 'Supervisor', 'Start', 'End', 'Rate']
    cells = row.select('td')
    job = dict(zip(columns, cells))

    job_url = job['Title'].find('a').attrs['href']
    job_title = job['Title'].get_text().strip()

    job['Id'] = job_url_to_id(job_url)
    job['Title'] = job_title
    job['Archived'] = is_archived

    job['Supervisor'] = job['Supervisor'].get_text().strip()
    job['Start'] = job['Start'].get_text().strip()
    job['End'] = job['End'].get_text().strip()
    job['Rate'] = job['Rate'].get_text().strip()

    return job


def extract_jobs_from_table(table, archived=False):
    if not table:
        return None

    return [tablerow_to_job(row, archived) for row in table.select('tr')]


def get_archived_jobs():
    print('fetching archived jobs')
    resp = s.get(action('welcome.archive'))
    soup = bs(resp.text, 'lxml')
    tables = soup.select('#filtertable ~ table')
    if not tables:
        return []
    return extract_jobs_from_table(tables[0], True)


def get_jobs():
    print('fetching jobs')
    resp = s.get(action('welcome.student'))
    soup = bs(resp.text, 'lxml')
    tables = soup.select('#filtertable ~ table')
    if not tables:
        return []
    return extract_jobs_from_table(tables[0], False)


def main(args):
    USERNAME = args[0]
    PASSWORD = args[1]
    loggedin = log_in(USERNAME, PASSWORD)

    active_jobs = get_jobs()
    archived_jobs = get_archived_jobs()

    basic_jobs = active_jobs + archived_jobs

    embedded_jobs = [embed_timecard_summaries(job) for job in basic_jobs]
    now_with_timecards = [embed_timecard_details(job) for job in embedded_jobs]

    print(json.dumps(now_with_timecards, sort_keys=True, indent=2))


if __name__ == '__main__':
    main(sys.argv[1:])
