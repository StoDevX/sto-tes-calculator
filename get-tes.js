#!/usr/bin/env babel-node

import Promise from 'bluebird'
Promise.config({
	// Enable warnings.
	warnings: true,
	// Enable long stack traces.
	longStackTraces: true,
	// Enable cancellation.
	cancellation: true,
})

import 'isomorphic-fetch'
import FormData from 'form-data'
import cheerio from 'cheerio'
import values from 'lodash/object/values'
import zipObject from 'lodash/array/zipObject'
import pairs from 'lodash/object/pairs'

const tes_base = 'https://www.stolaf.edu/apps/tes/'
const login_url = 'https://www.stolaf.edu/apps/tes/index.cfm?fuseaction=login.processLogin'
const login_error = 'https://www.stolaf.edu/apps/tes/index.cfm?fuseaction=login.login&error=1'

function getPage(u, p) {
	const formData = new FormData()
	formData.append('username', u)
	formData.append('password', p)
	formData.append('username_required', 'You must enter a username.')
	formData.append('password_required', 'You must enter a password.')
	formData.append('Submit', 'Login')

	return (url, opts) => fetch(url, {
		method: 'POST',
		body: formData,
		credentials: 'include',
	 	...opts,
	 })
	.then(r => r.text())
}

async function checkLogin(get) {
	try {
		await get(login_url, {redirect: 'manual'})
	}
	catch(e) {
		console.error(e)
		console.error('uh oh – we didn\'t manage to log in!')
		return false
	}

	console.log('logged in successfully')
	return true
}

async function getJobs(get) {
	const response = await get(tes_base)

	console.log(response)

	return

	const $ = cheerio.load(response)
	const table = $('#hor-minimalist-d')

	const job_data = table.find('tr')//.map(row => row.find('td'))

	console.log(job_data)
	const jobs_list = []
	job_data.each((i, job) => {
		jobs_list.push({
			name: job[0].text(),
			href: job[0].find('a')[0].attr('href'),
			boss: job[1].text(),
			start: job[2].text(),
			end: job[3].text(),
			rate: Number(job[4].text().replace('$', '')),
		})
	})

	console.log('jobs_list', jobs_list)

	const jobs = zipObject(jobs_list.map(job => [job.name, job]))

	return jobs
}

async function getJobHours(get, jobData) {
	console.log('jobData', jobData)
	const hours_page = await get(`${tes_base}${jobData.attr('href')}`)
	const $ = cheerio.load(hours_page)
	const [current, prior] = $('.entry-content > table')
	// print(stuff)

	jobData.hours = {}

	// get current month's hours
	const current_months = current.find('tr').slice(1)
	for (const month of current_months) {
		const cells = month.find('td')
		const month_name = cells[0].text().split(' ')[0]
		const month_hours = Number(cells[2].text().strip())
		jobData.hours[month_name] = month_hours
	}

	// get previous hours
	const prior_months = prior.find_all('tr').slice(1)
	for (const month of prior_months) {
		const cells = month.find('td')
		const month_name = cells[0].text().split(' ')[0]
		const month_hours = Number(cells[2].text().strip())
		jobData.hours[month_name] = month_hours
	}

	delete jobData['href']
}

async function getData({username=null, password=null}) {
	const get = getPage(username, password)

	await checkLogin(get)

	let jobs = {}
	try {
		jobs = await getJobs(get)
		return
	}
	catch (err) {
		console.error(err)
		return []
	}

	console.log('jobs', jobs)

	await Promise.all(pairs(jobs).map(([_, data]) => {
		const result = getJobHours(get, data)
		console.log(data)
		console.log(result)
		return result
	}))

	return values(jobs)
}

getData({username: 'rives', password: 'nfoofoon'})
	.then(data => JSON.stringify(data, null, 4))
	.then(v => console.log(v))
	.catch(err => console.error('[getData]', err))

process.on('unhandledRejection', function(reason, p) {
	console.log("Unhandled Rejection at: Promise ", p, " reason: ", reason);
});
