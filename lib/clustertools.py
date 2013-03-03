#from httplib2 import Http
#from urllib   import urlencode
import sys, os
import time
import platform
import requests
import psutil
import socket
import select
import jsonpickle

sys.path.insert(0, '.')

from run import *



setupfile    = 'uisetup.json'


if not os.path.exists(setupfile):
    print "count not find setup file %s" % setupfile
    sys.exit(1)

for k,v in jsonpickle.decode(open(setupfile, 'r').read())['server'].items():
    #print "SERVER K %s V %s" % (k, v)
    globals()[k] = v

for k,v in jsonpickle.decode(open(setupfile, 'r').read())['datas' ].items():
    #print "DATAS K %s V %s" % (k, v)
    globals()[k] = v


class broadcast_sender(object):
    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setblocking(0)
        
        self.sender   = s
    
    def send(self, data):
        self.sender.sendto(data, ('<broadcast>', BROADCAST_PORT))
        

    def broadcastserverinfo(self):
        print "starting broadcast"
        try:
            srvInfo = get_computer_info()
            data    = "%s,%s,%s,%s\n" % (str(srvInfo['curr_time']), srvInfo['host_name'], srvInfo['ip'], PORT)
            #print "sending: ", data
            sys.stdout.flush()
            self.send(data)
            #print "sent"
            sys.stdout.flush()
        except:
            print "error broadcasting", sys.exc_info()
            raise
    


class broadcast_receiver(object):
    def __init__(self):
        r = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        r.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        r.bind(('<broadcast>', BROADCAST_PORT))
        r.setblocking(0)
        
        self.receiver = r

    def receive(self):
        result = select.select([self.receiver],[],[])
        msg    = result[0][0].recv(1024)
        print msg
        return msg
    
    def listenbroadcastserverinfo(self):
        #print "listening broadcast"
        try:
            data = self.receive()
            print "message received", data
            sys.stdout.flush()
            return data
        except:
            print "error listeningn to broadcast", sys.exc_info()
            raise


def get_computer_info():
    info = {}
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    info['host_name'] = socket.gethostname()

    s.connect((IP_TO_QUERY,0))
    info['ip'       ] = s.getsockname()[0]
    s.close()
    #print "ips", socket.gethostbyname_ex(socket.gethostname())[2]
    #info['ip'       ] = ";".join( [ip for ip in socket.gethostbyname_ex('')[2] if not ip.startswith('127.')][:1] )

    #socket.gethostbyname(socket.gethostname())
    info['curr_time'] = time.time()
    
    info['machine'  ] = platform.machine()
    info['node'     ] = platform.node()
    info['platform' ] = platform.platform()
    info['processor'] = platform.processor()
    info['release'  ] = platform.release()
    info['system'   ] = platform.system()
    info['version'  ] = platform.version()
    info['uname'    ] = platform.uname()

    info['phymem'   ] = psutil.TOTAL_PHYMEM
    info['numcpus'  ] = psutil.NUM_CPUS
    info['boottime' ] = psutil.BOOT_TIME



    mem = psutil.virtual_memory()
    info['mem'      ] = mem
    
    disk_par = psutil.disk_partitions()
    disk_use = []
    #print disk_par
    
    #for diskinfo in disk_par:
        #print diskinfo
        #a, b, c, d = diskinfo
        #print 'A', a, 'B', b, 'C', c, 'D', d
        #mountpoint = diskinfo[ 1 ]
        #print 'MOUNTPOINT "%s"' % mountpoint
        #usage = os.statvfs( '/' )
        #print 'USAGE "%s"' % usage
        #disk_use.append( usage )
    
    info['disk'     ] = {
        'partitions': disk_par,
        #'usage'     : disk_use
    }


    info['cpu'] = [{}]
    with open('/proc/cpuinfo', 'r') as cpui:
        for line in cpui:
            if len( line.strip() ) == 0:
                #print "empty"
                info['cpu'].append({})
                break
                #continue
                
            #print line
            lined = line.strip().split(":")
            #print lined
            
            key   = lined[0].strip()
            val   = "".join( line[len(key)+3:] ).strip()
            #print "K '%s' V '%s'" % (key, val)
            
            info['cpu'][-1][key] = val
            
    return info


def get_computer_status():
    info = {}

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    info['host_name'] = socket.gethostname()

    s.connect((IP_TO_QUERY,0))
    info['ip'       ] = s.getsockname()[0]
    s.close()
    #print "ips", socket.gethostbyname_ex(socket.gethostname())[2]
    #info['ip'       ] = ";".join( [ip for ip in socket.gethostbyname_ex('')[2] if not ip.startswith('127.')][:1] )

    #socket.gethostbyname(socket.gethostname())

    info['node'     ] = platform.node()

    mem = psutil.virtual_memory()
    info['mem'      ] = mem

    cpu = psutil.cpu_times()
    info['cpu'      ] = cpu

    diskio = psutil.disk_io_counters()
    info['diskio'   ] = diskio

    networ = psutil.network_io_counters()
    info['network'  ] = networ
    
    info['curr_time'] = time.time()
    
    return info

class run_command(object):
    pass


#class httphandler(object):
#    def __init__(self):
#        pass
#    
#    def putter(self):
#        pass
#    
#    def getter(self):
#        pass
#    
#    def deleter(self):
#        pass
#    
#    def poster(self):
#        pass


#== background ==
#thread
#
#
#pc_info
#
#
#command
#
#
#stdout / stderr / queue - multitherad
#
#
#proc info