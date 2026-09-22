"""Post-session Excel export: summary, per-student, per-problem, per-test-case and raw submissions."""
from collections import Counter, defaultdict
from io import BytesIO

from django.utils import timezone
from django.utils.dateparse import parse_datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from ee1102.stats import VERDICTS, compute, contest_submissions
from judge.models import SubmissionTestCase

BOLD = Font(bold=True)
HEAD = PatternFill('solid', fgColor='DDE4EE')


def _local(dt):
    return timezone.localtime(dt).replace(tzinfo=None) if dt else None


def _iso_local(s):
    return _local(parse_datetime(s)) if s else None


def _sheet(wb, title, header, rows, widths=None):
    ws = wb.create_sheet(title)
    ws.append(header)
    for c in ws[1]:
        c.font, c.fill = BOLD, HEAD
    for r in rows:
        ws.append(r)
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    for i, h in enumerate(header, 1):
        ws.column_dimensions[get_column_letter(i)].width = (widths or {}).get(h, max(10, min(40, len(str(h)) + 2)))
    return ws


def build_workbook(contest):
    data = compute(contest)
    codes = [p['code'] for p in data['problems']]
    wb = Workbook()
    wb.remove(wb.active)

    s, c = data['summary'], data['contest']
    _sheet(wb, 'Summary', ['Field', 'Value'], [
        ['Contest', f"{c['name']} ({c['key']})"],
        ['Start', _local(contest.start_time)], ['End', _local(contest.end_time)],
        ['Exported at', _local(timezone.now())],
        ['Max score', c['max_score']],
        ['Students on roster', s['students']], ['Students who joined', s['joined']],
        ['Students who submitted', s['submitted']], ['Total submissions', s['submissions']],
        ['Accepted submissions', s['ac']],
        ['Average score', round(sum(r['total'] for r in data['students']) / len(data['students']), 3)
         if data['students'] else 0],
    ], widths={'Field': 26, 'Value': 40})

    header = ['Username', 'Name', 'Joined', 'Total score', 'Problems solved', 'Total attempts', 'Last submission']
    for code in codes:
        header += [f'{code} score', f'{code} tests passed', f'{code} attempts', f'{code} solved (min)']
    rows = []
    for r in sorted(data['students'], key=lambda r: (-r['total'], r['username'])):
        row = [r['username'], r['name'], 'yes' if r['joined'] else 'no', r['total'], r['solved'], r['attempts'],
               _iso_local(r['last'])]
        for code in codes:
            p = r['problems'][code]
            row += ([p['best'], f"{p['passed']:g}/{p['cases']:g}", p['attempts'], p['first_ac_min']] if p
                    else [0, '', 0, None])
        rows.append(row)
    _sheet(wb, 'Students', header, rows, widths={'Username': 18, 'Name': 24, 'Last submission': 20})

    _sheet(wb, 'Problems',
           ['Code', 'Name', 'Points', 'Students attempted', 'Students solved', 'Submissions', 'AC rate %',
            'Avg attempts to solve', 'Avg score (all students)'] + VERDICTS,
           [[p['code'], p['name'], p['points'], p['attempted'], p['solved'], p['submissions'], p['ac_rate'],
             p['avg_attempts_to_solve'], p['avg_score']] + [p['verdicts'].get(v, 0) for v in VERDICTS]
            for p in data['problems']], widths={'Name': 30})

    subs = list(contest_submissions(contest).select_related('source'))
    by_id = {x.id: x for x in subs}
    case_stats = defaultdict(Counter)
    for tc in SubmissionTestCase.objects.filter(submission_id__in=by_id.keys()).only('submission_id', 'case',
                                                                                     'status'):
        case_stats[(by_id[tc.submission_id].problem.code, tc.case)][tc.status] += 1
    _sheet(wb, 'Test cases', ['Problem', 'Case #', 'Runs', 'Passed', 'Pass %'] + VERDICTS[1:],
           [[code, case, sum(cnt.values()), cnt['AC'], round(100 * cnt['AC'] / sum(cnt.values()), 1)] +
            [cnt.get(v, 0) for v in VERDICTS[1:]]
            for (code, case), cnt in sorted(case_stats.items())])

    _sheet(wb, 'Submissions',
           ['ID', 'Time', 'Username', 'Problem', 'Language', 'Status', 'Result', 'Points', 'Tests passed',
            'Tests total', 'Exec time (s)', 'Memory (KB)', 'Source'],
           [[x.id, _local(x.date), x.user.user.username, x.problem.code, x.language.key, x.status, x.result,
             getattr(getattr(x, 'contest', None), 'points', 0.0), x.case_points, x.case_total, x.time, x.memory,
             getattr(getattr(x, 'source', None), 'source', '')]
            for x in subs], widths={'Time': 20, 'Username': 18, 'Source': 80})

    buf = BytesIO()
    wb.save(buf)
    return buf.getvalue()
