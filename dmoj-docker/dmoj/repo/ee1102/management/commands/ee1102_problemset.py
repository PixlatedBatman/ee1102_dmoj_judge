"""Load a function-style problem set (ee1102/problemsets/<name>.py) into the site, judges and a contest."""
import copy
import importlib
import io
import json
import os
import shutil
import zipfile

import yaml
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand, CommandError

from ee1102.models import ProblemStarter
from ee1102.problemsets.harness import checker_source, grader_source
from judge.models import Contest, ContestProblem, Language, Problem, ProblemGroup, ProblemType


def build_description(p, judging_note):
    examples = '\n'.join(line for _, _, line in p['examples'])
    return (f"{p['description']}\n\n## Examples\n```python\n{examples}\n```\n\n"
            f"## Hint\n{p['hint']}\n\n{judging_note}\n")


class Command(BaseCommand):
    help = 'Create/update the problems of a problem set and add them, in order, to a contest (safe to re-run).'

    def add_arguments(self, parser):
        parser.add_argument('problemset', help='module name in ee1102/problemsets, e.g. tasession')
        parser.add_argument('--contest', default='tasession', help='contest key to add the problems to')
        parser.add_argument('--points', type=int, default=10, help='contest points per problem')

    def handle(self, problemset, contest, points, **options):
        spec = importlib.import_module(f'ee1102.problemsets.{problemset}')
        try:
            contest = Contest.objects.get(key=contest)
        except Contest.DoesNotExist:
            raise CommandError(f'No contest {contest!r}')
        group, _ = ProblemGroup.objects.get_or_create(name='ee1102', defaults={'full_name': 'EE1102'})
        ptype, _ = ProblemType.objects.get_or_create(name='ee1102', defaults={'full_name': 'EE1102'})
        py3 = Language.objects.filter(key='PY3')

        for order, p in enumerate(spec.PROBLEMS, 1):
            cases = self.build_cases(p)
            self.write_judge_files(p, cases)

            problem, created = Problem.objects.update_or_create(code=p['code'], defaults=dict(
                name=p['name'], description=build_description(p, spec.JUDGING_NOTE), group=group,
                time_limit=2, memory_limit=262144, points=points, partial=True, is_public=False))
            problem.types.set([ptype])
            problem.allowed_languages.set(py3)
            ProblemStarter.objects.update_or_create(problem=problem, defaults={'code': p['starter']})
            ContestProblem.objects.update_or_create(contest=contest, problem=problem, defaults=dict(
                points=points, partial=True, order=order))
            self.stdout.write(f"{order}. {p['code']:<14} {p['name']:<26} {'created' if created else 'updated'}, "
                              f"{len(p['examples'])} visible + {len(p['hidden'])} hidden tests")

        cache.clear()
        self.stdout.write(self.style.SUCCESS(f'Problem set {problemset!r} loaded into contest {contest.key!r}.'))

    def build_cases(self, p):
        namespace = {}
        exec(p['solution'], namespace)
        fn = namespace[p['function']]
        for args, expected, line in p['examples']:
            got = fn(*copy.deepcopy(args))
            if got != expected:
                raise CommandError(f"{p['code']}: reference solution gives {got!r} for slide example "
                                   f"`{line.split('#')[0].strip()}`, slide says {expected!r}")
        cases = []
        for args in [a for a, _, _ in p['examples']] + p['hidden']:
            before = copy.deepcopy(args)
            result = fn(*copy.deepcopy(args))
            assert json.loads(json.dumps(list(args))) == list(before), f"{p['code']}: args not JSON round-trippable"
            cases.append((json.dumps(list(args)) + '\n', repr(result) + '\n'))
        return cases

    def write_judge_files(self, p, cases):
        root = os.path.join(settings.DMOJ_PROBLEM_DATA_ROOT, p['code'])
        if os.path.isdir(root):
            shutil.rmtree(root)
        os.makedirs(root)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, (inp, out) in enumerate(cases, 1):
                zf.writestr(f'{i}.in', inp)
                zf.writestr(f'{i}.out', out)
        with open(os.path.join(root, 'tests.zip'), 'wb') as f:
            f.write(buf.getvalue())
        with open(os.path.join(root, 'grader.py'), 'w') as f:
            f.write(grader_source(p['function'], p.get('must_be_new', False)))
        with open(os.path.join(root, 'checker.py'), 'w') as f:
            f.write(checker_source(p['function']))
        init = {
            'archive': 'tests.zip', 'custom_judge': 'grader.py', 'checker': 'checker.py',
            'test_cases': [{'in': f'{i}.in', 'out': f'{i}.out', 'points': 1} for i in range(1, len(cases) + 1)],
        }
        # Written last: the judges pick the problem up when init.yml appears.
        with open(os.path.join(root, 'init.yml'), 'w') as f:
            yaml.safe_dump(init, f, sort_keys=False)
