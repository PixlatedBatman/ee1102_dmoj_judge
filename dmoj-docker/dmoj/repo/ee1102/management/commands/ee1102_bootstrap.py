"""Idempotent one-time setup: judges, Python 3 only, navbar, and a test problem + contest."""
import io
import os
import zipfile
from datetime import timedelta

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from judge.models import (Contest, ContestProblem, Judge, Language, NavigationBar, Problem, ProblemData, ProblemGroup,
                          ProblemTestCase, ProblemType)
from judge.utils.problem_data import ProblemDataCompiler

JUDGES = ('judge1', 'judge2')
NAVBAR = [('problems', 'Problems', '/problems/', r'^/problem'), ('contest', 'Contests', '/contests/', r'^/contest'),
          ('submit', 'My submissions', '/submissions/', r'^/submi|^/src/')]

TEST_DESCRIPTION = """Read two integers $a$ and $b$ on one line and print their sum.

## Input Format
One line with two space-separated integers $a$ and $b$ ($-10^9 \\le a, b \\le 10^9$).

## Output Format
A single integer, $a + b$.

## Sample Input 1
```
1 2
```

## Sample Output 1
```
3
```

## Sample Input 2
```
-5 12
```

## Sample Output 2
```
7
```
"""

# (input, output); the first two are the visible samples above, the rest are hidden.
TEST_CASES = [('1 2', '3'), ('-5 12', '7'), ('1000000000 1000000000', '2000000000'), ('0 0', '0'),
              ('-999999999 -1', '-1000000000')]


class Command(BaseCommand):
    help = 'Set up judges, Python-3-only language, navbar, and a test problem/contest (safe to re-run).'

    def handle(self, *args, **options):
        self.languages()
        self.judges()
        self.navbar()
        self.test_problem()
        self.stdout.write(self.style.SUCCESS('EE1102 bootstrap complete.'))

    def languages(self):
        if not Language.objects.filter(key='PY3').exists():
            call_command('loaddata', 'language_small', verbosity=0)
        Language.objects.exclude(key='PY3').filter(submission__isnull=True).delete()
        self.stdout.write('Languages: ' + ', '.join(Language.objects.values_list('key', flat=True)))

    def judges(self):
        key = os.environ['JUDGE_KEY']
        for name in JUDGES:
            judge, _ = Judge.objects.get_or_create(name=name, defaults={'auth_key': key})
            if judge.auth_key != key:
                judge.auth_key = key
                judge.save(update_fields=['auth_key'])
        self.stdout.write('Judges registered: ' + ', '.join(JUDGES))

    def navbar(self):
        NavigationBar.objects.all().delete()
        for order, (key, label, path, regex) in enumerate(NAVBAR, 1):
            NavigationBar.objects.create(key=key, label=label, path=path, regex=regex, order=order, parent=None)

    def test_problem(self):
        group, _ = ProblemGroup.objects.get_or_create(name='ee1102', defaults={'full_name': 'EE1102'})
        ptype, _ = ProblemType.objects.get_or_create(name='ee1102', defaults={'full_name': 'EE1102'})
        problem, created = Problem.objects.get_or_create(code='aplusb', defaults=dict(
            name='A Plus B (test)', description=TEST_DESCRIPTION, group=group, time_limit=2, memory_limit=262144,
            points=10, partial=True, is_public=False))
        problem.types.add(ptype)
        problem.allowed_languages.set(Language.objects.filter(key='PY3'))

        if created or not problem.cases.exists():
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, 'w') as zf:
                for i, (inp, out) in enumerate(TEST_CASES, 1):
                    zf.writestr(f'{i}.in', inp + '\n')
                    zf.writestr(f'{i}.out', out + '\n')
            data, _ = ProblemData.objects.get_or_create(problem=problem)
            data.zipfile.save('aplusb.zip', ContentFile(buf.getvalue()), save=False)
            data.checker = 'standard'
            data.save()
            problem.cases.all().delete()
            for i in range(1, len(TEST_CASES) + 1):
                ProblemTestCase.objects.create(dataset=problem, order=i, type='C', input_file=f'{i}.in',
                                               output_file=f'{i}.out', points=1, is_pretest=False)
            files = sorted(zipfile.ZipFile(io.BytesIO(buf.getvalue())).namelist())
            ProblemDataCompiler.generate(problem, data, problem.cases.order_by('order'), files)
            self.stdout.write(f'Problem "aplusb" test data generated ({len(TEST_CASES)} cases). {data.feedback}')

        now = timezone.now()
        contest, created = Contest.objects.get_or_create(key='test', defaults=dict(
            name='Test Contest', description='Setup check. Solve A Plus B.', start_time=now - timedelta(minutes=5),
            end_time=now + timedelta(days=7), is_visible=True, scoreboard_visibility=Contest.SCOREBOARD_HIDDEN,
            format_name='default', is_rated=False))
        if created:
            ContestProblem.objects.create(contest=contest, problem=problem, points=10, partial=True, order=1)
        self.stdout.write('Contest "test" ready.')
