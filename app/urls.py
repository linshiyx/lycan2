#coding=utf-8
from django.conf.urls import patterns, include, url
from app import views

urlpatterns = [
    url(r'^$',  views.index),
    url(r'^login/$', views.login_ajax),
    url(r'^register/$', views.register_ajax),
    url(r'^create_room/$', views.create_room),
    url(r'^join_room/$', views.join_room),
    url(r'^ready/$', views.ready),
    url(r'^confirm_roll/$', views.confirm_roll),
    url(r'^confirm_valentine/$', views.confirm_valentine),
    url(r'^confirm_guarded/$', views.confirm_guarded),
    url(r'^request_seen/$', views.request_seen),
    url(r'^confirm_seen/$', views.confirm_seen),
    url(r'^confirm_dead/$', views.confirm_dead),
    url(r'^confirm_witch/$', views.confirm_witch),
    url(r'^confirm_hunted/$', views.confirm_hunted),
    url(r'^finish_talk/$', views.finish_talk),
    url(r'^vote_badge/$', views.vote_badge),
    url(r'^hand_badge/$', views.hand_badge),
    url(r'^vote_dead/$', views.vote_dead),
]
