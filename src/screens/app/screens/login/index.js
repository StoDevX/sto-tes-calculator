import React from 'react'

export default React.createClass({
	getInitialState() {
		return {
			username: '',
			password: '',
		}
	},

	handleLogin(ev) {
		ev.preventDefault()
	},
	handleTyping(ev) {
		let {type, value} = ev.target

		if (type === 'text')
			this.setState({username: value})
		else if (type === 'password')
			this.setState({password: value})
	},

	render() {
		return <form className='login' onSubmit={this.handleLogin} onChange={this.handleTyping}>
			<label className='username'>
				<span>St. Olaf Username</span>
				<input type='text' placeholder='sevir' />
			</label>
			<label className='password'>
				<span>St. Olaf Password</span>
				<input type='password' placeholder='••••••••' />
			</label>

			<input type='submit' value='Log In' />
		</form>
	}
})
