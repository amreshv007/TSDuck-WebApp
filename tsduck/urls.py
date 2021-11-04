from django.urls import path
from . import views

urlpatterns = [
    path('', views.ts_index, name='credential_input'),
    path('analyze', views.authenticate, name='stream_analysis'),
    path('analyze/result', views.cmd_result, name='cmd_result'),
    path('analyze/tstables-result', views.stream_edit, name='stream_edit'),
    path('analyze/delete-streams', views.delete_stream, name='delete_stream'),
    path('analyze/upload', views.upload_stream, name='upload_stream'),
    path('logout', views.session_close, name='session_close'),
]