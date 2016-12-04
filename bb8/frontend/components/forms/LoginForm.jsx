import React from 'react'
import { Field, reduxForm } from 'redux-form'
import validator from 'validator'

import RaisedButton from 'material-ui/RaisedButton'

import renderTextField from './util'
import { startLogin } from '../../actions/accountActionCreators'


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
  >
    <div>
      <Field name="email" component={renderTextField} label="Email" />
    </div>
    <div>
      <Field name="passwd" component={renderTextField} label="Password" />
    </div>
    <RaisedButton className="b-login-card__button" type="submit" label="Login" fullWidth primary />
  </form>
)

LoginForm.propTypes = {
  handleSubmit: React.PropTypes.func,
}

export default reduxForm({
  form: 'LoginForm',  // a unique identifier for this form
  validate,
})(LoginForm)
