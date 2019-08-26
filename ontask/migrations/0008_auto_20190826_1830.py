# Generated by Django 2.2.4 on 2019-08-26 09:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ontask', '0007_auto_20190825_1810'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='name',
            field=models.CharField(choices=[('workflow_create', 'Workflow created'), ('workflow_update', 'Workflow updated'), ('workflow_delete', 'Workflow deleted'), ('workflow_data_upload', 'Data uploaded to workflow'), ('workflow_data_merge', 'Data merged into workflow'), ('workflow_data_failedmerge', 'Failed data merge into workflow'), ('workflow_data_flush', 'Workflow data flushed'), ('workflow_attribute_create', 'New attribute in workflow'), ('workflow_attribute_update', 'Attributes updated in workflow'), ('workflow_attribute_delete', 'Attribute deleted'), ('workflow_share_add', 'User share added'), ('workflow_share_delete', 'User share deleted'), ('workflow_import', 'Import workflow'), ('workflow_clone', 'Workflow cloned'), ('workflow_update_lusers', 'Update list of workflow users'), ('workflow_star', 'Toggle workflow star'), ('column_add', 'Column added'), ('column_add_formula', 'Column with formula created'), ('column_add_random', 'Column with random values created'), ('column_rename', 'Column renamed'), ('column_delete', 'Column deleted'), ('column_clone', 'Column cloned'), ('column_restrict', 'Column restricted'), ('action_create', 'Action created'), ('action_update', 'Action updated'), ('action_delete', 'Action deleted'), ('action_clone', 'Action cloned'), ('action_email_sent', 'Emails sent'), ('action_list_email_sent', 'Email with data list sent'), ('action_canvas_email_sent', 'Canvas Emails sent'), ('action_email_notify', 'Notification email sent'), ('action_email_read', 'Email read'), ('action_serve_toggled', 'Action URL toggled'), ('action_served_execute', 'Action served'), ('action_import', 'Action imported'), ('action_json_sent', 'Emails sent'), ('condition_create', 'Condition created'), ('condition_update', 'Condition updated'), ('condition_delete', 'Condition deleted'), ('condition_clone', 'Condition cloned'), ('tablerow_update', 'Table row updated'), ('tablerow_create', 'Table row created'), ('survey_input', 'Survey data input'), ('view_create', 'Table view created'), ('view_edit', 'Table view edited'), ('view_delete', 'Table view deleted'), ('view_clone', 'Table view cloned'), ('filter_create', 'Filter created'), ('filter_update', 'Filter updated'), ('filter_delete', 'Filter deleted'), ('plugin_create', 'Plugin created'), ('plugin_update', 'Plugin updated'), ('plugin_delete', 'Plugin deleted'), ('plugin_execute', 'Plugin executed'), ('sql_connection_create', 'SQL connection created'), ('sql_connection_edit', 'SQL connection updated'), ('sql_connection_delete', 'SQL connection deleted'), ('sql_connection_clone', 'SQL connection cloned'), ('schedule_email_edit', 'Edit scheduled email action'), ('schedule_email_delete', 'Delete scheduled email action'), ('schedule_email_execute', 'Execute scheduled email action'), ('schedule_send_list_edit', 'Edit scheduled send list action'), ('schedule_send_list_delete', 'Delete scheduled send list action'), ('schedule_send_list_execute', 'Execute scheduled send list action'), ('schedule_canvas_email_edit', 'Edit scheduled canvas email action'), ('schedule_canvas_email_execute', 'Execute scheduled canvas email action'), ('schedule_canvas_email_delete', 'Delete scheduled canvas email action'), ('download_zip_action', 'Download a ZIP with personalized text'), ('schedule_json_edit', 'Edit scheduled JSON action'), ('schedule_json_delete', 'Delete scheduled JSON action'), ('schedule_json_execute', 'Execute scheduled JSON action')], max_length=256),
        ),
    ]
