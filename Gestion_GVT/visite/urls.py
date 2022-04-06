#from django.conf.urls import urls
from django.urls import path
from visite import views

from django.conf.urls.static import static
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    # path('', views.ProprietaireListView.as_view(), name='list'),
    #path('testAdd', views.add_test_v, name='add_test_v'),
    path('all_visite/', views.all_visite, name='all_visite'),
    path('all_visite/<int:id>/', views.get_one_visite, name='get_one_visite'),
    path('add_visite/', views.add_visite, name='add_visite'),
    path('', views.index, name='visite'),
    path('add', views.add, name='add'),
    path('modifier/<int:id>', views.modifier, name='modifier'),
    path('supprimer/<int:id>', views.supprimer, name='supprimer'),
    path('search-visite', csrf_exempt(views.search_visite), name="search-visite"),
    path('redevances', views.redevances, name='Redevances'),
    path('CA', views.CA, name='CA'),
    path('VT', views.VT, name='VT'),
    path('VH', views.VH, name='VH'),
    path('export_xls', views.export_users_xls, name='export_xls'),
    # path('facture/<int:id>', views.facture, name='facture'),
    path('facture/<int:id>', views.render_pdf_view, name='facture'),
]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
