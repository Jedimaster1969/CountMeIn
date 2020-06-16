from django.urls import path, re_path
from . import views
from .views import DetailViewAsset, CreateViewAsset,UpdateViewAsset,DeleteViewAsset,DetailViewAssetMember, DeleteViewMember

urlpatterns = [
	path('asset/<int:asset_id>/', views.asset_detail, name='asset_detail'),
	path('asset/<int:asset_id>/edit/', views.asset_detail_edit, name='asset_detail_edit'),
	path('asset/members/<int:asset_id>/', views.member_detail, name='member_detail'),
	path('asset/members/<int:asset_id>/<int:member_id>/', views.member_detail, name='member_detail'),
	path('asset/members/<int:asset_id>/<str:activated>/', views.member_detail, name='member_detail'),
	path('asset/members/<int:asset_id>/<int:member_id>/edit', views.member_detail_edit, name='member_detail_edit'),
	path('asset/members/<int:asset_id>/<int:member_id>/delete/', views.delete_a_member, name='member_delete'),
	path('asset/add/', CreateViewAsset.as_view(), name='add_event'),
	path('asset/update/<int:pk>', UpdateViewAsset.as_view(), name='asset_update'),
	path('asset/exception/<int:asset_id>/', views.asset_exception_detail, name='asset_exception_detail'),
	re_path(r'^invite/(?P<invite_code>\d+)/$', views.asset_invite, name="asset_invite"),
]

