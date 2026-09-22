from django.urls import include, path

from ee1102 import views

urlpatterns = [
    path('ta/', include([
        path('', views.dashboard, name='ee1102_dashboard'),
        path('data/', views.dashboard_data, name='ee1102_dashboard_data'),
        path('export/<str:contest>.xlsx', views.export_xlsx, name='ee1102_export_xlsx'),
    ])),
    path('', include('dmoj.urls')),
]

handler403 = 'judge.views.error.error403'
handler404 = 'judge.views.error.error404'
handler500 = 'judge.views.error.error500'
