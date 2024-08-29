
from django.shortcuts import render
from django.views.generic.base import View
from django.views.generic import TemplateView
from chess_db.models import Game

def index(request):
    context = {'title': "Home Page"}
    return render(request, "../templates/chess/index.html", context)

class Games(TemplateView):
    template_name = "../templates/chess/games.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Recent Games"
        context["games"] = Game.objects.all()
        return context

def game_detail(request, game_id):
    game = Game.objects.get(id=game_id)
    context = {'game': game}
    return render(request, "../templates/chess/game_detail.html", context)

def play(request):
    return render(request, "../templates/chess/play.html")