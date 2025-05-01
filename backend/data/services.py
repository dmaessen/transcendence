from .models import *
from django.db.models import Q
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

# Get data from tables 
def get_all_users():
    return CustomUser.objects.all()

def get_user_matches(user_id):
    return Match.objects.filter(player_id=user_id)
def get_user_3_matches(user_id):
    return Match.objects.filter(Q(player_1_id=user_id) | Q(player_2_id=user_id)).order_by('-id')[:3]

def get_user_tournaments(user_id):
    user = CustomUser.objects.get(id=user_id)
    return list(user.tournaments.values_list('id', flat=True))
def get_user_3_tournaments(user_id):
    user = CustomUser.objects.get(id=user_id)
    tournaments = user.tournaments.all().order_by('-start_date')[:3]
    logging.info(f"!!!!!! services: {tournaments}")
    return tournaments

def get_tournaments():
    return Tournament.objects.all()

def get_tournament_data(tournament_id):
    tournament = Tournament.objects.get(id=tournament_id)
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
    matchid = Match.objects.get(id=match_id)
    total_seconds = int(matchid.match_time.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    match_time_str = f"{minutes}m {seconds}s"
    return match_time_str

# Manage friendships 
def add_new_friend(user_id, friend_id):
    user = CustomUser.objects.filter(id=user_id).first()
    friend = CustomUser.objects.filter(id=friend_id).first()
    friendship = get_frienship(user_id, friend_id)
    if friendship and friendship.status == "pending":
        accept_friend(user_id, friend_id)
        return f"Friendship request or connection already exists between {user.username} and {friend.username}."
    
    Friendship.objects.create(sender=user, receiver=friend, status='pending')
    return f"Friend request sent from {user.username} to {friend.username}."

def accept_friend(friendship_id):
    friendship = Friendship.objects.get(id=friendship_id)
    friendship.status = 'approved'
    friendship.save()
    return f"Friendship is a success!"

def cancel_friend(friendship_id):
    friendship_id = Friendship.objects.get(id=friendship_id).delete()
    return f"request canceled"

def remove_friend(user_id, friend_id):
    user = CustomUser.objects.get(id=user_id)
    friend = CustomUser.objects.get(id=friend_id)
    Friendship.objects.filter(
        models.Q(sender=user, receiver=friend) | 
        models.Q(sender=friend, receiver=user)
    ).delete()
    return f"No longer friends."

def get_frienship(user_id, friend_id):
    user = CustomUser.objects.get(id=user_id)
    friend = CustomUser.objects.get(id=friend_id)
    friendship = Friendship.objects.filter(
        models.Q(sender=user, receiver=friend) | 
        models.Q(sender=friend, receiver=user)
    ).first()
    if friendship:
        return friendship
    else:
        return None 

def get_friends(user_id):
    user = CustomUser.objects.get(id=user_id)
    friendships = Friendship.objects.filter((Q(sender=user) | Q(receiver=user)), status='approved')
    friends = []
    for friend in friendships:
        if(user == friend.sender):
            status = cache.get(f"user_online_{friend.receiver.id}", False)
            friends.append({
                "friend": friend.receiver.username,
                "friend_id": friend.receiver.id,
                "is_online": status,
            })
        else:
            status = cache.get(f"user_online_{friend.sender.id}", False)
            friends.append({
                "friend": friend.sender.username,
                "friend_id": friend.sender.id,
                "is_online": status,
            })
    return list(friends)

def get_friendship_requests(user_id):
    user = CustomUser.objects.get(id=user_id)
    requests = Friendship.objects.filter((Q(sender=user) | Q(receiver=user)), status='pending')
    fRequests = []
    for req in requests:
        fRequests.append({
            "user_id": user.id,
            "receiver": req.receiver.username,
            "receiver_id": req.receiver.id,
            "sender": req.sender.username,
            "sender_id": req.sender.id,
            "friendship_id": req.id
        })
    return fRequests

# Manage profile 
def change_name(req, user_id):
    user = CustomUser.objects.get(user_id)
    user.name = req.POST.get('name')
    user.save()

def change_picture(req, user_id):
    user = CustomUser.objects.get(user_id)
    user.avatar = req.POST.get()

def change_email(req, user_id):
    user = CustomUser.objects.get(user_id)

def delete_account(user_id):
    user = CustomUser.objects.get(user_id)
    user.delete()


#TODO set of functions to set data after a match and a tournament 