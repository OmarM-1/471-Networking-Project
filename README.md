# 471-Networking-Project
## Multi-Client FTP Socket Program
Names and email addresses of all
- Omar Montes | 621omontes@csu.fullerton.edu

- Batu Demirtaş batudemirtas@csu.fullerton.edu

- Swayam Shree | sswayam@csu.fullerton.edu

- Ian Martines | b.ianmartinez98@csu.fullerton.edu

- Kiara Guerra | kguerra3411@csu.fullerton.edu

  
The programming language you use (e.g. C++, Java, or Python)
- Python
  
## PREREQS
- Python installed
- all files downloaded in same folder/directory

## To Run: 
### **ON MacOS**: 
1. Make sure all files are downloaded and in a trusted folder
2. open multiple terminals (if 3 chats needed open 4)
3. In each terminal, locate the directory in which all files are in
   - example: `cd /Users/Desktop/myTrustedFile`
4. Run the server file with the following code in the first terminal to open the server port:
   - `python3 server.py`
5. Run the client on each of the other terminals:
   - `python3 client.py`
6. Once logged in, it should prompt for a display name like so:
   - `Enter your name: `
7. Once name has been entered you can send and recieve messages
   - if you are logged in on one terminal 1 and run the client.py on terminal 2 and enter your name the following will show on terminal 1:
   - $${\color{red}X \space \color{red}has \space \color{red}joined \space \color{red}the \space \color{red}chat.}$$

### **ON WINDOWS**: 
1. Make sure all files are downloaded and in a trusted folder
2. Open multiple Command Prompt or PowerShell windows (if 3 chats needed open 4)
3. In each terminal, locate the directory in which all files are in
   - example: `cd C:\project\path\Desktop\myTrustedFile`
4. Run the server file with the following code in the first terminal to open the server port:
   - `python server.py`
5. Run the client on each of the other terminals:
   - `python client.py`
6. Once logged in, it should prompt for a display name like so:
   - `Enter your name: `
7. Once name has been entered you can send and recieve messages
   - if you are logged in on one terminal 1 and run the client.py on terminal 2 and enter your name the following will show on terminal 1:
   - $${\color{red}X \space \color{red}has \space \color{red}joined \space \color{red}the \space \color{red}chat.}$$
## 
You can now message in the terminal to other terminals

### Using FTP Functionality
- ***Important commands:*** $${\color{blue}CLIENT \space TERMINAL \space ONLY}$$
  - **/get** ~ Downloads file from the server folder to client folder
    - *desired files to retrieve must be in the server folder*
  - **/put** ~ Adds file from client folder to server folder
    - *desired files to share must be in the client folder* 
  - **/ls** ~ shows list of all files in server folder available to retrieve
  - **/exit** ~ Removes self from server and notifies others that you have left the chat
 

