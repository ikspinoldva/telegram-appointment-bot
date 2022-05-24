Telegram bot for booking sessions.
2 interfaces: for administrator and for clients.
The administrator adds sessions and clients can reserve them.

API_TOKEN - API token of the bot

ADMIN_ID - Telegram account ID, which will have administrator rights 
(to add, delete and book unlimited number of sessions, other users can 
only book 1 session from their account). The administrator can also 
change prices for services, address and information about themselves.

Technology Stack:
- Async library to work with TelegramAPI
- Sqlite 3.
- Docker. 

SQLite database will lie in the project folder db/appointment.db.
