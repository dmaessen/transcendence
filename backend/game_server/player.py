class Player :
    STATUS = ['online', 'in game', 'offline'] #need to ping the player in backend after x amount of time to see if online
    def __init__(self, user_id, session_key, status):
        self.user_id = user_id
        self.session_key = session_key
        self.status = status
