#Nian Li Nov 2020
from socket import *
import sys
import os

def check_command(command):
    all_commands = ["CRT", "MSG", "DLT", "EDT", "LST", "RDT", "UPD", "DWN", "RMV", "XIT", "SHT"]
    return command.split()[0] in all_commands

#get server IP
server_IP = sys.argv[1]
#get server port number
server_port = int(sys.argv[2])
#create client socket
clientSocket = socket(AF_INET, SOCK_STREAM)
#estsblish connection
clientSocket.connect((server_IP, server_port))

#login
while(1):
    username = input("Enter username\n")
    if username != "":
        break
    else:
        print("username can't be empty, please retype it")
while(1):    
    password = input("Enter password\n")
    if password != "":
        break
    else:
        print("password can't be empty, please retype it")
clientSocket.sendall(username.encode())
clientSocket.sendall(password.encode())
while (1):
    msg_login = clientSocket.recv(1024).decode("utf-8")
    print(msg_login)
    if msg_login == "Welcome to the forum":
        break
    else:
        username = input("Enter username\n")      
        password = input("Enter password\n")
    
        clientSocket.sendall(username.encode())
        clientSocket.sendall(password.encode())

#get command
while(1):
    comm = input("Enter one of the following commands: CRT,\nMSG, DLT, EDT, LST, RDT, UPD, DWN, RMV,\nXIT, SHT: ")
    if not check_command (comm):
        print("Invalid command")
        continue
    elif comm.split()[0] == "UPD":
        clientSocket.sendall(comm.encode())
        if len(comm.split()) != 3:
            print("invalid parameter: Please follow the correct format \"UPD title filename\"")
            continue
        elif comm.split()[2] not in os.listdir():
            print ("the file doesn't exist in the current working directory")
            continue
        else:
            with open(comm.split()[2], "rb") as f:
                line = f.read(1024)
                while line:
                    clientSocket.send(line)
                    line = f.read(1024)
            clientSocket.send(b"finish")
        reply = clientSocket.recv(1024).decode("utf-8")  
        print(reply)  



    else:
        clientSocket.sendall(comm.encode())
        reply = clientSocket.recv(1024).decode("utf-8")
        print(reply)

        
 
#clientSocket.close()


