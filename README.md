# 471-Networking-Project
## Multi-Client FTP Socket Program
Names and email addresses of all
- Omar Montes | 621omontes@csu.fullerton.edu

- Batu Demirtaş batudemirtas@csu.fullerton.edu

- Swayam Shree | sswayam@csu.fullerton.edu

- Ian Martines | b.ianmartinez98@csu.fullerton.edu

The programming language you use (e.g. C++, Java, or Python)
- Python

### To Run: 
ON MAC: 
1. Make sure all files are downloaded and in a trusted folder
2. open multiple terminals (if 3 chats needed open 4)
3. In each terminal, locate the directory in which all files are in
   - example: `/Users/Desktop/myTrustedFile`
4. Run the server file with the following code in the first terminal to open the server port
   - `python3 server.py`
5. Run the client on each of the other terminals
   - `python3 client.py`
6. Once logged in, it should prompt for a name like so:
   - `Enter your name: `
7. Once name has been entered you can send and recieve messages
   - if you are logged in on one terminal 1 and run the client.py on terminal 2 and enter your name the following will show on terminal 1:
   - $${\color{red}X \space \color{red}has \space \color{red}joined \space \color{red}the \space \color{red}chat.}$$

ON WINDOWS: 
 - Same steps as MAC but use:
    - `python server.py`
    - `python client.py`



Add this part if we do FTP: 
- ***Important commands***
  - **/get** ~ Downloads file from the server folder to client folder
  - **/put** ~ Adds file from client folder to server folder
  - **/ls** ~ shows list of all files in server folder available
