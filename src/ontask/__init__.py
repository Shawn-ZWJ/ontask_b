# -*- coding: utf-8 -*-
"""
Basic functions and definitions used all over the platform.
"""


import json

from ontask.celery import app as celery_app

__all__ = ['celery_app', 'OnTaskException']

from django.utils.translation import ugettext_lazy as _

__version__ = 'B.4.0.0'

# Dictionary to store in the session the data between forms.
action_session_dictionary = 'action_run_payload'


def is_legal_name(val):
    """
    Function to check if a string is a valid column name, attribute name or
    condition name.

    These are the characters that have been found to be problematic with
    these names and the responsible for these anomalies:

    - " Provokes a db error when handling the templates due to the encoding
      produced by the text editor.

    - ' String delimiter, python messes around with it and it is too complex to
        handle all possible cases and translations.

    In principle, arbitrary combinations of the following symbols should be
    handle by OnTask::

      !#$%&()*+,-./:;<=>?@[\]^_`{|}~

    :param val: String with the column name
    :return: String with a message suggesting changes, or None if string correct

    """

    if "'" in val:
        return _("The symbol ' cannot be used in the column name.")

    if '"' in val:
        return _('The symbol " cannot be used in the column name.')

    return None


def fix_pctg_in_name(val):
    """
    Function that escapes a value for SQL processing (replacing % by double %%)
    :param val: Value to escape
    :return: Escaped value
    """
    return val.replace('%', '%%')


def is_json(text):
    try:
        _ = json.loads(text)
    except ValueError:
        return False
    return True


def get_action_payload(request):
    """
    Gets the payload from the current session
    :param request: Request object
    :return: request.session[session_dictionary_name] or None
    """

    return request.session.get(action_session_dictionary, None)


class OnTaskException(Exception):
    """
    Generic class in OnTask for our own exception
    """

    def __init__(self, msg, value):
        self.msg = msg
        self.value = value

    def __str__(self):
        return repr(self.value)
