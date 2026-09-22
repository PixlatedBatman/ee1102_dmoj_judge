import os

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from ee1102.export import build_workbook
from judge.models import Contest


class Command(BaseCommand):
    help = 'Export contest stats to exports/<contest>-stats-<time>.xlsx'

    def add_arguments(self, parser):
        parser.add_argument('contest', help='contest key')

    def handle(self, contest, **options):
        try:
            c = Contest.objects.get(key=contest)
        except Contest.DoesNotExist:
            raise CommandError(f'No contest with key {contest!r}. Keys: ' +
                               ', '.join(Contest.objects.values_list('key', flat=True)))
        os.makedirs('exports', exist_ok=True)
        path = os.path.join('exports', f"{c.key}-stats-{timezone.localtime().strftime('%Y%m%d-%H%M')}.xlsx")
        with open(path, 'wb') as f:
            f.write(build_workbook(c))
        self.stdout.write(self.style.SUCCESS(f'Wrote dmoj-docker/dmoj/repo/{path}'))
