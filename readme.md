# TELEGRAM ASSISTANT


## Why i made this program?

It all started when i was trying to connect to my home PC with my cellphone via SSH. But with the dynamic ipv4 allways changing, i had to find a way to discover my PC's new IP address in order to remotely access it from anywhere. So i decided to subscribe to no-ip and create a free ddns. Unfortunetely i found out that no-ip doesn't change the target ip automatically in the free plan, so i decided to find another solution. That solution was writing a telegram assistant. Since it's turned on, it answers what my home pc's IP is. I wrote an "take note" feature as well.

## How to use it?

First you are going to create the telegram robot. You can easily do it talking to a bot in Telegram called "The bot father". I recomend you to go to the Telegram's API docs to do take a better look of how to do it. Then you have to make, make an .env file containing the telegram token and the API key. Then you have to discover what your chat id is. To do it you just have to run the bot and send "chat id" to him. It will answer. Put a chat id variable in your .env file so the bot will know what's the admin's chat id. Then create another .env variable with a utf-8 encoded sha-256 hash. It will be your password for when you're asking your ip address from another telegram account. Now you can freely use your assistant.

###### Disclaimer:

I don't reccomend using this assistant to keep sensitive information since i didn't really focused on the security features. It was made only for personal purposes.
