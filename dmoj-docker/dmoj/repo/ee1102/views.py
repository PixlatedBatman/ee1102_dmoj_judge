import os

from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone

from ee1102.export import build_workbook
from ee1102.stats import compute, default_contest
from judge.models import Contest, Judge

with open(os.path.join(os.path.dirname(__file__), 'dashboard.html'), encoding='utf-8') as f:
    DASHBOARD_HTML = f.read()


@staff_member_required
def dashboard(request):
    return HttpResponse(DASHBOARD_HTML)


@staff_member_required
def dashboard_data(request):
    contests = list(Contest.objects.order_by('-start_time').values('key', 'name'))
    key = request.GET.get('contest')
    contest = get_object_or_404(Contest, key=key) if key else default_contest()
    judges = [{'name': j.name, 'online': j.online, 'ping': j.ping, 'load': j.load}
              for j in Judge.objects.order_by('name')]
    return JsonResponse({'contests': contests, 'judges': judges, 'data': compute(contest) if contest else None})


@staff_member_required
def export_xlsx(request, contest):
    contest = get_object_or_404(Contest, key=contest)
    stamp = timezone.localtime().strftime('%Y%m%d-%H%M')
    response = HttpResponse(build_workbook(contest),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{contest.key}-stats-{stamp}.xlsx"'
    return response
