#Nian Li comp3331 assignment Nov 2020
import sys
from socket import *
import os
import re
import threading

#thread class, representing the thread in the forum
class Thread:
    def __init__(self, creater, title, counter):
        self.creater = creater
        self.title = title
        self.counter = counter
        self.messages = []
        self.files = []
    def add_msg(self, username, msg):
        self.counter += 1
        self.messages.append(username + ": " + msg + "\n")
        with open(self.title, "a") as f:
            f.write(str(self.counter) + " " + username + ": " + msg + "\n")
            
    def get_title(self):
        return self.title

    def get_creater(self):
        return self.creater    

    def delete_msg(self, number, username, conn):
        if int(number) not in range (1, int(self.counter) + 1):
            print ("The message doesn't exist")
            conn.sendall("The message doesn't exist".format(username).encode())     
        elif self.messages[self.get_message(int(number))].split(":")[0] == username:
            self.messages.pop(self.get_message(int(number)))
            self.update()
            self.counter -= 1
            print ("The message hsa been deleted")
            conn.sendall("The message hsa been deleted".encode())                
        else:
            print("deleting rejected, {} is not the creater of message".format(username))
            conn.sendall("deleting rejected, {} is not the creater of message".format(username).encode()) 
    
    def edit_msg(self, username, number, message, conn):
        if int(number) not in range (1, int(self.counter) + 1):
            print ("The message doesn't exist")
            conn.sendall("The message doesn't exist".format(username).encode())     
        
        elif self.messages[self.get_message(int(number))].split(":")[0] == username:
            self.messages[self.get_message(int(number))] = username + ": " + message + "\n"
            self.update()
            
            print ("The message hsa been edited")
            conn.sendall("The message hsa been edited".encode())       
        
        else:
            print("editing rejected, {} is not the creater of message".format(username))
            conn.sendall("editing rejected, {} is not the creater of message".format(username).encode()) 

    def update(self):
        with open(self.title, "w") as f:
            f.write(self.creater + "\n")
            counter = 1
            for i in range(1, len(self.messages) + 1):
                if re.search("^\S+ uploaded \S+$", self.messages[i - 1]) == None:
                    f.write(str(counter) + " " + self.messages[i - 1])
                    counter += 1
                else:
                    f.write(self.messages[i - 1])


    def add_file(self, file_name, username):
        self.messages.append("{} uploaded {}".format(username, file_name) + "\n")
        with open(self.title, "a") as f:
            f.write("{} uploaded {}".format(username, file_name) + "\n")
    #return the username of the user who posted the message
    def get_message_poster(self, number):
        index = self.get_message(int(number))
        poster = self.messages[index].split(":")[0]
        return poster
    #return the index of the message in the messages list, upload message will be skipped
    def get_message(self, number):
        counter = 0
        index = 0
        for line in self.messages: 
            if re.search("^\S+ uploaded \S+\n$" ,line) != None:
                index += 1
                continue
            else:
                counter += 1
            
            if counter == number:
                return int(index)
            
            index += 1     
        
        
#find the thread and return it
#if no, return false
def find_thread(title):
    global threads
    for thread in threads:
        if thread.get_title() == title:
            return thread
    return False   

#clean the files 
def clear_forum():
    for file in os.listdir():
        if file != "client.py" and file != "server.py" and file != "credentials.txt":
            os.remove(file)
        

#check username and password, and return true and false
def check_credetial(u_and_p):
    
    f = open("credentials.txt", "r")
    for line in f:
        if line.rstrip("\n") == u_and_p.rstrip("\n"):
            return True
    f.close() 
    return False

#create a new file, write user's name and return True
#otherwise return False
def create_thread (username, title, conn):
    global threads
    if title in map(Thread.get_title, threads):
        print("Thread {} exists".format(title))
        conn.send(b"ET")
    else:
        conn.send(b"OK")
        with open(title, "x") as f:
            f.write(username + "\n")
        new_thread = Thread(username, title, 0)   
        threads.append(new_thread)
        thread_titles.append(new_thread.get_title())
        print("Thread {} created".format(title))

def post_message (username, title, message, conn):
    thread = find_thread(title)
    if thread != False:#thread exist, add message 
        thread.add_msg(username, message)
        print("Message {} posted to {} thread".format(message, title))
        conn.sendall("Message {} posted to {} thread".format(message, title).encode())
    else:#send error when thread doesn't exist
        print("post failed, {} thread doesn't exist".format(title))
        conn.sendall("post failed, {} thread doesn't exist".format(title).encode())

def delete_message (username, title, n_msg, conn):
    thread = find_thread(title)
    if thread == False:
        print("deleting failed, {} thread doesn't exist".format(title))
        conn.sendall("deleting failed, {} thread doesn't exist".format(title).encode())
    elif thread.get_creater() != username:
        print("deleting rejected, {} is not the creater of message {}".format(username, title))
        conn.sendall("deleting rejected, {} is not the creater of message {}".format(username, title).encode())
    else:
        with lock:
            thread.delete_msg(n_msg, username, conn)

def edit_message(username, title, n_msg, message, conn):
    thread = find_thread(title)
    if thread == False:
        print("editing failed, {} thread doesn't exist".format(title))
        conn.sendall("editing failed, {} thread doesn't exist".format(title).encode())
    elif thread.get_message_poster(n_msg) != username:
        print("editing rejected, {} is not the creater of message {}".format(username, title))
        conn.sendall("editing rejected, {} is not the creater of message {}".format(username, title).encode())
    else:
        with lock:
            thread.edit_msg(username, n_msg, message, conn)

def read_thread(title, conn):
    thread = find_thread(title)
    if thread == False:
        print("reading failed, {} thread doesn't exist".format(title))
        conn.send(b"NX")
    else:
        conn.send(b"OK") #tell the client to get ready to revice content in the thread
        #the following 2 lines of code is 
        #cited from https://stackoverflow.com/a/20007570
        #author: freakish   
        l = os.path.getsize(title)
        conn.send(byte_number_converter(l, 1))
        with open(title, "rb") as f:
            line = f.read(1024)
            while line:
                conn.send(line)
                line = f.read(1024)
        

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


def upload_file(username, title, filename, conn):
    thread = find_thread(title)

    if thread == False:
        print("uploading failed, {} thread doesn't exist".format(title))
        conn.sendall(b"NT") 
    else:
        conn.sendall(b"OK")
        print("sending file")
        with open(title + "-" + filename, "wb") as f:
            #the following pieces of code are
            #cited from https://stackoverflow.com/a/20007570
            #author: freakish
            file_size = byte_number_converter(conn.recv(4), 0)
            curr_size = 0
            while curr_size < file_size:
                line = conn.recv(1024)
                if not line:
                    break
                if file_size < len(line) + curr_size:
                    line = line[:file_size - curr_size]
                curr_size += len(line)   
                f.write(line)

        thread.add_file(filename, username)
        print("uploading finish")

def download_file(username, title, filename, conn):
    #the following pieces of code are
    #cited from https://stackoverflow.com/a/20007570
    #author: freakish
    l = os.path.getsize(filename)
    conn.send(byte_number_converter(l, 1))
    with open(filename, "rb") as f:
        line = f.read(1024)
        while line:
            conn.send(line)
            line = f.read(1024)
        print("finish sending")

    
def new_thread_client (conn):
    global clients

    #check password and username
    while(1):
        #recive username and password
        u_and_p = conn.recv(1024).decode("utf-8")        
        if not check_credetial(u_and_p):
            print("Incorrect password")
            conn.send(b"NO")
            continue
        
        username = u_and_p.split()[0]
        if username in clients:
            conn.send(b"ET")
            print("login rejected, client with the same username is active")
            continue
        break


    clients.append(username)
    conn.send(b"OK")
    print("{} successful login".format(username))
    
    while True:
        comm = conn.recv(1024).decode("utf-8")
        if comm == '':
            break
        print("{} issued {} command".format(username, comm.split()[0]))

        if comm.split()[0] == "CRT":
            with lock:
                create_thread(username,comm.split()[1], conn)
           
        elif comm.split()[0] == "MSG":
            if len(comm.split()) >= 3:
                with lock:
                    post_message(username, comm.split()[1], ' '.join(comm.split()[2:]), conn)   
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"MSG Thread Message\"".encode())   
            
        elif comm.split()[0] == "DLT":
            if len(comm.split()) == 3:
                with lock:
                    delete_message(username, comm.split()[1], comm.split()[2], conn)
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"DLT Thread MessageNumber\"".encode())

        elif comm.split()[0] == "EDT":
            if len(comm.split()) >= 4:
                with lock:
                    edit_message(username, comm.split()[1], comm.split()[2], " ".join(comm.split()[3:]), conn)
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"EDT Thread MessageNumber Message\"".encode())    

        elif comm.split()[0] == "UPD":
            if len(comm.split()) == 3:
                with lock:
                    upload_file(username, comm.split()[1], comm.split()[2], conn)
            else:
                print("invalid parameter")
                

        elif comm.split()[0] == "RDT":
            if len(comm.split()) == 2:
                with lock:
                    read_thread(comm.split()[1], conn)
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"RDT title\"".encode())

        elif comm.split()[0] == "DWN":
            filename = comm.split()[1] + "-" + comm.split()[2]
            if comm.split()[1] not in os.listdir():
                print("downloading failed, thread doesn't exist")
                conn.send(b"NE")
            elif filename not in os.listdir():
                print("downloading failed, file doesn't exist")
                conn.send(b"NF")
            else:    
                conn.send(b"OK")
                with lock:
                    download_file(username, comm.split()[1], filename, conn)
        
        elif comm.split()[0] == "RMV":
            thread = find_thread(comm.split()[1])
            t_name = comm.split()[1]
            if thread == False:
                conn.send(b"NT")
                print("removing failed, thread doesn't exist")
            elif thread.get_creater() != username:
                conn.send(b"NU")
                print("removing failed, you are not the owner of the thread")
            else:
                conn.send(b"OK")
                for file in os.listdir():
                    if file == t_name or re.search("^" + t_name + "-", file) != None:
                        os.remove(file)
                print("thread {} is removed".format(t_name))
        elif comm.split()[0] == "XIT":
            conn.close()
            with lock:
                clients.remove(username)
            print("{} exited".format(username))
            break
        elif comm.split()[0] == "LST":
           
            if len(thread_titles) == 0:
                conn.send(b"NO")
                
            else:
                conn.send(b"OK")
                with open(".threads_names", "w") as f:
                    for t in thread_titles:
                        f.write(t + "\n")

                l = os.path.getsize(".threads_names")
                conn.send(byte_number_converter(l, 1))
                with open(".threads_names", "rb") as f:
                    line = f.read(1024)
                    while line:
                        conn.send(line)
                        line = f.read(1024)
                os.remove(".threads_names")
        elif comm.split()[0] == "SHT":
            if comm.split()[1] == admin_passwd:
                conn.send(b"OK")
                print("server shuts down")
                clear_forum()
                serverSocket.close()
                
            else:
                print("SHT failed: wrong admin password")
                conn.send(b"NO")




if __name__ == "__main__":

    threads = []
    thread_titles = []
    clear_forum()
    Thread_Counter = 0
    clients = [] #list of active clients' username

    lock = threading.Lock()

    #get port
    server_port = int(sys.argv[1])
    #get admin password
    admin_passwd = sys.argv[2]
    #create TCP socket 
    serverSocket = socket(AF_INET, SOCK_STREAM)
    #assign the server port with the given port number 
    try:
        serverSocket.bind(('localhost', server_port))
    except:
        print("port is already occupied")
        sys.exit()

    serverSocket.listen(1)
    print("Waiting for clients")
    while(1):
        try:
            conn, addr = serverSocket.accept()
        except:
            break    
        identity = conn.recv(2)
        if identity == b"CL":
            print("Client connected")
            client_thread = threading.Thread(target=new_thread_client, args=(conn,))
            client_thread.setDaemon(True)
            client_thread.start()
        

        
        
                


       




