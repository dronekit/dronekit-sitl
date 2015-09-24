from __future__ import print_function
import time
import socket
import sys
import os
import platform
import re
from pymavlink import mavutil
from Queue import Empty

if platform.system() == 'Windows':
    from errno import WSAECONNRESET as ECONNABORTED
else:
    from errno import ECONNABORTED

# Clean impl of mp dependencies for droneapi

import droneapi.module.api as api

def errprinter(*args):
    print(*args, file=sys.stderr)







def wait_read(sock):
    while True:
        inputready, outputready, exceptready = select.select([sock],[],[],.1)
        if len(inputready):
            break

def wait_write(sock):
    while True:
        inputready, outputready, exceptready = select.select([],[sock],[],.1)
        if len(outputready):
            break

def spawn(target, *args):
    t = Thread(target=target, args=args)
    t.daemon = True
    t.start()
    return t

def udp(port):
    sock = socket.socket(type=socket.SOCK_DGRAM)

    in_queue = Queue()
    out_queue = Queue() 

    def read():
        while True:
            try:
                wait_read(sock.fileno())
                data, address = sock.recvfrom(port)
                #print(role, 'received %s:%s: got %r' % (address + (data, )))
                in_queue.put((data, address))
            except socket.error as e:
                print('Socket error:', e)
                break

    def write():
        while True:
            try:
                wait_write(sock.fileno())
                (msg, target) = out_queue.get()
                #print(role, 'sending %s' % msg)
                out_bytes = sock.sendto(msg, ('0.0.0.0', target))
            except socket.error as e:
                print('Socket error:', e)
                break

    thr = spawn(read)
    thw = spawn(write)

    return (in_queue, out_queue, thr, thw)






class MavWriter():
    def __init__(self, queue):
        self.queue = queue

    def write(self, pkt):
        self.queue.put(pkt)

    def read(self):
        errprinter('writer should not have had a read request')
        os._exit(43)

def send_heartbeat(master):
    master.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)

def request_data_stream_send(master, rate=1):
    master.mav.request_data_stream_send(master.target_system, master.target_component,
                                        mavutil.mavlink.MAV_DATA_STREAM_ALL, rate, 1)

from Queue import Queue
from threading import Thread

def forward():
    mav = mavutil.mavlink.MAVLink(MavWriter(self.out_queue), srcSystem=0, use_native=False)
    #self.master

    import atexit
    self.exiting = False
    def onexit():
        self.exiting = True
    atexit.register(onexit)

    # Wait for incoming messages.
    (inudp, outudp, thr, thw) = udp(6760)

    def mavlink_thread():
        # Huge try catch in case we see http://bugs.python.org/issue1856
        try:
            while True:
                # Downtime                    
                time.sleep(0.05)

                while True:
                    try:
                        msg = inudp.get_nowait()
                        self.master.write(msg)
                    except socket.error as error:
                        if error.errno == ECONNABORTED:
                            errprinter('reestablishing connection after read timeout')
                            try:
                                self.master.close()
                            except:
                                pass
                            self.master = mavutil.mavlink_connection(self.master.address)
                            continue

                        # If connection reset (closed), stop polling.
                        return
                    except Empty:
                        break
                    except Exception as e:
                        errprinter('mav send error:', e)
                        break

                while True:
                    try:
                        msg = self.master.recv_msg()
                    except socket.error as error:
                        if error.errno == ECONNABORTED:
                            errprinter('reestablishing connection after send timeout')
                            try:
                                self.master.close()
                            except:
                                pass
                            self.master = mavutil.mavlink_connection(self.master.address)
                            continue

                        # If connection reset (closed), stop polling.
                        return
                    except Exception as e:
                        # TODO debug these.
                        # errprinter('mav recv error:', e)
                        msg = None
                    if not msg:
                        break

                    outudp.put((msg, 6760))

        except Exception as e:
            # http://bugs.python.org/issue1856
            if self.exiting:
                pass
            else:
                raise e


    t = Thread(target=mavlink_thread)
    t.daemon = True
    t.start()

    print('udpin:127.0.0.1:6760')

    t.join()
    thr.join()
    thw.join()

    print('done.')


# def connect(ip, await_params=False, status_printer=errprinter):
#     import droneapi.module.api as api
#     state = MPFakeState(mavutil.mavlink_connection(ip))
#     state.status_printer = status_printer
#     # api.init(state)
#     return state.prepare(await_params=await_params).get_vehicles()[0]