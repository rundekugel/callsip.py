#!/usr/bin/env python
#$Id: callsip.py 523 2014-11-02 13:21:33Z gaul1 $

'''
SIP Phone caller. V0.3 by lifesim.de 
'''
import os
import socket
import sys
import time

CRLF="\r\n"

#---
def buildSipMsg(action, receiver, viaserver, caller, protocol="TCP", tag="x", verbosity=0):  
  msg=""
  msg+= action+" sip:"+receiver+" SIP/2.0"+CRLF
  msg+="Via: SIP/2.0/"+protocol+" "+viaserver+CRLF
  msg+="To: sip:"+receiver+";tag="+tag+CRLF
  msg+="From: sip:"+caller+CRLF
  msg+="Call-ID: "+getCallId(new=False)+CRLF
  msg+="Cseq: "+str(getseq(inc=False))+" "+action+CRLF
  #msg+="Contact: sip:xx@"$localIp+CRLF
  msg+=CRLF
  return msg

def show_help():
  ret= "SIP Phone caller. V0.3 by lifesim.de"+CRLF
  ret+= "usage:"+CRLF+"callsip [-v:N|-p:Port|-dS:ec.|-s:Via-server] sip-user-address"+CRLF
  ret+= "option (default)    , desc."+CRLF
  ret+= " -c: (555@caller)    , caller sip-address or phone number"+CRLF
  ret+= " -d: (5)             , duration(sec.)"+CRLF
  ret+= " -l: (na)            , own ip or URI"+CRLF
  ret+= " -p: (5060)          , port"+CRLF
  ret+= " -s: (from address)  , via-server ip or URI"+CRLF
  ret+= " -u  (),             , use UDP instead of TCP"+CRLF
  ret+= " -v: (0)             , verboselevel 0..4"+CRLF
  ret+= CRLF
  ret+= "examples:"+CRLF
  ret+= "   callsip -d:3 alice@home.net"+CRLF
  ret+= "   #starts a sip call to alice and hangs up after 3 sec."+CRLF
  ret+= "   callsip c:+4930555@x alice@home.net"+CRLF
  ret+= "   #starts a sip call to alice with callerid 004930555."+CRLF
  print(ret)
  return ret


def getseq(reset=0, inc=True):
  this=getseq
  if 'cseq' not in this.__dict__:
    this.cseq=0
  if reset:
    this.cseq=0
  if inc:
    this.cseq+=1
  return this.cseq
  
def getCallId(new=0):
  this=getCallId
  if 'cid' not in this.__dict__:
    this.cid="c0" 
  if new:
    this.cid="c"+hex(int(time.time()*10))
  return this.cid
    
def txMsg(s,action, receiver, viaserver, caller, tcpudp="TCP", tag="x", verbosity=0):  
  if s==None:
    return -1
  m=buildSipMsg(action,receiver, viaserver, caller, protocol=tcpudp, tag=tag)  
  if verbosity>2:
    print("<--tx:"+os.linesep+m)
  r=0;rx=""
  tries=100
  keyw="Content-Length"
  try:
    r=s.send(m.encode())
    if verbosity>3:
      print("sent %d bytes:"%r)
    while tries:
      if tcpudp=="TCP":
        r=s.recv(2048)
      else:

        r,server=s.recvfrom(2048)
      if verbosity>5:
        print(r)
      rx+=r
      if keyw in rx:
        tries=0
        if verbosity>2:
          print("found")
        break
      tries -=1
      time.sleep(0.05)
    if verbosity>2:  
      print("tries:"+str(tries))
  except Exception as e:
    if verbosity:
      print("rx err: "+str(e))
    pass
  if verbosity>3:
    print("received %d bytes:"%len(rx))
  if verbosity>1:
    print("-->rx:"+os.linesep+rx)
  #todo: parse cseq, tag, cid and validate
  return r
  
def callsip(sipadr, caller="555@x", duration=5, viaServer="", port=5060, tag="x", tcpudp="TCP", forceipv6=0, verbosity=0):  
  if viaServer=="":
    v=sipadr.split("@")
    if len(v)<2:
      return -2
    viaServer=v[1]
  v=caller.split("@")
  if len(v)<2:
    caller+="@x"
  if verbosity>0:
    print("SIP Phone caller. V0.3-$Rev: 424 $")
    print("duration=["+str(duration)+"]")
    print("verbose=["+str(verbosity)+"]")
    print("receiver-sipaddress=["+sipadr+"]")
    print("caller=["+caller+"]")
  if verbosity>1:
    print("via-server="+viaServer+":"+str(port))
    print("tag=["+tag+"]")

  #--- open connection to send sip
  if verbosity:
    print("Connecting to " + viaServer +":"+str(port))
  if tcpudp=="TCP":
    protocol=socket.SOCK_STREAM
  else:
    protocol=socket.SOCK_DGRAM
  if forceipv6:
    if verbosity:
      print("ipv6")
    s = socket.socket(socket.AF_INET6, protocol, 0)
  else:
    s = socket.socket(socket.AF_INET, protocol)
  if s==None:
    try:
      if verbosity:
        print("try ipv6")
      s = socket.socket(socket.AF_INET6, protocol, 0)
    except:
      pass
  #print ("done.")
  try:
    r=s.connect((viaServer, port))
  except:
    if verbosity:
      print("no connect!")
      return -1
  #print (r,s)
  if verbosity>1:
    print("Connected to:"+s.getpeername()[0])
  #s.setblocking(0.1)
  s.settimeout(0.2)
 
  #--talk sip
  getCallId(new=True)
  getseq(reset=True)
  #if port!=5060:
    #viaServer=viaServer+":"+str(port)
  r=txMsg(s,"INVITE", sipadr, viaServer, caller, tcpudp=tcpudp, tag=tag, verbosity=verbosity)   
  time.sleep(duration)
  getseq(inc=True)
  r=txMsg(s,"BYE", sipadr, viaServer, caller, tcpudp=tcpudp, tag=tag, verbosity=verbosity)   
  #s.shutdown()
  s.close()  
  return 0
      
def main():
  args=sys.argv
  if len(args)<2:
    show_help()
    return 1
  port=5060
  caller="555@x"
  viaServer=""
  sipadr=""
  tcpudp="TCP"
  verbosity=1
  forceipv6=0
  tag="x"
  duration=3
  #--- parse params
  for arg in sys.argv:
    a3=arg[:3]
    a4=arg[:4]
    if arg == "-h" or arg=='?':  
      show_help()
    elif arg[:3] == "-v:":
      verbosity = int(arg[3:],10)
    elif a3 == "-c:":
      caller=arg[3:]
    elif a3 == "-d:":
      duration = int(arg[3:],10)
    elif a3== "-l:":
      myUri =arg[3:]
    elif a3== "-s:":
      viaServer =arg[3:]
    elif a3== "-t:":
      tag =arg[3:]
    elif a3 == "-p:":
      port = int(arg[4:],10)
    elif arg=="-u":
      tcpudp="UDP"
    elif arg=="-6":
      forceipv6=1
    elif arg[0]!="-":
      sipadr=arg
  #---
  r=callsip(sipadr, caller=caller, duration=duration, viaServer=viaServer, port=port, 
            tag=tag, tcpudp=tcpudp, forceipv6=forceipv6,verbosity=verbosity)
  
if __name__ == "__main__":
  main()
  
#eof
