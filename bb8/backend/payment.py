# -*- coding: utf-8 -*-
"""
    Payment Management
    ~~~~~~~~~~~~~~~~~~

    Copyright 2016 bb8 Authors
"""

import stripe

from flask import g

from bb8 import config
from bb8.backend.database import Account, AccountTierEnum


stripe.api_key = config.STRIPE_API_KEY


class InvalidSourceTokenError(Exception):
    """This is raised when the stripe source token is invalid."""
    pass


def create_all_plans():
    """Create all plans from configuration."""
    # Delete all old plans
    for plan in stripe.Plan.list():
        plan.delete()

    # Re-create all plans
    for plan in config.STRIPE_PLANS:
        stripe.Plan.create(**plan)


def create_customer(email):
    return stripe.Customer.create(email=email)


def subscribe(customer_id, plan='basic-monthly'):
    stripe.Subscription.create(customer=customer_id, plan=plan)


def update_payment(data):
    customer = stripe.Customer.retrieve(g.account.stripe_customer_id)

    subscription = data.get('subscription')
    if subscription:
        plan = subscription['plan']
        action = subscription['action']
        current = list(stripe.Subscription.list(customer=customer, plan=plan))

        if action == 'Start':
            if current:  # Already has a valid subscription
                return
            subscribe(g.account.stripe_customer_id, plan)
        elif action == 'Stop':
            current[0].delete()

    token = data.get('token')
    if token:
        try:
            customer.sources.create(source=token)
        except Exception:
            raise InvalidSourceTokenError


def process_successful_payment_event(event):
    data = event['data']['object']
    if not data['paid']:
        return

    # Update subscription valid period
    customer_id = data['customer']

    account = Account.get_by(stripe_customer_id=customer_id, single=True)
    if account is None:
        raise RuntimeError('Non-exist customer payment received: %s' %
                           customer_id)

    subscription = data['lines']['data'][0]
    account.active_until = subscription['period']['end']
    sub = stripe.Subscription.retrieve(id=subscription['id'])

    if sub.status != 'trialing':
        account.membership = AccountTierEnum.Basic


def process_failed_payment_event(unused_event):
    """Payment failed, send an email to the user."""
    pass


def process_trial_will_end_event(unused_event):
    """Trial will end, send an email to the user."""
    pass
