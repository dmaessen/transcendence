from .models import CustomUser, Match, Tournament
from django.db.models import Q

def get_all_users():
    return CustomUser.objects.all()

def get_user_matches(user_id):
    return Match.objects.filter(player_id=user_id)

def get_user_tournaments(user_id):
    return ", ".join(str(t.id) for t in user_id.tournaments.all())

def get_win_cout(user_id):
    wins = Match.objects.filter(id=user_id)
    win_count = wins.count()
    return win_count

def get_matches_count(user_id):
    matches = Match.objects.filter(Q(player_1=user_id) | Q(player_2=user_id))
    matches_count = matches.count()
    return matches_count

def get_score(user_id):
    win_count = get_win_cout(user_id)
    matches_count = get_matches_count(user_id)
    if matches_count != 0 :
        score = win_count / matches_count
    else:
        score = 0
    return score
    
def get_match_time(match_id):
    total_seconds = int(match_id.match_time.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    match_time_str = f"{minutes}m {seconds}s"
    return match_time_str