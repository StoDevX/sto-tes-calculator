import React from 'react'
import moment from 'moment'
import {groupBy, forEach, map, reduce, pluck, mapValues, size, trunc} from 'lodash'

let actions = {
	logout() {
		console.log('logout')
	},
	refresh() {
		console.log('refresh')
	}
}

let sum = (accumulator, value) => accumulator + value

export default React.createClass({
	render() {
		let workAward = 2300

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
				hours: 41.18,
				month: 'February',
			}
		]

		hours = map(hours, job => {
			job.earned = job.rate * job.hours
			return job
		})

		let months = groupBy(hours, 'month')
		let jobs = mapValues(groupBy(hours, 'job'), jobs => {
			return {
				earned: reduce(pluck(jobs, 'earned'), sum, 0),
				hours: reduce(pluck(jobs, 'hours'), sum, 0),
				rate: (reduce(pluck(jobs, 'rate'), sum, 0) / size(jobs)),
			}
		})

		let hoursWorkedOverall = reduce(pluck(hours, 'hours'), sum, 0)
		let amountEarnedOverall = reduce(pluck(hours, 'earned'), sum, 0)

		let avgRate = reduce(pluck(jobs, 'rate'), sum, 0) / size(jobs)
		let maxHours = workAward / avgRate
		let remainingHours = maxHours - hoursWorkedOverall

		let now = moment()
		let graduation = moment('05/13/2015', 'MM/DD/YYYY')
		let hoursUntilGraduation = graduation.diff(now, 'weeks')

		let hoursToWorkPerWeek = remainingHours / hoursUntilGraduation
		console.log(maxHours, remainingHours, hoursUntilGraduation, hoursToWorkPerWeek)

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
								// console.log(month)
								// let hoursWorkedThisMonth = reduce(monthData, (sum, job) => sum + job.hours, 0)
								let hoursWorkedThisMonth = reduce(pluck(monthData, 'hours'), sum, 0)
								return <li key={month}>
									<details>
										<summary>
											<span className='key'>{month}: </span>
											{hoursWorkedThisMonth} hrs
										</summary>
										<ul>
											{map(monthData, ({job, hours}, i) => <li key={i}>{job}: {hours}</li>)}
										</ul>
									</details>
								</li>
							})}
							<li key='total'>
								<details>
									<summary>
										<span className='key'>Total: </span>
										{hoursWorkedOverall} hrs
									</summary>
									<ul>
										{map(jobs, ({hours}, jobName) =>
											<li key={jobName}>{jobName}: {hours}</li>)}
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
					<li>Hours Remaining: {remainingHours}</li>
					<li>Hours Per Week: {hoursToWorkPerWeek}</li>
				</ul>
			</main>
		</div>
	}
})
