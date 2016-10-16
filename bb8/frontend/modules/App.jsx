import React from 'react';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';
import FlatButton from 'material-ui/FlatButton';

import LoginForm from '../components/LoginForm';

const App = () => (
  <div>
    Hello, Compose.ai!
    Here is a demo of material ui buttons:
    <MuiThemeProvider>
      <div>
        <FlatButton label="Default" />
        <FlatButton label="Primary" primary />
        <FlatButton label="Secondary" secondary />
        <FlatButton label="Disabled" disabled />
        <LoginForm />
      </div>
    </MuiThemeProvider>
  </div>);

export default App;
