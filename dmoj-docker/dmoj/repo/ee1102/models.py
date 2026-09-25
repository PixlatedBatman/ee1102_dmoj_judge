from django.db import models

from judge.models import Problem


class ProblemStarter(models.Model):
    """Starter code pre-filled in the problem page's inline editor."""
    problem = models.OneToOneField(Problem, on_delete=models.CASCADE, related_name='ee_starter')
    code = models.TextField(verbose_name='starter code', blank=True,
                            help_text='Python 3 code shown in the editor when a student opens the problem '
                                      '(their saved draft, if any, takes priority).')

    class Meta:
        verbose_name = 'starter code'
        verbose_name_plural = 'starter code'

    def __str__(self):
        return f'Starter code for {self.problem.code}'
