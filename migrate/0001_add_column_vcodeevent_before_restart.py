#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import logging
from playhouse.migrate import migrate
from peewee import BooleanField


logger = logging.getLogger('data')


def forward(migrator):
    migrate(
        migrator.add_column('vcodeevent', 'before_restart', BooleanField(null=True, default=None)),
    )
