from .models import *
from django.db.models import Q

# Get data from tables 
def get_all_users():
    return User.objects.all()

def get_user_matches(user_id):
    return Match.objects.filter(player_id=user_id)
def get_user_3_matches(user_id):
    return Match.objects.filter(Q(player_1_id=user_id) | Q(player_2_id=user_id)).order_by('-id')[:3]

def get_user_tournaments(user_id):
    user = User.objects.get(id=user_id)
    return list(user.tournaments.values_list('id', flat=True))
def get_user_3_tournaments(user_id):
    return Tournament.objects.filter(players__id=user_id).order_by("-start_date")[:3]

def get_tournaments():
    return Tournament.objects.all()

def get_tournament_data(tournament_id):
    tournament = Tournament.objects.get(tournament_id)
    return tournament

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
    matchid = Match.objects.get(match_id)
    total_seconds = int(matchid.match_time.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    match_time_str = f"{minutes}m {seconds}s"
    return match_time_str

# Manage friendships 
def add_friend(user_id, friend_id):
    user = User.objects.get(user_id)
    friend = User.objects.get(friend_id)
    if Friendship.objects.filter(user=user, friend=friend).exists():
        return f"Friendship request or connection already exists between {user.username} and {friend.username}."
    
    Friendship.objects.create(user=user, friend=friend, status='pending')
    return f"Friend request sent from {user.username} to {friend.username}."

def accept_friend(user_id, friend_id):
    user = User.objects.get(user_id)
    friend = User.objects.get(friend_id)
    try:
        friendship = Friendship.objects.get(user, friend, status='pending')
        friendship.status = 'approved'
        friendship.save()
        Friendship.objects.create(user, friend, status='approved')
        return f"{user.username} and {friend.username} are now friends!"
    except Friendship.DoesNotExist:
        return f"No pending friend request from {friend.username} to {user.username}."

def remove_friendship(user_id, friend_id):
    user = User.objects.get(user_id)
    friend = User.objects.get(friend_id)
    deleted_count = Friendship.objects.filter(
        Q(user, friend) | Q(user, friend)
    ).delete()
    if deleted_count[0] > 0:
        return f"Friendship or request between {user.username} and {friend.username} has been removed."
    return f"No friendship or request exists between {user.username} and {friend.username}."

def are_friends(user_id, friend_id):
    user = User.objects.get(user_id)
    friend = User.objects.get(friend_id)
    return Friendship.objects.filter(user, friend, status='approved').exists()

def get_friends(user_id):
    user = User.objects.get(user_id)
    friends = Friendship.objects.filter(user, status='approved').values_list('friend__username', flat=True)
    return list(friends)

def get_received_friend_requests(user_id):
    user = User.objects.get(user_id)
    requests = Friendship.objects.filter(user, status='pending')
    output = []
    for req in requests:
        output.append({
            "from": req.user.username,
            "sent_at": req.created_at,
        })
    return output

def get_sent_friend_requests(user_id):
    user = User.objects.get(user_id)
    requests = Friendship.objects.filter(user=user, status='pending')
    output = []
    for req in requests:
        output.append({
            "from": req.user.username,
            "sent_at": req.created_at,
        })
    return output

# Manage profile 
def change_name(req, user_id):
    user = User.objects.get(user_id)
    user.name = req.POST.get('name')
    user.save()

def change_picture(req, user_id):
    user = User.objects.get(user_id)
    user.avatar = req.POST.get()

def change_email(req, user_id):
    user = User.objects.get(user_id)

def delete_account(user_id):
    user = User.objects.get(user_id)
    user.delete()


#TODO set of functions to set data after a match and a tournament 