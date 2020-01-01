# -*- coding: utf-8 -*-

"""Send Email Messages with the rendered content in the action."""

import datetime
from time import sleep
from typing import Dict, List, Optional, Union

import html2text
import pytz
from django.conf import settings
from django.contrib.sites.models import Site
from django.core import mail, signing
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.template import Context, Template, TemplateSyntaxError
from django.urls import reverse
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from ontask.action import forms, payloads
from ontask.action.services.run_producer_base import ActionRunServiceBase

import ontask.settings
from ontask import is_correct_email, simplify_datetime_str, models
from ontask.action.evaluate.action import (
    evaluate_action, evaluate_row_action_out, get_action_evaluation_context,
)
from ontask.core.celery import get_task_logger
from ontask.dataops.sql.column_queries import add_column_to_db
from ontask.models import Action, Column, Log

logger = get_task_logger('celery_execution')


def _send_confirmation_message(
    user,
    action: Action,
    nmsgs: int,
) -> None:
    """Send the confirmation message.

    :param user: Destination email
    :param action: Action being considered
    :param nmsgs: Number of messages being sent
    :return:
    """
    # Creating the context for the confirmation email
    now = datetime.datetime.now(pytz.timezone(settings.TIME_ZONE))
    cfilter = action.get_filter()
    context = {
        'user': user,
        'action': action,
        'num_messages': nmsgs,
        'email_sent_datetime': now,
        'filter_present': cfilter is not None,
        'num_rows': action.workflow.nrows,
        'num_selected': action.get_rows_selected(),
    }

    # Create template and render with context
    try:
        html_content = Template(
            str(getattr(ontask.settings, 'NOTIFICATION_TEMPLATE')),
        ).render(Context(context))
        text_content = strip_tags(html_content)
    except TemplateSyntaxError as exc:
        raise Exception(
            _('Syntax error in notification template ({0})').format(str(exc)),
        )

    # Log the event
    context = {
        'num_messages': nmsgs,
        'email_sent_datetime': str(now),
        'filter_present': cfilter is not None,
        'num_rows': action.workflow.nrows,
        'subject': str(ontask.settings.NOTIFICATION_SUBJECT),
        'body': text_content,
        'from_email': str(ontask.settings.NOTIFICATION_SENDER),
        'to_email': [user.email]}
    action.log(user, Log.ACTION_EMAIL_NOTIFY, **context)

    # Send email out
    try:
        send_mail(
            str(ontask.settings.NOTIFICATION_SUBJECT),
            text_content,
            str(ontask.settings.NOTIFICATION_SENDER),
            [user.email],
            html_message=html_content)
    except Exception as exc:
        raise Exception(
            _('Error when sending the notification: {0}').format(str(exc)),
        )


def _check_cc_lists(cc_email_list: List[str], bcc_email_list: List[str]):
    """Verify that the cc lists are correct.

    :param cc_email_list: List of emails to use in CC
    :param bcc_email_list: List of emails to use in BCC
    :return: Nothing or exception
    """
    # Set the cc_email_list and bcc_email_list to the right values
    if cc_email_list is None:
        cc_email_list = []
    if bcc_email_list is None:
        bcc_email_list = []

    # Check that cc and bcc contain list of valid email addresses
    if not all(is_correct_email(email) for email in cc_email_list):
        raise Exception(_('Invalid email address in cc email'))
    if not all(is_correct_email(email) for email in bcc_email_list):
        raise Exception(_('Invalid email address in bcc email'))


def _create_track_column(action: Action) -> str:
    """Create an additional column for email tracking.

    :param action: Action to consider
    :return: column name
    """
    # Make sure the column name does not collide with an existing one
    idx = 0  # Suffix to rename
    cnames = [col.name for col in action.workflow.columns.all()]
    while True:
        idx += 1
        track_col_name = 'EmailRead_{0}'.format(idx)
        if track_col_name not in cnames:
            break

    # Add the column if needed (before the mass email to avoid overload
    # Create the new column and store
    column = Column(
        name=track_col_name,
        description_text='Emails sent with action {0} on {1}'.format(
            action.name,
            simplify_datetime_str(datetime.datetime.now(pytz.timezone(
                settings.TIME_ZONE))),
        ),
        workflow=action.workflow,
        data_type='integer',
        is_key=False,
        position=action.workflow.ncols + 1,
    )
    column.save()

    # Increase the number of columns in the workflow
    action.workflow.ncols += 1
    action.workflow.save()

    # Add the column to the DB table
    add_column_to_db(
        action.workflow.get_data_frame_table_name(),
        track_col_name,
        'integer',
        0)

    return track_col_name


def _create_single_message(
    msg_body_sbj_to: List[str],
    track_str: str,
    from_email: str,
    cc_email_list: List[str],
    bcc_email_list: List[str],
) -> Union[EmailMessage, EmailMultiAlternatives]:
    """Create either an EmailMessage or EmailMultiAlternatives object.

    :param msg_body_sbj_to: List with body, subject, to
    :param track_str: String to add to track
    :param from_email: From email
    :param cc_email_list: CC list
    :param bcc_email_list: BCC list

    :return: Either EmailMessage or EmailMultiAlternatives
    """
    if settings.EMAIL_HTML_ONLY:
        # Message only has the HTML text
        msg = EmailMessage(
            msg_body_sbj_to[1],
            msg_body_sbj_to[0] + track_str,
            from_email,
            [msg_body_sbj_to[2]],
            bcc=bcc_email_list,
            cc=cc_email_list,
        )
        msg.content_subtype = 'html'
    else:
        # Get the plain text content and bundle it together with the HTML
        # in a message to be added to the list.
        msg = EmailMultiAlternatives(
            msg_body_sbj_to[1],
            html2text.html2text(msg_body_sbj_to[0]),
            from_email,
            [msg_body_sbj_to[2]],
            bcc=bcc_email_list,
            cc=cc_email_list,
        )
        msg.attach_alternative(msg_body_sbj_to[0] + track_str, 'text/html')
    return msg


def _create_messages(
    user,
    action: Action,
    action_evals: List,
    track_col_name: str,
    action_info: Dict,
) -> List[Union[EmailMessage, EmailMultiAlternatives]]:
    """Create the email messages to send and the tracking ids.

    :param user: User that sends the message (encoded in the track-id)
    :param action: Action to process
    :param action_evals: Action content already evaluated
    :param track_col_name: column name to track
    :param action_info: Dictionary with the required fields
    :return:
    """
    # Context to log the events (one per email)
    context = {
        'email_sent_datetime': str(
            datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)),
        ),
    }

    # Everything seemed to work to create the messages.
    msgs = []
    # for msg_body, msg_subject, msg_to in action_evals:
    for msg_body_sbj_to in action_evals:
        # If read tracking is on, add suffix for message (or empty)
        track_str = ''
        if action_info['track_read']:
            # The track id must identify: action & user
            track_str = (
                '<img src="https://{0}{1}{2}?v={3}" alt=""'
                + ' style="position:absolute; visibility:hidden"/>'
            ).format(
                Site.objects.get_current().domain,
                settings.BASE_URL,
                reverse('trck'),
                signing.dumps(
                    {
                        'action': action.id,
                        'sender': user.email,
                        'to': msg_body_sbj_to[2],
                        'column_to': action_info['item_column'],
                        'column_dst': track_col_name,
                    },
                ),
            )

        msg = _create_single_message(
            msg_body_sbj_to,
            track_str,
            user.email,
            action_info['cc_email'],
            action_info['bcc_email'],
        )
        msgs.append(msg)

        # Log the event
        context['subject'] = msg.subject
        context['body'] = msg.body
        context['from_email'] = msg.from_email
        context['to_email'] = msg.to[0]
        if track_str:
            context['track_id'] = track_str
        action.log(user, Log.ACTION_EMAIL_SENT, **context)

    return msgs


def _deliver_msg_burst(
    msgs: List[Union[EmailMessage, EmailMultiAlternatives]],
):
    """Deliver the messages in bursts.

    :param msgs: List of either EmailMessage or EmailMultiAlternatives
    :return: Nothing.
    """
    if len(msgs) == 0:
        # bypass trivial case, no list given
        return

    # Partition the list of emails into chunks as per the value of EMAIL_BURST
    chunk_size = len(msgs)
    wait_time = 0
    if settings.EMAIL_BURST:
        chunk_size = settings.EMAIL_BURST
        wait_time = settings.EMAIL_BURST_PAUSE
    msg_chunks = [
        msgs[idx:idx + chunk_size]
        for idx in range(0, len(msgs), chunk_size)
    ]
    for idx, msg_chunk in enumerate(msg_chunks):
        # Mass mail!
        mail.get_connection().send_messages(msg_chunk)

        if idx != len(msg_chunks) - 1:
            logger.info(
                'Email Burst (%s) reached. Waiting for %s secs',
                str(len(msg_chunk)),
                str(wait_time))
            sleep(wait_time)


def send_emails(
    user,
    action: Action,
    action_info: Dict,
    log_item: Optional[Log] = None,
) -> List[str]:
    """Send action content evaluated for each row.

    Sends the emails for the given action and with the
    given subject. The subject will be evaluated also with respect to the
    rows, attributes, and conditions.

    The messages are sent in bursts with a pause in seconds as specified by the
    configuration variables EMAIL_BURST  and EMAIL_BURST_PAUSE

    :param user: User object that executed the action
    :param action: Action from where to take the messages
    :param log_item: Log object to store results
    :param action_info: Dictionary key, value as defined in EmailPayload

    :return: List of strings with the "to" fields used.
    """
    # Evaluate the action string, evaluate the subject, and get the value of
    # the email column.
    item_column = action.workflow.columns(pk=action_info['item_column'])
    action_evals = evaluate_action(
        action,
        extra_string=action_info['subject'],
        column_name=item_column.name,
        exclude_values=action_info['exclude_values'])

    # Turn cc_email and bcc email into lists
    action_info['cc_email'] = action_info['cc_email'].split()
    action_info['bcc_email'] = action_info['bcc_email'].split()

    _check_cc_lists(action_info['cc_email'], action_info['bcc_email'])

    track_col_name = ''
    if action_info['track_read']:
        track_col_name = _create_track_column(action)
        # Get the log item payload to store the tracking column
        log_item.payload['track_column'] = track_col_name
        log_item.save()

    msgs = _create_messages(
        user,
        action,
        action_evals,
        track_col_name,
        action_info,
    )

    _deliver_msg_burst(msgs)

    if action_info['send_confirmation']:
        # Confirmation message requested
        _send_confirmation_message(user, action, len(msgs))

    return [msg.to[0] for msg in msgs]


def send_list_email(
    user,
    action: Action,
    action_info: Dict,
    log_item: Optional[Log] = None,
) -> List[str]:
    """Send action content evaluated once to include lists.

    Sends a single email for the given action with the lists expanded and with
    the given subject evaluated also with respect to the attributes.

    :param user: User object that executed the action
    :param action: Action from where to take the messages
    :param log_item: Log object to store results
    :param action_info: Dictionary key, value as defined in EmailPayload

    :return: Empty list (because it is a single email sent)
    """
    # Evaluate the action string, evaluate the subject, and get the value of
    # the email column.
    action_text = evaluate_row_action_out(
        action,
        get_action_evaluation_context(action, {}))

    # Turn cc_email and bcc email into lists
    action_info['cc_email'] = action_info['cc_email'].split()
    action_info['bcc_email'] = action_info['bcc_email'].split()

    _check_cc_lists(action_info['cc_email'], action_info['bcc_email'])

    # Context to log the events
    msg = _create_single_message(
        [action_text, action_info['subject'], action_info['email_to']],
        '',
        user.email,
        action_info['cc_email'],
        action_info['bcc_email'],
    )

    try:
        # Send email out
        mail.get_connection().send_messages([msg])
    except Exception as exc:
        raise Exception(
            _('Error when sending the list email: {0}').format(str(exc)),
        )

    # Log the event
    context = {
        'email_sent_datetime': str(
            datetime.datetime.now(pytz.timezone(settings.TIME_ZONE)),
        ),
        'subject': msg.subject,
        'body': msg.body,
        'from_email': msg.from_email,
        'to_email': msg.to[0]}
    action.log(user, Log.ACTION_EMAIL_SENT, **context)

    return []


class ActionRunServiceEmail(ActionRunServiceBase):
    """Class to serive running an email action."""

    def __init__(self):
        """Assign """
        super().__init__(forms.EmailActionRunForm, payloads.EmailPayload)
        # self.info_initial = {'post_url': reverse('action:email_done')}
        self.template = 'action/request_email_data.html'
        self.log_event = models.Log.ACTION_RUN_EMAIL

