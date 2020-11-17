#Nian Li comp3331 assignment Nov 2020
import sys
from socket import *
import os
import re

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

    def delete_msg(self, number, username):
        print(self.messages)
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
    
    def edit_msg(self, number, message):
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
        if self.title + "-" + file_name in os.listdir():
            print("uploading failed, file {} already exists in thread {}".format(file_name, self.title))
            conn.sendall("uploading failed, file {} already exists in thread {}".format(file_name, self.title).encode()) 
        else:
            print("{} uploaded file {} to {} thread".format(username, file_name, self.title))
            conn.sendall("{} uploaded to {} thread".format(file_name, self.title).encode())
            self.messages.append("{} uploaded {}".format(username, file_name) + "\n")
            with open(self.title, "a") as f:
                f.write("{} uploaded {}".format(username, file_name) + "\n")
    

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

def initialize_forum():
    global threads
    for file in os.listdir():
        if file != "client.py" and file != "server.py" and file != "credentials.txt":
            os.remove(file)
            '''
            with open(file, "r") as f:
                #the line below is cited from stackoverflow
                #credit: mick barry
                #https://stackoverflow.com/questions/7167008/efficiently-finding-the-last-line-in-a-text-file
                lines = f.read().splitlines()
                creater = lines[0]
                if len(lines) == 1:
                    counter = 0
                else:
                    counter = lines[-1].split()[0]
            t = Thread(lines[0], file, counter)
            threads.append(t)
            thread_titles.append(t.get_title())
            '''

#check username and password, and return true and false
def check_credetial(username, password):
    f = open("credentials.txt", "r")
    for line in f:
        if line.split()[0] == username and line.split()[1] == password:
            return True
    f.close() 
    return False

#create a new file, write user's name and return True
#otherwise return False
def create_thread (username, title):
    global threads
    if title in map(Thread.get_title, threads):
        print("Thread {} exists".format(comm.split()[1]))
        conn.sendall("Thread {} exists".format(title).encode())
    else:
        with open(title, "x") as f:
            f.write(username + "\n")
        new_thread = Thread(username, title, 0)   
        threads.append(new_thread)
        thread_titles.append(new_thread.get_title())
        print("Thread {} created".format(title))
        conn.sendall("Thread {} created".format(title).encode())


def post_message (username, title, message):
    thread = find_thread(title)
    if thread != False:#thread exist, add message 
        thread.add_msg(username, message)
        print("Message {} posted to {} thread".format(message, title))
        conn.sendall("Message {} posted to {} thread".format(message, title).encode())
    else:#send error when thread doesn't exist
        print("post failed, {} thread doesn't exist".format(title))
        conn.sendall("post failed, {} thread doesn't exist".format(title).encode())

def delete_message (username, title, n_msg):
    thread = find_thread(title)
    if thread == False:
        print("deleting failed, {} thread doesn't exist".format(title))
        conn.sendall("deleting failed, {} thread doesn't exist".format(title).encode())
    elif thread.get_creater() != username:
        print("deleting rejected, {} is not the creater of message {}".format(username, title))
        conn.sendall("deleting rejected, {} is not the creater of message {}".format(username, title).encode())
    else:
        thread.delete_msg(n_msg, username)

def edit_message(username, title, n_msg, message):
    thread = find_thread(title)
    if thread == False:
        print("editing failed, {} thread doesn't exist".format(title))
        conn.sendall("editing failed, {} thread doesn't exist".format(title).encode())
    elif thread.get_creater() != username:
        print("editing rejected, {} is not the creater of message {}".format(username, title))
        conn.sendall("editing rejected, {} is not the creater of message {}".format(username, title).encode())
    else:
        thread.edit_msg(n_msg, message)

def read_thread(title):
    thread = find_thread(title)
    if thread == False:
        print("reading failed, {} thread doesn't exist".format(title))
        conn.send(b"fail")
    else:
        conn.send(b"R") #tell the client to get ready to revice content in the thread
        with open(title, "rb") as f:
            line = f.read(1024)
            while line:
                conn.send(line)
                line = f.read(1024)
        conn.send(b"finish")        
            



def upload_file(username, title, filename):
    thread = find_thread(title)
    if thread == False:
        print("uploading failed, {} thread doesn't exist".format(title))
        conn.sendall("uploading failed, {} thread doesn't exist".format(title).encode())
    else:

        with open(title + "-" + filename, "wb") as f:
            while (1):
                line = conn.recv(1024)
                if line == b"finish":
                    print("finish")
                    break
                f.write(line)

        thread.add_file(filename, username)
        conn.sendall("uploading finish".encode())








    







if __name__ == "__main__":
    
    threads = []
    thread_titles = []
    initialize_forum()


    #get port
    server_port = int(sys.argv[1])
    #get admin password
    admin_passwd = sys.argv[2]
    #create TCP socket 
    serverSocket = socket(AF_INET, SOCK_STREAM)
    #assign the server port with the given port number 
    serverSocket.bind(('localhost', server_port))

    serverSocket.listen(1)
    print("Waiting for clients")
   

    conn, addr = serverSocket.accept()

        
    print("Client connected")
    #recive username and password
    username = conn.recv(1024).decode("utf-8")
    password = conn.recv(1024).decode("utf-8")
    
    #check password and username
    while not check_credetial(username, password):
        print("Incorrect password")
        conn.sendall("Invalid password".encode())
        username = conn.recv(1024).decode("utf-8")
        password = conn.recv(1024).decode("utf-8")
    
    conn.sendall("Welcome to the forum".encode())
    print("{} successful login".format(username))
    
    while True:
        comm = conn.recv(1024).decode("utf-8")
        if comm == '':
            break
        print("{} issued {} command".format(username, comm.split()[0]))
        if comm.split()[0] == "CRT":
            if len(comm.split()) == 2:
                create_thread(username,comm.split()[1])
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"CRT Thread\"".encode())

        elif comm.split()[0] == "MSG":
            if len(comm.split()) >= 3:
                post_message(username, comm.split()[1], ' '.join(comm.split()[2:]))   
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"MSG Thread Message\"".encode())   
            
        elif comm.split()[0] == "DLT":
            if len(comm.split()) == 3:
                delete_message(username, comm.split()[1], comm.split()[2])
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"DLT Thread MessageNumber\"".encode())

        elif comm.split()[0] == "EDT":
            if len(comm.split()) == 4:
                edit_message(username, comm.split()[1], comm.split()[2], comm.split()[3])
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"EDT Thread MessageNumber Message\"".encode())    

        elif comm.split()[0] == "LST":
            if len(comm.split()) == 1:
                if len(thread_titles) == 0:
                    conn.sendall("no active thread".encode())
                else:
                    conn.sendall(("The list of active threads:\n" + "\n".join(thread_titles)).encode())
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"LST\"".encode())

        elif comm.split()[0] == "UPD":
            if len(comm.split()) == 3:
                upload_file(username, comm.split()[1], comm.split()[2])
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"UPD title filename\"".encode())

        elif comm.split()[0] == "RDT":
            if len(comm.split()) == 2:
                read_thread(comm.split()[1])
            else:
                print("invalid parameter")
                conn.sendall("invalid parameter: Please follow the correct format \"RDT title\"".encode())

                            

       




