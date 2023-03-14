from socket import *
serverName = input('Who are we contacting? ')
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_DGRAM)
message = input('input lowercase sentence: ')
clientSocket.sendto(message.encode(),(serverName, serverPort))
modifiedMessage, serverAddress = clientSocket.recvfrom(1048)
print (modifiedMessage.decode())
clientSocket.close()
