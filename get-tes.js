#!/usr/bin/env babel-node


import Promise from 'bluebird'
// import jsdom from 'jsdom'
// import axios from 'axios'
import fsLib from 'fs'
// let axios = Promise.promisifyAll(axiosLib)
let fs = Promise.promisifyAll(fsLib)

const tes_base = 'https://www.stolaf.edu/apps/tes/'
const login_url = 'https://www.stolaf.edu/apps/tes/index.cfm?fuseaction=login.processLogin'
const login_error = 'http://www.stolaf.edu/apps/tes/index.cfm?fuseaction=login.login&error=1'

async function main() {
	// let creds = await fs.readFileAsync('./credentials.txt', {encoding: 'utf-8'})

	// const [user, pword] = creds.split('\n')
	const [user, pword] = ['rives', 'imbackin']
	// const credentials = {
	// 	form: {
	// 		username: user,
	// 		password: pword,
	// 	}
	// }
	// console.log(credentials)

	let formData = new FormData()
	formData.append('username', user)
	formData.append('password', pword)

	let resp = await fetch(login_url, {
		method: 'POST',
		body: formData,
	})

	console.log(resp.text())
}

window.run = main
// main()

/*
s = requests.Session()
resp = s.post(login_url, data=credentials)
if resp.url == login_url:
	print('uh oh – we didn\'t manage to log in!')
	sys.exit(0)

print('logged in successfully')

soup = BS(resp.text)
table = soup.find(id='hor-minimalist-d')
job_data = [job_data.find_all('td') for job_data in table.find_all('tr')]

jobs_list = [{
	'name': job[0].get_text(),
	'href': job[0].a['href'],
	'boss': job[1].get_text(),
	'start': job[2].get_text(),
	'end': job[3].get_text(),
	'rate': job[4].get_text(),
} for job in job_data]

jobs = {job['name']: job for job in jobs_list}

for name, job in jobs.items():
	hours_page = s.get(tes_base + job['href'])
	hours_soup = BS(hours_page.text)
	current, prior = hours_soup.select('.entry-content > table')
	// print(stuff)

	job['hours'] = {}

	// get current month's hours
	current_months = current.find_all('tr')[1:]
	for month in current_months:
		cells = month.find_all('td')
		month_name = cells[0].get_text().split(' ')[0]
		month_hours = cells[2].get_text().strip()
		job['hours'][month_name] = month_hours

	// get previous hours
	prior_months = prior.find_all('tr')[1:]
	for month in prior_months:
		cells = month.find_all('td')
		month_name = cells[0].get_text().split(' ')[0]
		month_hours = cells[1].get_text().strip()
		job['hours'][month_name] = month_hours

	del job['href']

print(list(jobs.values()))
*/
