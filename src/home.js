import React from 'react'
import moment from 'moment'
import {toFixed} from 'humanize-plus'
import reduce from 'lodash/collection/reduce'
import map from 'lodash/collection/map'
import groupBy from 'lodash/collection/groupBy'
import pluck from 'lodash/collection/pluck'
import mapValues from 'lodash/object/mapValues'
import size from 'lodash/collection/size'
import values from 'lodash/object/values'

import data from '../data.json'
console.log(data)

import actions from './actions'

const sum = (accumulator, value) => accumulator + value
const sumKey = (coll, key) => reduce(pluck(coll, key), sum, 0)

export default class Home extends React.Component {
	render() {
		const workAward = 2500
		let jobs = data

		jobs = map(jobs, (job) => {
			job.worked = reduce(values(job.hours), sum)
			job.earned = job.rate * job.worked
			return job
		})

		console.log(jobs)

		// let months = groupBy(jobs, 'month')
		// jobs = mapValues(groupBy(hours, 'job'), jobs => ({
		// 		earned: sumKey(jobs, 'earned'),
		// 		hours: sumKey(jobs, 'hours'),
		// 		rate: sumKey(jobs, 'rate') / size(jobs),
		// }))

		const hoursWorkedOverall = sumKey(jobs, 'worked')
		const amountEarnedOverall = sumKey(jobs, 'earned')
		// console.log(hoursWorkedOverall, amountEarnedOverall)

		const avgRate = sumKey(jobs, 'rate') / size(jobs)
		const maxHours = workAward / avgRate
		const remainingHours = maxHours - hoursWorkedOverall

		const now = moment()
		const graduation = moment('05/20/2015', 'MM/DD/YYYY')

		// this becomes 0 during the week leading up to finals
		const weeksUntilGraduation = graduation.diff(now, 'weeks') || 1

		const hoursToWorkPerWeek = remainingHours / weeksUntilGraduation
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
