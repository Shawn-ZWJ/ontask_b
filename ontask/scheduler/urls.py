# -*- coding: utf-8 -*-

"""URLs for the scheduler package."""

from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from ontask.scheduler import api
from ontask.scheduler.views import delete, edit_action_run, finish_scheduling, index, view

app_name = 'scheduler'

urlpatterns = [

    # List all schedule actions
    path('', index, name='index'),

    # Create scheduled email action
    path(
        '<int:pk>/create_action_run/',
        edit_action_run,
        name='create_action_run'),

    # Edit scheduled email action
    path('<int:pk>/edit_action_run/', edit_action_run, name='edit_action_run'),

    # View the details of a scheduled action
    path('<int:pk>/view/', view, name='view'),

    # Delete scheduled email action
    path('<int:pk>/delete/', delete, name='delete'),

    path(
        'finish_scheduling/',
        finish_scheduling,
        name='finish_scheduling'),

    # API
    path(
        'scheduled_email/',
        api.ScheduledActionEmailAPIListCreate.as_view(),
        name='api_scheduled_email'),

    path(
        'scheduled_json/',
        api.ScheduledActionJSONAPIListCreate.as_view(),
        name='api_scheduled_json'),

    # Get, update content or destroy scheduled actions
    path(
        '<int:pk>/rud_email/',
        api.ScheduledEmailAPIRetrieveUpdateDestroy.as_view(),
        name='api_rud_email'),
    path(
        '<int:pk>/rud_json/',
        api.ScheduledJSONAPIRetrieveUpdateDestroy.as_view(),
        name='api_rud_json'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
