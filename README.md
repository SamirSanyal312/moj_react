# Master of Jokes

Master of Jokes is a Flask-based web application that lets users share, view, and rate jokes in a unique exchange system inspired by the concept:

> _"Have a penny, leave a penny. Need a penny, take a penny."_

Users earn joke credits by contributing jokes and spend them to view jokes submitted by others.

## 🚀 Features

- 🔐 **User Authentication**
- 📝 **Leave a Joke**
- 📚 **My Jokes**
- 😂 **Take a Joke**
- ⭐ **Rate Jokes**
- 🛡 **Moderator Role**
- 📑 **Logging System**

## 🧪 How to Run (Dev Mode)

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database and run the app:

   ```bash
   flask --app app init-db
   flask --app app run --debug
   ```

   Visit `http://127.0.0.1:5500` in your browser.

## 🐳 Deploy with Docker

1. Clone the repository:

   ```bash
   git clone https://github.iu.edu/SE-Team-6/master-of-jokes.git
   cd master-of-jokes
   ```

2. Build the Docker image:

   ```bash
   docker build -t master-of-jokes .
   ```

3. Run the container:

   ```bash
   docker run -P master-of-jokes
   ```

   Access the app at: `http://127.0.0.1:5500`

### 🛠 For existing local DBs:

Run this SQL command if you already have `moj.sqlite`:

````sql
ALTER TABLE user ADD COLUMN role TEXT DEFAULT 'user';

## 🛠 Moderator Initialization (MoJ 2.0)

To create the initial moderator user, use the following custom Flask CLI command. This is required for setting up role-based access control in MoJ 2.0.

### 📋 Usage

Run this command from the root of your project (with your virtual environment activated):

```bash
flask --app moj create-moderator <email> <nickname> <password>
````

## 📝 React Frontend (Status Reporting)
If using the optional React status dashboard:

```bash
npx create-react-app moj-status-report

cd moj-status-report

npm install axios

npm start
```
