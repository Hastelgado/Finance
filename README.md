# Finance

A simple finance/stock quotes application that's built on the Python Flask framework. You have the ability to quote, buy, and sell stocks using IEX's data API, as well as look at your purchase history. The database used is SQLite built off of CS50's SQLAlchemy library.

# What I learned

* Basic web development using the Flask framework.
* Building a simple relational database with tables between Users and Stocks.
* Using a Web API to parse JSON data to my app.
* Using flask sessions.

# Configuring your own API key
Before getting started, we’ll need to register for an API key in order to be able to query IEX’s data. To do so, follow these steps:

1. Visit iexcloud.io/cloud-login#/register/.
2. Select the “Individual” account type, then enter your name, email address, and a password, and click “Create account”.
3. Once registered, scroll down to “Get started for free” and click “Select Start plan” to choose the free plan.
4. Once you’ve confirmed your account via a confirmation email, visit https://iexcloud.io/console/tokens.
5. Copy the key that appears under the Token column (it should begin with pk_).
6. In your terminal window, execute:
7. $ export API_KEY=value
Where value is that (pasted) value, without any space immediately before or after the =. You also may wish to paste that value in a text document somewhere, in case you need it again later.

# Configuring a Virtual Environment for the needed packages

1. Run "python -m venv venv", and click "yes" if prompted by your editor if you wish to use this Venv for the current workspace folder.
2. Run "pip install -r requirements.txt" to install the necessary packages.

# Running the app

To run the app, simply start Flask’s built-in web server (within your work folder):
"flask run"
### Note: The app won't start if you haven't exported the necessary API key from IEX into the code OS environment.
