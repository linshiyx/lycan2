#coding=utf-8
from channels.routing import route
from app import consumers
from app.views import login
from channels.staticfiles import StaticFilesConsumer

channel_routing = {
    # This makes Django serve static files from settings.STATIC_URL, similar
    # to django.views.static.serve. This isn't ideal (not exactly production
    # quality) but it works for a minimal example.
    'http.request': StaticFilesConsumer(),

    # Wire up websocket channels to our consumers:
    'websocket.connect': consumers.ws_connect,
    'websocket.receive': consumers.ws_message,
    'websocket.disconnect': consumers.ws_disconnect,

    'new_round': consumers.new_round,
    'cupid_start': consumers.cupid_start,
    'guard_start': consumers.guard_start,
    'seer_start': consumers.seer_start,
    'lycan_start': consumers.lycan_start,
    'witch_start': consumers.witch_start,
    'day_start': consumers.day_start,
    'vote_badge': consumers.vote_badge,
    'deliver_dead': consumers.deliver_dead,
    'hunter_start': consumers.hunter_start,
    'hand_badge': consumers.hand_badge,
    'free_talk':consumers.free_talk,
    'vote_dead': consumers.vote_dead,
}