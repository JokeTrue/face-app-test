from math import ceil

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import FormView, TemplateView

from FaceAppTest.settings import DEFAULT_TOURNAMENT_ID
from core.forms import TeamQuestForm
from core.models import TeamQuest, Quest, TeamQuestStatuses, Team, Tournament


class LoginPageView(LoginView):
    template_name = 'login.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.get_success_url())
        else:
            return super(LoginPageView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('quests')


class QuestsView(LoginRequiredMixin, FormView):
    model = TeamQuest
    template_name = 'quests_list.html'
    login_url = '/login'
    form_class = TeamQuestForm

    def get_queryset(self):
        qr = []
        quests = Quest.objects.filter(tournament__id=DEFAULT_TOURNAMENT_ID).order_by('id')

        for quest in quests:
            obj, _ = TeamQuest.objects.get_or_create(
                team=self.request.user,
                quest=quest
            )
            qr.append(obj)

        return qr

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['qr'] = self.get_queryset()
        return ctx

    def post(self, request, *args, **kwargs):
        team_quest = TeamQuest.objects.get(pk=self.request.POST['id'])
        answer = self.request.POST['answer']

        form = self.form_class(self.request.POST, instance=team_quest)

        if form.is_valid():
            form.instance.done_time = timezone.now()

            if form.instance.quest.answer == answer:
                form.instance.status = TeamQuestStatuses.READY
            else:
                form.instance.status = TeamQuestStatuses.FAIL

            form.save()

        return redirect('/quests')

    def form_valid(self, form):
        obj = form.save(commit=False)
        answer = self.request.POST['answer']

        if obj.quest.answer == answer:
            obj.status = TeamQuestStatuses.READY
        else:
            obj.status = TeamQuestStatuses.FAIL

        obj.save()

        return redirect('quests')


class TournamentView(LoginRequiredMixin, TemplateView):
    template_name = 'tournament.html'

    def get_context_data(self):
        ctx = super().get_context_data()

        ctx['tournament'] = Tournament.objects.get(pk=DEFAULT_TOURNAMENT_ID)
        team_quests = TeamQuest.objects.filter(quest__tournament=ctx['tournament'])
        teams = Team.objects.filter(pk__in=team_quests.values_list('team__pk', flat=True))

        ctx['teams'] = []
        for team in teams:
            inner_team_quests = team_quests.filter(
                team=team,
                status__in=[TeamQuestStatuses.FAIL, TeamQuestStatuses.READY]
            ).order_by('quest_id')

            team.quests = inner_team_quests
            team.total_done = inner_team_quests.filter(status=TeamQuestStatuses.READY).count()

            quests_time = sum(
                map(lambda item: (item.done_time - ctx['tournament'].created).total_seconds() / 60.0, inner_team_quests)
            )
            hints_time = sum(map(lambda item: 15 * item.hints, inner_team_quests))
            failed_time = inner_team_quests.filter(status=TeamQuestStatuses.FAIL).count() * 30

            team.time = ceil(quests_time + hints_time + failed_time)
            ctx['teams'].append(team)

        ctx['teams'] = sorted(ctx['teams'], key=lambda i: (-i.total_done, i.time))
        ctx['quests'] = Quest.objects.filter(tournament=DEFAULT_TOURNAMENT_ID).order_by('id')
        return ctx
