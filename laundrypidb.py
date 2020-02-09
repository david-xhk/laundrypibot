import pyrebase
import time


config = {
    "apiKey": "AIzaSyB95vJSTpj4uhlN3eoyagKDKUJIRvjGF-Y",
    "authDomain": "laundry-pi-bot.firebaseapp.com",
    "databaseURL": "https://laundry-pi-bot.firebaseio.com",
    "projectId": "laundry-pi-bot",
    "storageBucket": "laundry-pi-bot.appspot.com",
    "messagingSenderId": "465812216734"
}


db = pyrebase.initialize_app(config).database()


def get_chat_id(phone_num):
    return db.child("contacts", phone_num[-8:]).get().val()


def set_chat_id(phone_num, chat_id):
    db.child("contacts", phone_num[-8:]).set(chat_id)


def get_current_timestamp():
    return int(round(time.time()))


def get_last_timestamp(washer_id):
    return max(db.child("washers", washer_id).get().val().keys())


def clear_timestamps(washer_id):
    db.child("washers", washer_id).set([])


def get_washers():
    return db.child("washers").get().each()


def is_valid_washer(washer_id):
    if washer_id == "0":
        return False
    
    for washer in get_washers():
        if washer_id == str(washer.key()):
            return True
    
    return False
    

def get_washer_state(washer_id, timestamp=None):
    if timestamp is None:
        timestamp = get_last_timestamp(washer_id)
    
    return db.child("washers", washer_id, timestamp, "state").get().val()


def set_washer_state(washer_id, state, timestamp=None):
    if timestamp is None:
        timestamp = get_current_timestamp()  
    
    db.child("washers", washer_id, timestamp, "state").set(state)


def check_washers():
    overview = []
    
    for washer in get_washers():
        washer_id = washer.key()
        
        if washer_id == 0:
            continue
        
        last_timestamp = max(washer.val())
        state = washer.val()[last_timestamp]["state"]
        
        if state == "faulty":
            status = "Washer {} has been reported as faulty.".format(washer_id)
        
        elif state == "idle":
            status = "Washer {} is not in use.".format(washer_id)
        
        elif state == "running":
            status = "Washer {} has been running for {} minutes.".format(
                    washer_id, (get_current_timestamp()-int(last_timestamp))//60)
        else:
            status = "Washer {} is in an unknown state.".format(washer_id)
        
        overview.append(status)
    
    return "\n".join(overview)


def get_waitlist(washer_id, timestamp=None):
    if timestamp is None:
        timestamp = get_last_timestamp(washer_id)
    
    waitlist = db.child("washers", washer_id, timestamp, "waitlist").get().val()
    
    if not waitlist:
        waitlist = []
    
    return waitlist


def set_waitlist(washer_id, waitlist, timestamp=None):
    if timestamp is None:
        timestamp = get_last_timestamp(washer_id)
    
    db.child("washers", washer_id, timestamp, "waitlist").set(waitlist)


def update_waitlist(washer_id, chat_id):
    if not washer_id:
        washer_id, state, last_timestamp = assign_washer()
        
        if state == "idle":
            return "Washer {} is not in use.".format(washer_id)
    else:
        last_timestamp = get_last_timestamp(washer_id)
        state = get_washer_state(washer_id, last_timestamp)
    
    if state == "faulty":
        return "Washer {} has been reported as faulty.".format(washer_id)
    
    waitlist = get_waitlist(washer_id, last_timestamp)
    
    if chat_id not in waitlist:
        waitlist.append(chat_id)
        set_waitlist(washer_id, waitlist, last_timestamp)
    
    if state == "idle":
        return "Washer {} is currently idle, but you will be notified when it has stopped running.".format(washer_id)
    
    if state == "running":
        time_elapsed = (get_current_timestamp()-int(last_timestamp))//60
        return "Washer {} has been running for {} minutes. You will be notified when it has stopped running.".format(
                washer_id, time_elapsed)


def assign_washer():
    assigned_washer = 0
    state = "faulty"
    smallest_timestamp = "1e37"
    
    for washer in get_washers():
        washer_id = washer.key()
        
        if washer_id == 0:
            continue
        
        last_timestamp = get_last_timestamp(washer_id)
        last_state = get_washer_state(washer_id, last_timestamp)

        if (last_state == "faulty" or
            last_state == "running" and last_timestamp >= smallest_timestamp):
            continue
        
        else:
            assigned_washer = washer_id
            state = last_state
            
            if last_state == "running":
                smallest_timestamp = last_timestamp
            elif last_state == "idle":
                smallest_timestamp = 0
                break

    return assigned_washer, state, smallest_timestamp


def reset(to="blank"):
    if to == "blank":
        db.child("washers").set([])
        db.child("contacts").set([])
    
    elif to == "cleared":
        for washer in get_washers():
            clear_timestamps(washer.key())

