import 'babelify/polyfill'
import 'whatwg-fetch'

import {run as runRouter, Route, NotFoundRoute, DefaultRoute} from 'react-router'
import React from 'react'

import App from './screens/app/'
import Home from './screens/app/screens/home'
import Login from './screens/app/screens/login'
import NotFound from './screens/app/screens/notFound'

import get from '../get-tes.js'

let routes = (
	<Route handler={App} path="/">
		<DefaultRoute handler={Home} />
		<Route name="login" handler={Login} />
		<NotFoundRoute handler={NotFound}/>
	</Route>
)

runRouter(routes, (RouteHandler) => {
	React.render(<RouteHandler />, document.getElementById('app'))
})
