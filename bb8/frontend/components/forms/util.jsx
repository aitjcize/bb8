import React from 'react'
import TextField from 'material-ui/TextField'

const renderTextField = ({ input, label, meta: { touched, error }, ...custom }) => (
  <TextField
    fullWidth
    hintText={label}
    floatingLabelText={label}
    errorText={touched && error}
    {...input}
    {...custom}
  />
)

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
}

export default renderTextField
