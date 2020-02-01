from datetime import timedelta
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _


class TeamManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, password, **extra_fields):
        """
        Create and save a user with the given username, email, and password.
        """
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(password, **extra_fields)

    def create_superuser(self, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(password, **extra_fields)


class Team(AbstractBaseUser, PermissionsMixin):
    objects = TeamManager()

    class Meta:
        verbose_name = 'Команда'
        verbose_name_plural = 'Команды'

    email = models.EmailField('Email', null=True, unique=True, blank=True)
    name = models.CharField('Название команды', max_length=30, null=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log '
                    'into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    def __str__(self):
        return '#{}: {}'.format(self.id, self.name)


class Tournament(models.Model):
    class Meta:
        verbose_name = 'Турнир'
        verbose_name_plural = 'Турниры'

    title = models.CharField('Название', max_length=255)
    created = models.DateTimeField('Дата создания', default=timezone.now)


    def __str__(self):
        return self.title

    @property
    def end_time(self):
        return self.created + timedelta(hours=5)

class Quest(models.Model):
    class Meta:
        verbose_name = 'Квест'
        verbose_name_plural = 'Квесты'

    tournament = models.ForeignKey(Tournament, verbose_name='Турнир', on_delete=models.CASCADE)
    title = models.CharField('Название', max_length=255)
    coords = models.CharField('Координаты', max_length=255)
    description = models.TextField('Описание', max_length=300)
    answer = models.CharField('Ответ', max_length=255)

    def __str__(self):
        return self.title


class QuestHint(models.Model):
    class Meta:
        verbose_name = 'Подсказка на квест'
        verbose_name_plural = 'Подсказки на квесты'

    quest = models.ForeignKey(Quest, verbose_name='Квест', on_delete=models.CASCADE, related_name='answers')
    text = models.TextField('Подсказка')

    def __str__(self):
        return 'Квест #{} – Подсказк #{}'.format(self.quest.id, self.id)


class TeamQuestStatuses:
    NOT_READY = 'NOT_READY'
    READY = 'READY'
    FAIL = 'FAIL'

    STATUSES = (
        (NOT_READY, 'Не начато'),
        (READY, 'Сдано'),
        (FAIL, 'Провалено')
    )


class TeamQuest(models.Model):
    class Meta:
        verbose_name = 'Ответ команды'
        verbose_name_plural = 'Ответы команд'
        unique_together = ['team', 'quest']

    team = models.ForeignKey(Team, verbose_name='Команда', on_delete=models.CASCADE)
    quest = models.ForeignKey(Quest, verbose_name='Квест', on_delete=models.CASCADE)
    hints = models.SmallIntegerField('Количество подсказок', default=0)
    status = models.CharField(
        choices=TeamQuestStatuses.STATUSES,
        default=TeamQuestStatuses.NOT_READY,
        max_length=25
    )
    done_time = models.DateTimeField('Дата сдачи', null=True, blank=True, default=None)


    @property
    def get_readable_status(self):
        return dict(TeamQuestStatuses.STATUSES).get(self.status)

    def __str__(self):
        return 'Команда #{} – Квест #{}'.format(self.team.id, self.quest.id)
