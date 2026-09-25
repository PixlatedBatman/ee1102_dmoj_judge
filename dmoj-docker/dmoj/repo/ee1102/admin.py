from django.contrib import admin
from django.forms import ModelForm

from ee1102.models import ProblemStarter
from judge.admin.problem import ProblemAdmin
from judge.widgets import AdminAceWidget


class ProblemStarterForm(ModelForm):
    class Meta:
        widgets = {'code': AdminAceWidget(mode='python', height='250px')}


class ProblemStarterInline(admin.StackedInline):
    model = ProblemStarter
    form = ProblemStarterForm
    fields = ('code',)
    extra = 0
    max_num = 1
    can_delete = True


# Add a "Starter code" section to DMOJ's own problem edit page.
if ProblemStarterInline not in ProblemAdmin.inlines:
    ProblemAdmin.inlines = [*ProblemAdmin.inlines, ProblemStarterInline]
