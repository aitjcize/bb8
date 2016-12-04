# -*- coding: utf-8 -*-
"""
    Account Management
    ~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

from bb8.backend import payment
from bb8.backend.database import (DatabaseManager, Account, AccountUser,
                                  AccountTierEnum)


def register(data, invite=None):
    """Register the user."""
    if invite:
        account, payload = Account.from_invite_code(invite)
        if payload['email'] != data['email']:
            raise RuntimeError('invitation link not intended for this '
                               'email')
    else:
        # TODO(aitjcize): only do this when the account email is confirmed
        customer = payment.create_customer(data['email'])
        payment.subscribe(customer.id)
        account = Account(name=unicode(data['email']),
                          membership=AccountTierEnum.Trial,
                          stripe_customer_id=customer.id).add()

    account_user = AccountUser(
        account=account, email=data['email']
    ).set_passwd(data['passwd']).add()

    DatabaseManager.commit()
    return account_user
