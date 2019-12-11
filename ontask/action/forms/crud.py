# -*- coding: utf-8 -*-

"""Forms to process action related fields.

ActionUpdateForm: Basic form to process the name/description of an action

ActionForm: Inherits from Basic to process name, description and type

ActionDescriptionForm: Inherits from basic but process only description (for
    surveys)

FilterForm: Form to process filter elements

ConditionForm: Form to process condition elements
"""
from builtins import str
import json
from typing import Dict

from django import forms
from django.utils.translation import ugettext_lazy as _

from ontask import is_legal_name, models
from ontask.core import RestrictedFileField
import ontask.settings


class ActionUpdateForm(forms.ModelForm):
    """Basic class to edit name and description."""

    def __init__(self, *args, **kwargs):
        """Store user and wokflow."""
        self.workflow = kwargs.pop('workflow')
        super().__init__(*args, **kwargs)

    def clean(self) -> Dict:
        """Verify that the name is not taken."""
        form_data = super().clean()

        # Check if the name already exists
        name_exists = self.workflow.actions.filter(
            name=self.data['name'],
        ).exclude(id=self.instance.id).exists()
        if name_exists:
            self.add_error(
                'name',
                _('There is already an action with this name.'),
            )

        return form_data

    class Meta:
        """Select Action and the two fields."""

        model = models.Action
        fields = ('name', 'description_text')


class ActionForm(ActionUpdateForm):
    """Edit name, description and action type."""

    def __init__(self, *args: str, **kargs: str):
        """Adjust widget choices depending on action type."""
        super().__init__(*args, **kargs)

        at_field = self.fields['action_type']
        at_field.widget.choices = models.Action.AVAILABLE_ACTION_TYPES.items()

        if len(models.Action.AVAILABLE_ACTION_TYPES) == 1:
            # There is only one type of action. No need to generate the field.
            # Set to value and hide
            at_field.widget = forms.HiddenInput()
            at_field.initial = models.Action.AVAILABLE_ACTION_TYPES.items(
            )[0][0]

    class Meta(ActionUpdateForm.Meta):
        """Select action and the three fields."""

        model = models.Action
        fields = ('name', 'description_text', 'action_type')


class ActionDescriptionForm(forms.ModelForm):
    """Form to edit the description of an action."""

    class Meta:
        """Select model and the description field."""

        model = models.Action
        fields = ('description_text',)


class FilterForm(forms.ModelForm):
    """Form to read/write information about a filter."""

    action = None
    old_name = None

    def __init__(self, *args, **kwargs):
        """Adjust formula field parameters to use QueryBuilder."""
        self.action = kwargs.pop('action')

        super().__init__(*args, **kwargs)

        # Required enforced in the server (not in the browser)
        self.fields['formula'].required = False

    class Meta:
        """Select model and fields."""

        model = models.Condition
        fields = ('description_text', 'formula')
        widgets = {'formula': forms.HiddenInput()}

class ConditionForm(FilterForm):
    """Form to read information about a condition.

    The same as the filter but we need to enforce that the name is a valid
    variable name
    """

    def __init__(self, *args, **kwargs):
        """Remember the old name."""
        super().__init__(*args, **kwargs)

        # Remember the condition name to perform content substitution
        if self.instance.name:
            self.old_name = self.instance.name

    def clean(self) -> Dict:
        """Check that data is not empty."""
        form_data = super().clean()

        name = form_data.get('name')
        if not name:
            self.add_error('name', _('Name cannot be empty'))
            return form_data

        msg = is_legal_name(form_data['name'])
        if msg:
            self.add_error('name', msg)

        # Check if the name already exists
        name_exists = self.action.conditions.filter(
            name=name,
        ).exclude(id=self.instance.id).exists()
        if name_exists:
            self.add_error(
                'name',
                _('There is already a condition with this name.'),
            )

        # Check that the name does not collide with other attribute or column
        if name in self.action.workflow.get_column_names():
            self.add_error(
                'name',
                _('The workflow has a column with this name.'),
            )

        # New condition name does not collide with attribute names
        if name in list(self.action.workflow.attributes.keys()):
            self.add_error(
                'name',
                _('The workflow has an attribute with this name.'),
            )

        return form_data

    class Meta(FilterForm.Meta):
        """Select name as extra field."""

        fields = ('name', 'description_text', 'formula')


class ActionImportForm(forms.Form):
    """Form to edit information to import an action."""

    upload_file = RestrictedFileField(
        max_upload_size=int(ontask.settings.MAX_UPLOAD_SIZE),
        content_types=json.loads(str(ontask.settings.CONTENT_TYPES)),
        allow_empty_file=False,
        label=_('File with previously exported OnTask actions'),
        help_text=_('File containing a previously exported action'),
    )


class RubricCellForm(forms.ModelForm):
    """Edit the content of a RubricCellForm."""

    class Meta:
        """Select Action and the two fields."""

        model = models.RubricCell
        fields = ('description_text', 'feedback_text')


class RubricLOAForm(forms.Form):
    """Edit the levels of attainment of a rubric."""

    levels_of_attainment = forms.CharField(
        strip=True,
        required=True,
        label=_('Comma separated list of levels of attainment'))

    def __init__(self, *args, **kwargs):
        """Store the criteria."""
        self.criteria = kwargs.pop('criteria')

        super().__init__(*args, **kwargs)

        self.fields['levels_of_attainment'].initial = ', '.join(
            self.criteria[0].categories)

    def clean(self) -> Dict:
        """Check that the number of LOAs didn't change."""
        form_data = super().clean()

        current_n_loas = [
            loa
            for loa in form_data['levels_of_attainment'].split(',')
            if loa]

        if len(current_n_loas) != len(self.criteria[0].categories):
            self.add_error(
                'levels_of_attainment',
                _('The number of levels cannot change.'))

        return form_data
