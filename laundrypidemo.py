#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import laundrypidb


def demo1():
    laundrypidb.reset("blank")
    ts = laundrypidb.get_current_timestamp()
    laundrypidb.set_washer_state(1, "idle", ts)
    laundrypidb.set_washer_state(2, "running", ts-20*60)
    laundrypidb.set_washer_state(3, "running", ts-12*60)
    laundrypidb.set_washer_state(4, "faulty", ts-32*60)
    return 0
    

def demo2():
    laundrypidb.reset("blank")
    ts = laundrypidb.get_current_timestamp()
    laundrypidb.set_washer_state(1, "running", ts-27*60)
    laundrypidb.set_washer_state(2, "running", ts-20*60)
    laundrypidb.set_washer_state(3, "running", ts-12*60)
    laundrypidb.set_washer_state(4, "faulty", ts-32*60)
    return 0


demos = {"1": demo1,
         "2": demo2}


def main():
    if len(sys.argv) != 2:
        sys.stdout.write("usage: python3 laundrypidemo.py [num]")
        return 1
    
    else:
        try:
            return demos[sys.argv[1]]()
        except:
            return 1


if __name__ == "__main__":
    main()