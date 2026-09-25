"""Bulk-create student accounts <prefix><NNN>, e.g. ee26b001..ee26b160 (safe to re-run)."""
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from judge.models import Language, Profile


class Command(BaseCommand):
    help = 'Create student accounts <prefix><number>, with the password equal to the username.'

    def add_arguments(self, parser):
        parser.add_argument('--prefix', default='ee26b')
        parser.add_argument('--start', type=int, default=1)
        parser.add_argument('--end', type=int, default=160, help='inclusive')
        parser.add_argument('--digits', type=int, default=3)
        parser.add_argument('--reset-passwords', action='store_true',
                            help='also reset existing accounts in the range back to password = username')

    @transaction.atomic
    def handle(self, prefix, start, end, digits, reset_passwords, **options):
        py3 = Language.objects.get(key='PY3')
        created = reset = skipped = 0
        for n in range(start, end + 1):
            username = f'{prefix}{n:0{digits}d}'
            user, is_new = User.objects.get_or_create(username=username)
            if is_new or reset_passwords:
                user.set_password(username)
                user.is_active = True
                user.save()
                created += is_new
                reset += not is_new
            else:
                skipped += 1
            Profile.objects.get_or_create(user=user, defaults={'language': py3})
        first, last = f'{prefix}{start:0{digits}d}', f'{prefix}{end:0{digits}d}'
        self.stdout.write(self.style.SUCCESS(
            f'{first}..{last}: {created} created, {reset} passwords reset, {skipped} already existed (unchanged).'))
