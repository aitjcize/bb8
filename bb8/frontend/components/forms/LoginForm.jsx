import React from 'react'
import { Field, reduxForm } from 'redux-form'
import validator from 'validator'
import stylePropType from 'react-style-proptype'

import RaisedButton from 'material-ui/RaisedButton'

import renderTextField from './util'
import { startLogin } from '../../actions/accountActionCreators'

const styles = {
  fields: {
    marginBottom: '1em',
  },
  inputPasswd: {
    letterSpacing: '.2em',
    cursor: 'text',
  },
}


function validate(values) {
  const errors = {}
  const email = values.email
  const passwd = values.passwd
  if (typeof email === 'string' && !validator.isEmail(email)) {
    errors.email = 'Please provide a valid email address'
  }
  if (typeof passwd === 'string' &&
      !validator.isLength(passwd, { min: 6, max: 20 })) {
    errors.passwd = 'Password length should between 6 to 20'
  }
  return errors
}

const LoginForm = props => (
  <form
    onSubmit={props.handleSubmit((value, dispatch) =>
      dispatch(startLogin(value.email, value.passwd)))}
    style={props.style}
  >
    <div style={styles.fields}>
      <Field
        name="email"
        component={renderTextField}
        floatingLabelText="Email"
      />
      <Field
        name="passwd"
        component={renderTextField}
        type="password"
        inputStyle={styles.inputPasswd}
        floatingLabelText="Password"
        readOnly
        onFocus={(e) => { e.target.removeAttribute('readonly') }}
      />
    </div>
    <RaisedButton type="submit" label="Login" fullWidth primary />
  </form>
)

LoginForm.propTypes = {
  handleSubmit: React.PropTypes.func,
  style: stylePropType,
}

export default reduxForm({
  form: 'LoginForm',  // a unique identifier for this form
  validate,
})(LoginForm)
