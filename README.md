# Coffee Keeper
### The inspiration
*Andrea: "These prices are way too high, f-cking coffee machines."  
Francesco: "Yeah, Polimi should do something. We should just bring our own coffee from home."  
Angelo: "Capsules cost way less if you buy them yourself."  
Franceso: "Definitely.  
Andrea: "Why don't we buy a coffee machine?"  
Angelo: "Ahahah."  
Andrea: "No, I mean, seriously."  
Francesco: "Aight, but how are we doing it? We can't just bring it over every day from home."  
Angelo: "We can find a locker with a power outlet close to it."  
Andrea: "Exactly."  
Francesco: "Everyone brings his own capsules? Seems messy, every coffee machine has his own capusles supported."  
Angelo: "What if one of us buys a big pack of them and we divide them?"  
Francesco: "I don't want capsules in my backpack."  
Andrea: "Let's just leave them grouped in their box, in the locker with the coffee machine."  
Francesco: "**And how do we know how many capsules each one of us has left?***"  

<br>

### What is it?
Coffee Keeper is a telegram bot able to monitor the count of coffee capsules used by uni students. Works in group chats, allows users to edit their amounts by using commands.  

<br>

### How does it work?
Basically, I decided to do everything I could to not pay a single cent for this. Telegram manages to contact my bot through webhook, which triggers an AWS Lambda that parses the message sent,
eventually communicating with some DynamoDB tables to store data between executions.
