import types from '../constants/ActionTypes'

import AccountsReducer from './AccountsReducer'

const account = {
  id: 1,
  name: 'Account 1',
  username: 'Account Username 1',
  email: 'account1@compose.ai',
  email_verified: true,
  timezone: 'UTC',
}

describe('Reducer for bots', () => {
  it('should return the initial state', () => {
    expect(
      AccountsReducer(undefined, {})
    ).toEqual({})
  })

  it('should return the logined account', () => {
    expect(
      AccountsReducer(undefined, {
        type: types.ACCOUNTS_LOGIN.SUCCESS,
        payload: account
      })
    ).toEqual(account)
  })

  it('should clean the account on logout', () => {
    expect(
      AccountsReducer(undefined, {
        type: types.ACCOUNTS_LOGOUT.SUCCESS,
      })
    ).toEqual({})
  })

  it('should update invite code', () => {
    expect(
      AccountsReducer(undefined, {
        type: types.ACCOUNTS_INVITE.SUCCESS,
        payload: 'mock-invite-code',
      })
    ).toEqual({
      inviteCode: 'mock-invite-code',
    })
  })

  it('should merge the account info if account is not null', () => {
    expect(
      AccountsReducer(
        {
          id: 1,
          name: 'abcde',
          email: 'asdf@gmail.com',
        },
        {
          type: types.ACCOUNTS_GET_ME.SUCCESS,
          payload: {
            name: 'account1',
          },
        })
    ).toEqual({
        id: 1,
        name: 'account1',
        email: 'asdf@gmail.com',
    })
  })
})
