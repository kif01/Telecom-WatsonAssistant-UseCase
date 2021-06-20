# Usecase-POC
https://watson-etisalat-assistant.eu-gb.mybluemix.net/

## Description
The POC aims to assist users with their queries to know information about the offers and plans offered by the telecom company, and help users with their accounts and history transactions in the telecom company. Users can ask about their transaction history, smiles balance, account information, offers and plans by the telecom company. In addition, this assistant handles multi-intents and automatically run them sequentially. 

## Technology
- Watson Assistant
- Watson Discovery
- IBM Cloud Functions
- Cloud Object Storage

## Main Topics To Ask About
- Smiles Balance
- Transactions History
- Profile Update
- Mobile Plans

## Main Features
- Multi-intents : if a user asks for different things in his same input, the assistant answers all of them sequentially (i.e. if a user asks about his smiles, transactions and plans then the assistant will respond to all of these 3 intents automatically in a sequence way)
- Authentication: When a user asks about his account, smiles balance or transactions, he will be asked to put his account number and OTP (The authentication process takes part in a cloud function).
- Mobile plans data are being extracted from Watson Discovery and automatically generated to the assistant (using another cloud function with python SDK for Watson Assistant) to update the entity regarding the plans and to update the option values of the Plan/Services Node in the dialogue flow. This same funcion creates as well a CSV file with all the extracted data so the assistant can read from whenever a user chooses a plan to know more about.
- ChitChat: User can chitchat with the assistant and ask for jokes for example. Once 3 chitchats intents are consecutively asked, then the assistant ends the chat.

## Architecture Diagram
![image](https://media.github.ibm.com/user/265755/files/82d24100-ad8e-11ea-91c9-6d0aefc36d81)
<br>
1- User can interact with the assistant through web or mobile application.<br>
2- The application calls Watson Assistant that is hosted on IBM Cloud.<br>
3- Watson Assistant makes calls to Cloud Functions to extract information to answer user queries.<br>
4- Cloud Functions periodically calls Discovery to extract information from webpages.<br>
5- Crawling information about plans and offers from the telecom company's HTML webages using Smart Document Understanding on Discovery.<br>
6- Cloud Functions saves the plans and offers in Cloud Object Storage and retrieves information about users and plans when they are requested.<br>

## Screenshots
<img width="1440" alt="Screen Shot 2020-06-15 at 3 34 16 AM" src="https://media.github.ibm.com/user/273026/files/70085b00-aeb9-11ea-8c51-695f8ffa05be">
<img width="1440" alt="Screen Shot 2020-06-15 at 3 35 05 AM" src="https://media.github.ibm.com/user/273026/files/cc6b7a80-aeb9-11ea-99dd-27f064dcc78b">
