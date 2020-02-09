import collections
import laundrypidb
import laundrypibot
import sys


class Washer:
    starting_threshold = 0.7
    starting_time = 20
    stopping_threshold = 0.7
    stopping_time = 20
    interval = 0.5
    valid_states = ("faulty", "idle", "running")
    debug = True
    
    def __init__(self, washer_id):
        self.washer_id = washer_id
        
        starting_len = int(self.starting_time/self.interval)
        self.starting = collections.deque([False]*starting_len, maxlen=starting_len)
        
        stopping_len = int(self.starting_time/self.interval)
        self.stopping = collections.deque([False]*stopping_len, maxlen=stopping_len)
        
        self.sync_washer()
        
    def sync_washer(self):
        try:
            self.last_timestamp = laundrypidb.get_last_timestamp(self.washer_id)
            self.last_state = laundrypidb.get_washer_state(self.washer_id, self.last_timestamp)
            
            if self.debug:
                sys.stdout.write("Washer {} state sync-ed to: \"{}\" at timestamp: {}\n".format(self.washer_id, self.last_state, self.last_timestamp))
            
            return 0
        
        except:
            self.last_timestamp = None
            self.last_state = None
            
            if self.debug:
                sys.stdout.write("Error in sync-ing washer {} state\n".format(self.washer_id))
            
            return 1

    def update_state(self, next_state):
        if (next_state not in self.valid_states or
            next_state == self.last_state or 
            self.last_state == "faulty" and next_state != "running"):

            if self.debug:
                sys.stdout.write("\nError in updating washer {} state\n".format(self.washer_id))
            
            return 1
        
        waitlist = laundrypidb.get_waitlist(self.washer_id)
        if next_state == "idle":
            while waitlist:
                laundrypibot.send_washer_notification(waitlist.pop(), self.washer_id)
        
        laundrypidb.set_washer_state(self.washer_id, next_state)
        laundrypidb.set_waitlist(self.washer_id, waitlist)
        
        if self.debug:
            sys.stdout.write("\nWasher {} state updated to: \"{}\" and waitlist set to: {} at timestamp: {}\n".format(self.washer_id, next_state, waitlist, self.last_timestamp))
        
        self.sync_washer()
        return 0
    
    def step(self, inp):
        if self.last_state == "running":
            self.stopping.append(inp == False)
            stopping_quotient = sum(self.stopping) / len(self.stopping)
            
            if self.debug:
                print("Washer {} stopping: {:.2f}/{:.2f}".format(self.washer_id, stopping_quotient, self.stopping_threshold), end="\r")
            
            if stopping_quotient >= self.stopping_threshold:
                while any(self.stopping):
                    self.stopping.append(False)
                
                self.update_state("idle")
        
        else:
            self.starting.append(inp == True)
            starting_quotient = sum(self.starting) / len(self.starting)
            
            if self.debug:
                print("Washer {} starting: {:.2f}/{:.2f}".format(self.washer_id, starting_quotient, self.starting_threshold), end="\r")
            
            if starting_quotient >= self.starting_threshold:
                while any(self.starting):
                    self.starting.append(False)
                
                self.update_state("running")
                
                

