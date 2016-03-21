# GusPIRC-IRC-Interface
The decent, simple, low-level, socket-based and event-driven IRC interface in Python.

To connect to IRC, all you have to do is to do a IRCConnector object and use the function
addSocketConnection() to add a connection to the server!

Then, parse all the messages received by receiveAllMessages() or just the latest one which
is returned by receiveLatestMessage()!
