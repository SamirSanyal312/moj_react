-- users table
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    nickname TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    joke_balance INTEGER DEFAULT 0,
    role TEXT DEFAULT 'user' 
);

-- jokes table
CREATE TABLE IF NOT EXISTS joke (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES user (id),
    UNIQUE (title, author_id)
);

-- joke ratings
CREATE TABLE IF NOT EXISTS rating (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    joke_id INTEGER NOT NULL,
    score INTEGER NOT NULL CHECK(score BETWEEN 1 AND 5),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (joke_id) REFERENCES joke (id),
    UNIQUE (user_id, joke_id)
);

-- joke views
CREATE TABLE IF NOT EXISTS joke_view (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    joke_id INTEGER NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (user_id, joke_id)
);

CREATE TABLE IF NOT EXISTS joke (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (author_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS taken_jokes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    joke_id INTEGER NOT NULL,
    UNIQUE (user_id, joke_id),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (joke_id) REFERENCES joke (id)
);

CREATE TABLE IF NOT EXISTS ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    joke_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (joke_id) REFERENCES joke (id),
    UNIQUE(user_id, joke_id)
);

CREATE TABLE IF NOT EXISTS taken_jokes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    joke_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id),
    FOREIGN KEY (joke_id) REFERENCES joke (id),
    UNIQUE(user_id, joke_id)
);


