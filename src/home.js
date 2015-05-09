import React from 'react'
import moment from 'moment'
import {toFixed} from 'humanize-plus'
import {groupBy, map, reduce, pluck, mapValues, size, chain} from 'lodash'

const actions = {
	logout() {
		console.log('logout')
	},
	refresh() {
		console.log('refresh')
	}
}

const sum = (accumulator, value) => accumulator + value
const sumKey = (coll, key) => reduce(pluck(coll, key), sum, 0)

export default class Home extends React.Component {
	render() {
		let workAward = 2500

		let hours = [
			{
				job: 'Assistant to the Macintosh Systems Administrator',
				rate: 8.00,
				hours: 51.33,
				month: 'September',
			},
			{
				job: 'Assistant to the Macintosh Systems Administrator',
				rate: 8.00,
				hours: 36.00,
				month: 'October',
			},
			{
				job: 'Assistant to the Macintosh Systems Administrator',
				rate: 8.00,
				hours: 36.70,
				month: 'November',
			},
			{
				job: 'Assistant to the Macintosh Systems Administrator',
				rate: 8.00,
				hours: 10.25,
				month: 'December',
			},
			{
				job: 'Assistant to the Macintosh Systems Administrator',
				rate: 8.00,
				hours: 21.42,
				month: 'January',
			},
			{
				job: 'Assistant to the Macintosh Systems Administrator',
				rate: 8.00,
				hours: 50.34,
				month: 'February',
			},
			{
				job: 'Assistant to the Macintosh Systems Administrator',
				rate: 8.00,
				hours: 16.25,
				month: 'March',
			},
			{
				job: 'Assistant to the Macintosh Systems Administrator',
				rate: 8.00,
				hours: 23.26,
				month: 'April',
			},
			{
				job: 'German Work Camp Booklet',
				rate: 8.00,
				hours: 4.5,
				month: 'April',
			},
			{
				job: 'Grader for Software Design',
				rate: 8.00,
				hours: 35.00,
				month: 'April',
			},
			{
				job: 'Assistant to the Macintosh Systems Administrator',
				rate: 8.00,
				hours: 10.09,
				month: 'May',
			},
			{
				job: 'German Work Camp Booklet',
				rate: 8.00,
				hours: 0,
				month: 'May',
			},
			{
				job: 'Grader for Software Design',
				rate: 8.00,
				hours: 3.05,
				month: 'May',
			},
		]

		hours = map(hours, job => {
			job.earned = job.rate * job.hours
			return job
		})

		let months = groupBy(hours, 'month')
		let jobs = mapValues(groupBy(hours, 'job'), jobs => ({
				earned: sumKey(jobs, 'earned'),
				hours: sumKey(jobs, 'hours'),
				rate: sumKey(jobs, 'rate') / size(jobs),
		}))
		// console.log(hours, months, jobs)

		let hoursWorkedOverall = sumKey(hours, 'hours')
		let amountEarnedOverall = sumKey(hours, 'earned')
		// console.log(hoursWorkedOverall, amountEarnedOverall)

		let avgRate = sumKey(jobs, 'rate') / size(jobs)
		let maxHours = workAward / avgRate
		let remainingHours = maxHours - hoursWorkedOverall

		let now = moment()
		let graduation = moment('05/13/2015', 'MM/DD/YYYY')

		// this becomes 0 during the week leading up to finals
		let weeksUntilGraduation = graduation.diff(now, 'weeks') || 1

		let hoursToWorkPerWeek = remainingHours / weeksUntilGraduation
		// console.log(maxHours, remainingHours, weeksUntilGraduation, hoursToWorkPerWeek)

		return <div>
			<menu>
				<button onclick={actions.refresh}>Refresh</button>
				<button onclick={actions.logOut}>Log Out</button>
			</menu>
			<main>
				<ul>
					<li>Hours
						<ul className='months'>
							{map(months, (monthData, month) => {
								let hoursWorkedThisMonth = sumKey(monthData, 'hours')
								return <li key={month}>
									<details>
										<summary>
											<span className='key'>{month}: </span>
											{toFixed(hoursWorkedThisMonth, 2)} hrs
										</summary>
										<ul>
											{map(monthData, ({job, hours}, i) =>
												<li key={i}>{job}: {toFixed(hours, 2)}</li>)}
										</ul>
									</details>
								</li>
							})}
							<li key='total'>
								<details>
									<summary>
										<span className='key'>Total: </span>
										{toFixed(hoursWorkedOverall, 2)} hrs
									</summary>
									<ul>
										{map(jobs, ({hours}, jobName) =>
											<li key={jobName}>{jobName}: {toFixed(hours, 2)}</li>)}
									</ul>
								</details>
							</li>
						</ul>
					</li>
					<li>Rates
						<ul className='months'>
							{map(jobs, ({rate}, jobName) =>
								<li key={jobName}>{jobName}: ${rate}</li>)}
						</ul>
					</li>
					<li>Work Award: ${workAward}</li>
					<li>Hours Remaining: {toFixed(remainingHours, 2)}</li>
					<li>Hours Per Week: {toFixed(hoursToWorkPerWeek, 2)}</li>
				</ul>
			</main>
		</div>
	}
}
