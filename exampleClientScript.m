clear all;
sock = tcpclient("localhost",50007)
frameCommand = [115,0,0,0]; %definition frame; the meaning of the codes is described in the article
write(sock,frameCommand,'uint32'); %send frame
ackErrorFrame = read(sock,4,'uint32'); %reading the code of the frame sent by the server
if ackErrorFrame(1)==300 
    disp("Tracker not connected");
elseif ackErrorFrame(1)==210
    disp("Connected to the tracker. Stationary profile is set")
elseif ackErrorFrame(1)==310
    disp("Bad command")
elseif ackErrorFrame(1)==301
    disp("The client is not root") %only the first connected client can issue commands to the tracker.
    %if there is one client, it doesn't matter
end

%definition and send frame; the meaning of the codes is described in the article
frameCommand = [110,0,0,0];
write(sock,frameCommand,'int32'); 
 

%----------------------------------------------------
%reading data for retroreflector  (only position)
%----------------------------------------------------
%reading the frame sent by the server

ackErrorFrame = read(sock,4,'int32');
if ackErrorFrame(1)==210
    gainPoz=1000.0;
    X=double(ackErrorFrame(2))/gainPoz
    Y=double(ackErrorFrame(3))/gainPoz
    Z=double(ackErrorFrame(4))/gainPoz
 
elseif ackErrorFrame(1)==313
    disp("Bad command")
elseif ackErrorFrame(1)==301
    disp("The client is not root")
end

%end of measurement
frameCommand = [112,0,0,0]; 
write(sock,frameCommand,'int32'); 
ackErrorFrame = read(sock,4,'int32');
disp(ackErrorFrame) %if correct ackErrorFrame(1)==212
%close connection
clear sock