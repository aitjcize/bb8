import types from '../constants/ActionTypes'
import NotificationReducer from './NotificationReducer' 
import { openNotification, closeNotification } from '../actions/uiActionCreators'

describe('Reducer for Notifications', () => {
  it('should return the initial state', () => {
    expect(
      NotificationReducer(undefined, {})
    ).toEqual({
      open: false,
      message: '',
    })
  })

  it('should open the notification snackbar', () => {
    expect(
      NotificationReducer(undefined, openNotification('abcde'))
    ).toEqual({
      open: true,
      message: 'abcde',
    })
  })

  it('should close the notification snackbar', () => {
    expect(
      NotificationReducer(undefined, closeNotification())
    ).toEqual({
      open: false,
      message: '',
    })
  })
})
