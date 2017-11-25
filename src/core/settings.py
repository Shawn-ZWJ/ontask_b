# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from django.conf import settings
from django.db import models

HELP_URL = getattr(settings, 'ONTASK_HELP_URL', '')

if 'siteprefs' in settings.INSTALLED_APPS:
    # Respect those users who doesn't have siteprefs installed.
    from siteprefs.toolbox import patch_locals, register_prefs, pref

    patch_locals()  # That's bootstrap.

    register_prefs(
        pref(HELP_URL,
             verbose_name='URL prefix to access the documentation in the '
                          'static area',
             static=False,
             field=models.CharField(max_length=256, blank=True)),
    )
