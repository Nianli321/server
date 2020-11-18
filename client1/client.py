#Nian Li Nov 2020
from socket import *
import sys
import os
import re
import threading
import time

def check_command(command):
    all_commands = ["CRT", "MSG", "DLT", "EDT", "LST", "RDT", "UPD", "DWN", "RMV", "XIT", "SHT"]
    return command.split()[0] in all_commands

#cited from https://stackoverflow.com/a/20007570
#author: freakish        
#convert bytes to number
def byte_number_converter(parameter, mode):
    if mode == 0:
        number = 0
        i = 0
        while i < 4:
            number += parameter[i] << (i*8)
            i += 1
        return number
    elif mode == 1:
        byte = bytearray()
        byte.append(255 & parameter)
        i = 0
        while i < 3:    
            parameter = parameter >> 8        
            byte.append(255 & parameter)
            i += 1
        return byte

def thread_check_server():
    while True:
        s = socket(AF_INET, SOCK_STREAM)
        time.sleep(0.5)
        try:
            s.connect((server_IP, server_port))
            s.send(b"TS")
            s.close()
        except:
            print("GoodBye server is shutting down")
            clientSocket.close()
            break
    os._exit(1)

#get server IP
server_IP = sys.argv[1]
#get server port number
server_port = int(sys.argv[2])
#create client socket
clientSocket = socket(AF_INET, SOCK_STREAM)
#estsblish connection
clientSocket.connect((server_IP, server_port))
#showing identity
clientSocket.send(b"CL")
exit_client = 0

#a thread for checking if server is alive
thread_check_server = threading.Thread(target=thread_check_server)
thread_check_server.start()
#login
while(1):
    while(1):
        username = input("Enter username\n")
        if username != "":
            break
        else:
            print("username can't be empty, please retype it")
    #clientSocket.sendall(username.encode())
    while(1):    
        password = input("Enter password\n")
        if password != "":
            break
        else:
            print("password can't be empty, please retype it")
    u_and_p = username + " " + password
    clientSocket.sendall(u_and_p.encode())
    reply = clientSocket.recv(2)
    if reply == b"OK":
        print("Welcom to the forum")
        break
    elif reply == b"NO":
        print("Wrong password and username, please type again")
    elif reply == b"ET":
        print("login rejected, client with the same username is active")


#get command
while(1):
    comm = input("Enter one of the following commands: CRT,\nMSG, DLT, EDT, LST, RDT, UPD, DWN, RMV,\nXIT, SHT: ")
    if not check_command (comm):
        print("Invalid command")
        continue
    elif comm.split()[0] == "UPD":
        if len(comm.split()) != 3:
            print("invalid parameter: Please follow the correct format \"UPD title filename\"")
            continue
        elif comm.split()[2] not in os.listdir():
            print ("the file doesn't exist in the current working directory")
            continue
        
        else:
            clientSocket.sendall(comm.encode())
            reply = clientSocket.recv(2)
          
            if reply == b"ET":
                print("uploading failed, file already exists in the thread")
            elif reply == b"NT":
                print("uploading failed, thread doesn't exist")
            elif reply == b"OK":
                print("{} uploaded to {} thread".format(comm.split()[2], comm.split()[1]))
                
                #the following 2 lines of code is 
                #cited from https://stackoverflow.com/a/20007570
                #author: freakish   
                l = os.path.getsize(comm.split()[2])
                clientSocket.send(byte_number_converter(l, 1))
                with open(comm.split()[2], "rb") as f:
                    line = f.read(1024)
                    while line:
                        clientSocket.send(line)
                        line = f.read(1024)
                    print("finish sending") 
 
    elif comm.split()[0] == "DWN":
        if len(comm.split()) != 3:
            print("invalid parameter: Please follow the correct format \"DWN title filename\"")
            continue
        else:
            clientSocket.sendall(comm.encode())
            reply = clientSocket.recv(2)
            if reply == b"NE":
                print("downloading failed, thread doesn't exist")
            elif reply == b"NF":
                print("downloading failed, file doesn't exist")
            elif reply == b"OK":
                print("ready to download")
                file_size = byte_number_converter(clientSocket.recv(4), 0)
                curr_size = 0
                #the following pieces of code are
                #cited from https://stackoverflow.com/a/20007570
                #author: freakish
                with open(comm.split()[2], "wb") as f:
                    while curr_size < file_size:
                        line = clientSocket.recv(1024)
                        if not line:
                            break
                        if file_size < len(line) + curr_size:
                            line = line[:file_size - curr_size]
                        curr_size += len (line)
                        f.write(line)
                    print("file downloaded")
    elif comm.split()[0] == "RMV":
        if len(comm.split()) != 2:
            print("invalid parameter: Please follow the correct format \"RMV title\"")
            continue
        else:
            clientSocket.sendall(comm.encode())
            reply = clientSocket.recv(2)
            if reply == b"NT":
                print("removing failed, thread doesn't exist")
            elif reply == b"NU":
                print("removing failed, you are not the owner of the thread")
            elif reply == b"OK":
                print("{} is removed". format(comm.split()[1]))
    elif comm.split()[0] == "XIT":
        if len(comm.split()) != 1:
            print("XIT should have no arguments")
            continue 
        else:
            clientSocket.sendall(comm.encode())
            print("GoodBye")
            clientSocket.close()
            break
    elif comm.split()[0] == "RDT":
        
        if len(comm.split()) != 2:
            print("invalid parameter: Please follow the correct format \"RDT title\"")
            continue
        else:
            clientSocket.sendall(comm.encode())
            reply = clientSocket.recv(2)

            if reply == b"NX":
 
                print("reading failed, {} thread doesn't exist".format(comm.split()[1]))
            elif reply == b"OK":

                
                #the following pieces of code are
                #cited from https://stackoverflow.com/a/20007570
                #author: freakish
                file_size = byte_number_converter(clientSocket.recv(4), 0)
                curr_size = 0
                thread = ""
                while curr_size < file_size:
                    line = clientSocket.recv(1024)
                    if not line:
                        break
                    if file_size < len(line) + curr_size:
                        line = line[:file_size - curr_size]
                    curr_size += len(line)   
                    thread += line.decode("utf-8")
                thread = thread.split("\n")
                thread.pop(0)
                if len(thread) == 1:
                    print("Thread {} is empty".format(comm.split()[1]))
                else:
                    print("\n".join(thread))
                    
    elif comm.split()[0] == "LST":
        if len(comm.split()) != 1:
            print("invalid parameter: LST has no arguments")
            continue
        else:
            clientSocket.sendall(comm.encode())
            reply = clientSocket.recv(2)

            if reply == b"NO":
                print("there is no threads in the server")
            elif reply == b"OK":
                #the following pieces of code are
                #cited from https://stackoverflow.com/a/20007570
                #author: freakish
                file_size = byte_number_converter(clientSocket.recv(4), 0)
                curr_size = 0
                while curr_size < file_size:
                    line = clientSocket.recv(1024)
                    if not line:
                        break
                    if file_size < len(line) + curr_size:
                        line = line[:file_size - curr_size]
                    curr_size += len(line)   
                    print(line.decode("utf-8"))
    elif comm.split()[0] == "CRT":
        if len(comm.split()) == 2:
            clientSocket.sendall(comm.encode())
            reply = clientSocket.recv(10)
            
            if reply == b"ET":
                print("thread can't be created, it already exists")
            elif reply == b"OK":
                print("Thread {} is created".format(comm.split()[1]))    
        else:
            print("invalid parameter: Please follow the correct format \"CRT Thread\"")
    elif comm.split()[0] == "SHT":
        if len(comm.split()) == 2:
            clientSocket.sendall(comm.encode())
            reply = clientSocket.recv(2)
            if reply == b"NO":
                print("shut down failed: wrong admin password")
            elif reply == b"OK":
                print("shut down successful")
        else:
            print("invalid parameter: Please follow the correct format \"SHT admin_password\"")


    else:
        clientSocket.sendall(comm.encode())
        reply = clientSocket.recv(1024).decode("utf-8")
        print(reply)

        
 



