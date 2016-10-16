import React from 'react';
import { Field, reduxForm } from 'redux-form';
import TextField from 'material-ui/TextField';
import RaisedButton from 'material-ui/RaisedButton';
import validator from 'validator';

import { startLogin } from '../actions';


function validate(values) {
  const errors = {};
  if (typeof values.email === 'string' &&
      !validator.isEmail(values.email)) {
    errors.email = 'Please provide a valid email address';
  }
  if (typeof values.passwd === 'string' &&
      !validator.isLength(values.passwd, { min: 6, max: 20 })) {
    errors.passwd = 'Password length should between 6 to 20';
  }
  return errors;
}

const renderTextField = ({ input, label, meta: { touched, error }, ...custom }) => (
  <TextField
    hintText={label}
    floatingLabelText={label}
    errorText={touched && error}
    {...input}
    {...custom}
  />
);

renderTextField.propTypes = {
  input: React.PropTypes.shape({
    checked: React.PropTypes.bool,
    name: React.PropTypes.string,
    onBlur: React.PropTypes.func,
    onChange: React.PropTypes.func,
    onDragStart: React.PropTypes.func,
    onDrop: React.PropTypes.func,
    onFocus: React.PropTypes.func,
    value: React.PropTypes.string,
  }),
  label: React.PropTypes.string,
  meta: React.PropTypes.shape({
    touched: React.PropTypes.bool,
    error: React.PropTypes.string,
  }),
};

function handleSubmit(value, dispatch) {
  dispatch(startLogin(value.email, value.passwd));
}


const LoginForm = props => (
  <form onSubmit={props.handleSubmit(handleSubmit)}>
    <div>
      <Field name="email" component={renderTextField} label="Email" />
    </div>
    <div>
      <Field name="passwd" component={renderTextField} label="Password" />
    </div>
    <div>
      <RaisedButton type="submit" label="Login" primary />
    </div>
  </form>
);

LoginForm.propTypes = {
  handleSubmit: React.PropTypes.func,
};

export default reduxForm({
  form: 'LoginForm',  // a unique identifier for this form
  validate,
})(LoginForm);
