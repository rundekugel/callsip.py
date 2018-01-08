# callsip.py
Simple SIP Phone caller. V0.2 
This small script let's a SIP Phone ring, without register.
Only ringing is supported, so sound transport until yet.
<p>
usage:
callsip [-v:N|-p:Port|-dS:ec.|-s:Via-server] sip-user-address
option (default)    , desc.
 -c: (555@caller)    , caller sip-address or phone number
 -d: (5)             , duration(sec.)
 -l: (na)            , own ip or URI
 -p: (5060)          , port
 -s: (from address)  , via-server ip or URI
 -u  (),             , use UDP instead of TCP
 -v: (0)             , verboselevel 0..4

examples:
   callsip -d:3 alice@home.net
   #starts a sip call to alice and hangs up after 3 sec.
   callsip c:+4930555@x alice@home.net
   #starts a sip call to alice with callerid 004930555.

</p>