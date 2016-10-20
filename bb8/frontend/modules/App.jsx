import React from 'react'
import FlatButton from 'material-ui/FlatButton'

import LoginForm from '../components/LoginForm'
import TopBar from '../components/TopBar'

const App = () => (
  <div>
    <div>
      <TopBar />
      <div>
        Hello, Compose.ai!
        Here is a demo of material ui buttons:
      </div>
      <FlatButton label="Default" />
      <FlatButton label="Primary" primary />
      <FlatButton label="Secondary" secondary />
      <FlatButton label="Disabled" disabled />
      <LoginForm />
    </div>
  </div>)

export default App
