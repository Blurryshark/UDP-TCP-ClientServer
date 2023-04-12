#!env python

#Tamana Zahir
#Liam Cristescu
#Guy Allgood
#Tomas Diaz-Wahl
#04.11.2023
#CST311 SP23

#This script will establish a network with 2 hosts connected to eachother by a single 
#router. The two hosts will both exist on a different subnet, both with a /24 network mask. 
#All devices on the network are able to communicate with eachother, including the two hosts. 

from mininet.net import Mininet
from mininet.node import Host, Node
from mininet.cli import CLI
from mininet.log import setLogLevel, info

def myNetwork():
  
  net = Mininet( topo=None,
                 build=False,
                 ipBase='10.0.0.0/8')
  
  info( '*** Adding controller\n' )
  info( '*** Add switches\n')
  r1 = net.addHost('r1', cls=Node, ip='192.0.1.1')
  r1.cmd('sysctl -w net.ipv4.ip_forward=1')
  info( '*** Add hosts\n')

# Added 'via' to the defaultRoute argument for addHost(). This was evidently keeping the hosts 
# from using the router for inter-subnet communication. completely dumb.

  h1 = net.addHost('h1', cls=Host, ip='192.0.1.2/24', defaultRoute='via 192.0.1.1')
  h2 = net.addHost('h2', cls=Host, ip='10.0.0.3/24', defaultRoute='via 10.0.0.1')
   
# Changes made to the lines below. According to the 'linuxrouter.py' script, the proper parameters
# to add for the third and fourth arguments are the port of the ROUTER, and the IP associated with 
# said port, respectively. I suppose mininet doesn't care which port on the host the link is 
# plugged in to. Python is Man's final sin against God. 

  net.addLink( h1, r1, intfName1 = 'r1-eth0', params2={ 'ip' : '192.0.1.1/24' } ) 
  net.addLink( h2, r1, intfName1 = 'r1-eth1', params2={ 'ip' : '10.0.0.1/24' } )
  
  info( '*** Starting network\n')
  net.build()
  
  CLI(net)
  net.stop()

if __name__ == '__main__':
  setLogLevel( 'info' )
myNetwork()
