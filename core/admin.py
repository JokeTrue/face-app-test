from django.contrib import admin

from core.models import Quest, Team, QuestHint, Tournament, TeamQuest


class QuestHintInline(admin.StackedInline):
    model = QuestHint
    extra = 0
    min_num = 0
    max_num = 3


@admin.register(Quest)
class QuestAdmin(admin.ModelAdmin):
    list_display = ['title', 'description']
    inlines = [QuestHintInline]


class QuestInline(admin.StackedInline):
    model = Quest
    extra = 0
    min_num = 1
    max_num = 8


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    inlines = [QuestInline]
    list_display = ['id', 'title', 'created']


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(QuestHint)
class QuestAnswerAdmin(admin.ModelAdmin):
    pass


@admin.register(TeamQuest)
class TeamQuestAdmin(admin.ModelAdmin):
    list_display = ['team', 'quest', 'hints']