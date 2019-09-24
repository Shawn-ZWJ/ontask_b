# -*- coding: utf-8 -*-

"""URL for actions."""

from django.urls import path

from ontask.action.views import (
    ActionCreateView, ActionUpdateView, ConditionCreateView, FilterCreateView,
    action_import, action_index, action_out_save_content, action_zip_export,
    clone_action, clone_condition, delete_action, delete_condition,
    delete_filter, edit_action, edit_condition, edit_description, edit_filter,
    export_ask, export_done, export_download, preview_next_all_false_response,
    preview_response, run_action, run_action_item_filter,
    run_canvas_email_done, run_email_done, run_json_done, run_survey_row,
    run_survey_ss, run_zip_done, select_column_action,
    select_condition_for_question, serve_action, show_timeline, showurl,
    shuffle_questions, survey_thanks, unselect_column_action, zip_action,
    serve_action_lti, edit_rubric_cell, edit_rubric_loas,
    toggle_question_change)

app_name = 'action'

urlpatterns = [
    #
    # Action CRUD
    #
    # List them all
    path('', action_index, name='index'),
    path('<int:wid>/index/', action_index, name='index_set'),

    # Create an action
    path('create/', ActionCreateView.as_view(), name='create'),

    # Show timeline
    path('timeline/', show_timeline, name='timeline'),
    path('<int:pk>/timeline/', show_timeline, name='timeline'),

    # Edit action
    path('<int:pk>/edit/', edit_action, name='edit'),

    # Save action out content
    path(
        '<int:pk>/action_out_save_content/',
        action_out_save_content,
        name='action_out_save_content'),

    # Action export ask
    path('<int:pk>/export_ask/', export_ask, name='export_ask'),

    # Action export done
    path('<int:pk>/export_done/', export_done, name='export_done'),

    # Action export done
    path(
        '<int:pk>/export_download/',
        export_download,
        name='export_download'),

    # Action import
    path('import/', action_import, name='import'),

    # Update an action
    path('<int:pk>/update/', ActionUpdateView.as_view(), name='update'),

    # Clone the action
    path('<int:pk>/clone_action/', clone_action, name='clone_action'),

    # Nuke the action
    path('<int:pk>/delete/', delete_action, name='delete'),

    # Run ZIP action
    path('<int:pk>/zip/', zip_action, name='zip_action'),

    # Run action
    path('<int:pk>/run/', run_action, name='run'),

    #
    # Personalised text and JSON action steps
    #
    path('item_filter/', run_action_item_filter, name='item_filter'),

    #
    # URLs to use when action finishes run
    #
    path('email_done/', run_email_done, name='email_done'),
    path('zip_done/', run_zip_done, name='zip_done'),
    path('zip_export/', action_zip_export, name='zip_export'),
    path('json_done/', run_json_done, name='json_done'),
    path(
        'canvas_email_done/',
        run_canvas_email_done,
        name='canvas_email_done'),

    #
    # ACTION IN EDIT PAGE
    #
    # Manage columns for action in
    path(
        '<int:pk>/<int:cpk>/<int:key>/select_column_action/',
        select_column_action,
        name='select_key_column_action'),
    path(
        '<int:pk>/select_column_action/',
        select_column_action,
        name='unselect_key_column_action'),

    # Select column for action in
    path(
        '<int:pk>/<int:cpk>/select_column_action/',
        select_column_action,
        name='select_column_action'),

    # Unselect column for action in
    path(
        '<int:pk>/<int:cpk>/unselect_column_action/',
        unselect_column_action,
        name='unselect_column_action'),

    # Toggle shuffle action-in
    path(
        '<int:pk>/shuffle_questions/',
        shuffle_questions,
        name='shuffle_questions'),

    # Toggle question changes
    path(
        '<int:pk>/toggle_question_change/',
        toggle_question_change,
        name='toggle_question_change'),

    # Select condition for a column/question
    path(
        '<int:pk>/<int:condpk>/select_condition/',
        select_condition_for_question,
        name='edit_in_select_condition'),
    path(
        '<int:tpk>/select_condition/',
        select_condition_for_question,
        name='edit_in_select_condition'),

    # Rubric URLs
    path(
        '<int:pk>/<int:cid>/<int:loa_pos>/rubriccell_edit',
        edit_rubric_cell,
        name='rubriccell_edit'),
    path(
        '<int:pk>/rubric_loas_edit',
        edit_rubric_loas,
        name='rubric_loas_edit'),

    #
    # RUN SURVEY
    #
    # Server side update of the run survey page for action in
    path('<int:pk>/run_survey_ss/', run_survey_ss, name='run_survey_ss'),

    # Run action in a row. Can be executed by the instructor or the
    # learner!!
    path(
        '<int:pk>/run_survey_row/',
        run_survey_row,
        name='run_survey_row'),

    # Say thanks
    path('thanks/', survey_thanks, name='thanks'),

    #
    # Preview action out
    #
    path(
        '<int:pk>/<int:idx>/preview/',
        preview_response,
        name='preview'),
    path(
        '<int:pk>/<int:idx>/preview_next_all_false/',
        preview_next_all_false_response,
        name='preview_all_false'),

    # Allow url on/off toggle
    path('<int:pk>/showurl/', showurl, name='showurl'),

    #
    # Serve the personalised content
    #
    path('<int:action_id>/serve/', serve_action, name='serve'),
    path('serve/', serve_action_lti, name='serve_lti'),

    #
    # Edit action description and name
    #
    path(
        '<int:pk>/edit_description/',
        edit_description,
        name='edit_description'),

    #
    # FILTERS
    #
    path(
        '<int:pk>/create_filter/',
        FilterCreateView.as_view(),
        name='create_filter'),
    path('<int:pk>/edit_filter/', edit_filter, name='edit_filter'),
    path('<int:pk>/delete_filter/', delete_filter, name='delete_filter'),

    #
    # CONDITIONS
    #
    path(
        '<int:pk>/create_condition/',
        ConditionCreateView.as_view(),
        name='create_condition'),
    path('<int:pk>/edit_condition/', edit_condition, name='edit_condition'),
    path(
        '<int:pk>/delete_condition/',
        delete_condition,
        name='delete_condition'),

    # Clone the condition
    path('<int:pk>/clone_condition/', clone_condition, name='clone_condition'),
    path(
        '<int:pk>/<int:action_pk>/clone_condition/',
        clone_condition,
        name='clone_condition'),
]
