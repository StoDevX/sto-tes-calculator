import React from 'react'
import {RouteHandler} from 'react-router'

export default React.createClass({
	render() {
		return <div className='app'>
			<menu className='toolbar'>
				<li>Back</li>
			</menu>
			<RouteHandler />
		</div>
	}
})
