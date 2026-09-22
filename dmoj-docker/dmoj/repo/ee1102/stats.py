"""Contest statistics shared by the live TA dashboard and the post-session export."""
from collections import Counter, defaultdict
from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from judge.models import Contest, ContestParticipation, ContestProblem, Submission

VERDICTS = ['AC', 'WA', 'TLE', 'MLE', 'OLE', 'IR', 'RTE', 'CE', 'IE', 'AB']
PENDING = ('QU', 'P', 'G')


def students():
    """All active non-staff accounts, i.e. the class roster."""
    return User.objects.filter(is_active=True, is_staff=False, is_superuser=False).select_related('profile') \
        .order_by('username')


def contest_problems(contest):
    return list(ContestProblem.objects.filter(contest=contest).select_related('problem').order_by('order'))


def contest_submissions(contest):
    """Every submission made to the contest by a student, oldest first."""
    return (Submission.objects.filter(contest_object=contest, user__user__is_staff=False)
            .select_related('user__user', 'problem', 'language', 'contest')
            .order_by('id'))


def compute(contest):
    now = timezone.now()
    problems = contest_problems(contest)
    roster = list(students())
    participations = {p.user_id: p for p in ContestParticipation.objects
                      .filter(contest=contest, virtual=ContestParticipation.LIVE)}
    subs = list(contest_submissions(contest))

    # cell[(profile_id, problem_id)] -> aggregate for that student on that problem
    cell = defaultdict(lambda: {'attempts': 0, 'best': 0.0, 'first_ac': None, 'passed': 0, 'cases': 0,
                                'last': None})
    per_problem = {cp.problem_id: {'verdicts': Counter(), 'submissions': 0, 'pending': 0} for cp in problems}
    last_seen = {}
    timeline = Counter()
    recent = []

    for s in subs:
        key = (s.user_id, s.problem_id)
        c = cell[key]
        c['attempts'] += 1
        c['last'] = s.date
        cs = getattr(s, 'contest', None)
        pts = cs.points if cs is not None else 0.0
        if pts > c['best'] or (pts == c['best'] and s.case_points > c['passed']):
            c['best'] = pts
            c['passed'] = s.case_points
            c['cases'] = s.case_total
        if c['cases'] == 0:
            c['cases'] = s.case_total
        if s.result == 'AC' and c['first_ac'] is None:
            c['first_ac'] = s.date
        pp = per_problem.get(s.problem_id)
        if pp is not None:
            pp['submissions'] += 1
            if s.status in PENDING:
                pp['pending'] += 1
            elif s.result:
                pp['verdicts'][s.result] += 1
        last_seen[s.user_id] = s.date
        timeline[s.date.replace(second=0, microsecond=0) - timedelta(minutes=s.date.minute % 5)] += 1

    for s in subs[-25:][::-1]:
        recent.append({
            'id': s.id, 'user': s.user.user.username, 'problem': s.problem.code, 'result': s.result or s.status,
            'status': s.status, 'passed': s.case_points, 'cases': s.case_total, 'date': s.date.isoformat(),
            'points': getattr(getattr(s, 'contest', None), 'points', 0.0),
        })

    start = contest.start_time
    student_rows = []
    for u in roster:
        pid = u.profile.id
        part = participations.get(pid)
        row = {'username': u.username, 'name': u.get_full_name() or u.profile.username_display_override,
               'joined': part is not None, 'total': 0.0, 'solved': 0, 'attempts': 0,
               'last': last_seen[pid].isoformat() if pid in last_seen else None, 'problems': {}}
        for cp in problems:
            c = cell.get((pid, cp.problem_id))
            if c is None:
                row['problems'][cp.problem.code] = None
                continue
            row['problems'][cp.problem.code] = {
                'best': round(c['best'], 3), 'attempts': c['attempts'], 'passed': c['passed'], 'cases': c['cases'],
                'solved': c['first_ac'] is not None,
                'first_ac': c['first_ac'].isoformat() if c['first_ac'] else None,
                'first_ac_min': round((c['first_ac'] - start).total_seconds() / 60, 1) if c['first_ac'] else None,
            }
            row['total'] += c['best']
            row['attempts'] += c['attempts']
            row['solved'] += c['first_ac'] is not None
        row['total'] = round(row['total'], 3)
        student_rows.append(row)

    problem_rows = []
    for cp in problems:
        code = cp.problem.code
        cells = [r['problems'][code] for r in student_rows if r['problems'][code]]
        solved = [c for c in cells if c['solved']]
        pp = per_problem[cp.problem_id]
        judged = sum(pp['verdicts'].values())
        problem_rows.append({
            'code': code, 'name': cp.problem.name, 'points': cp.points,
            'attempted': len(cells), 'solved': len(solved), 'submissions': pp['submissions'],
            'pending': pp['pending'],
            'ac_rate': round(100 * pp['verdicts']['AC'] / judged, 1) if judged else None,
            'avg_attempts_to_solve': round(sum(c['attempts'] for c in solved) / len(solved), 2) if solved else None,
            'avg_score': round(sum(c['best'] for c in cells) / len(student_rows), 3) if student_rows else 0,
            'verdicts': {v: pp['verdicts'][v] for v in VERDICTS if pp['verdicts'][v]},
        })

    active_cutoff = now - timedelta(minutes=5)
    return {
        'contest': {'key': contest.key, 'name': contest.name, 'start': contest.start_time.isoformat(),
                    'end': contest.end_time.isoformat(), 'max_score': sum(cp.points for cp in problems)},
        'generated': now.isoformat(),
        'summary': {
            'students': len(roster),
            'joined': sum(r['joined'] for r in student_rows),
            'submitted': len(last_seen),
            'active_5min': sum(1 for d in last_seen.values() if d >= active_cutoff),
            'submissions': len(subs),
            'pending': sum(p['pending'] for p in per_problem.values()),
            'ac': sum(p['verdicts']['AC'] for p in per_problem.values()),
        },
        'problems': problem_rows,
        'students': student_rows,
        'recent': recent,
        'timeline': sorted(((k.isoformat(), v) for k, v in timeline.items())),
    }


def default_contest():
    """Contest currently running, else the most recently started one."""
    now = timezone.now()
    return (Contest.objects.filter(start_time__lte=now, end_time__gte=now).order_by('-start_time').first() or
            Contest.objects.order_by('-start_time').first())

