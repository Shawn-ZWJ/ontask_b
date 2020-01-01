# -*- coding: utf-8 -*-

"""View to implement the timeline visualization."""

import json
from typing import Optional

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ontask.core.decorators import get_workflow
from ontask.core.permissions import is_instructor
from ontask.models import Log, Workflow


@user_passes_test(is_instructor)
@get_workflow(pf_related='logs')
def show_timeline(
    request: HttpRequest,
    pk: Optional[int] = None,
    workflow: Optional[Workflow] = None,
) -> HttpResponse:
    """Show a vertical timeline of action executions.

    :param request: HTTP request
    :param pk: Action PK. If none, all of them are considered
    :return: HTTP response
    """
    action = None
    if pk:
        action = workflow.actions.filter(pk=pk).first()

        if not action:
            # The action is not part of the selected workflow
            return redirect('home')
        logs = workflow.logs.filter(payload__action_id=action.id)
    else:
        logs = workflow.logs

    event_names = [
        Log.ACTION_DOWNLOAD,
        Log.ACTION_RUN_CANVAS_EMAIL,
        Log.ACTION_RUN_EMAIL,
        Log.ACTION_RUN_JSON,
        Log.ACTION_RUN_JSON_LIST,
        Log.ACTION_RUN_EMAIL_LIST,
        Log.ACTION_SURVEY_INPUT,
        Log.SCHEDULE_CANVAS_EMAIL_EDIT,
        Log.SCHEDULE_EMAIL_EDIT,
        Log.SCHEDULE_JSON_EDIT,
        Log.SCHEDULE_JSON_LIST_EDIT,
        Log.SCHEDULE_EMAIL_LIST_EDIT,
    ]

    # Filter the logs to display and transform into values (process the json
    # and the long value for the log name
    logs = [
        {'id': log.id,
         'name': log.get_name_display(),
         'modified': log.modified,
         'payload': json.dumps(log.payload, indent=2),
         'action_name': log.payload['action'],
         'action_id': log.payload['action_id']}
        for log in logs.filter(name__in=event_names)
    ]

    return render(
        request,
        'action/timeline.html',
        {'event_list': logs, 'action': action})
