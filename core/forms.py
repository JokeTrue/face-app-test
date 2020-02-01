from django import forms

from core.models import TeamQuest


class TeamQuestForm(forms.ModelForm):
    class Meta:
        model = TeamQuest
        fields = ['id', 'team', 'quest', 'hints']
