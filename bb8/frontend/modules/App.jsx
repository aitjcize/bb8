import React from 'react'

import TopBar from '../components/TopBar'

const App = props => (
  <div>
    <TopBar />
    {props.children}
  </div>
)

App.propTypes = {
  children: React.PropTypes.node,
}

export default App
