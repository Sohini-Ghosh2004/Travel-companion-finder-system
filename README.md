# Travel Companion Finder System

A web application that helps users find compatible travel partners, join travel groups, and communicate through chat. The system uses a hybrid recommendation model to match users based on preferences, behavior, and location.

---

## Overview

Planning trips with suitable companions is often difficult due to differences in interests, budget, and travel style. This system addresses that problem by analyzing user profiles and recommending the most compatible users.


The system is built using Flask and MySQL, with an integrated machine learning model for recommending users based on multiple factors:

- User profile similarity (content-based)
- User interaction patterns (collaborative filtering)
- Geographic proximity
- Clustering (K-Means)

The backend exposes REST APIs for authentication, user management, group management, chat, and recommendations.

---

## Features

### 1. User Management
- Create account
- Update profile
- Delete account
- View profile

### 2. Authentication
- JWT-based authentication
- Login / Logout
- Token blacklisting

### 3. Group System
- Create travel groups
- Join groups (with approval system)
- Accept / Reject join requests
- Leave group
- Delete group (admin only)
- Group listing with metadata

### 4. Chat System
- Private messaging
- Group chat
- Unread message tracking
- Mark messages as read

### 5. Recommendation System
- Hybrid recommendation engine
- Suggests users with similar travel interests
- Suggests groups with similar travel interests

---

## Recommendation Model

The recommendation system combines multiple techniques:

### Content-Based Filtering
Uses user profile features:
- Age
- Budget
- Travel preferences (beach, trekking, culture, adventure)
- Travel month

Similarity is computed using cosine similarity.

### Collaborative Filtering
- Uses user–POI rating matrix
- Computes similarity between users based on ratings

### Geographic Similarity
- Based on latitude and longitude
- Uses geodesic distance

### Clustering
- K-Means clustering groups similar users
- Adds cluster-based similarity boost

### Final Score

The final recommendation score is computed as:


`final_score` = `w_content * content_score` + `w_cf * cf_score` + `w_geo * geo_score` + `0.1 * cluster_score`


Weights (`w_content`, `w_cf`, `w_geo`) are dynamically computed based on the variance of their respective similarity scores, allowing the model to adaptively prioritize the most informative component.


## Tech Stack

- Python
- Flask
- MySQL
- Pandas / NumPy
- Scikit-learn
- Geopy(Nominatim - OpenStreetMap)
- JWT Authentication

---

## Environment Variables

Create a `.env` file:

```env
DB_HOST=your_host
DB_USER=your_user
DB_PASSWD=your_password
DB=your_database
JWT_SECRET=your_secret_key
OPENTRIPMAP_KEY=your_api_key
```


---

## API Endpoints

### Account
- `POST /api/create-account`
- `PUT /api/update-account`
- `DELETE /api/delete-account`
- `GET /api/profile`

### Auth
- `POST /api/login`
- `GET /api/logout`

### Groups
- `GET /api/groups`
- `POST /api/create-group`
- `POST /api/join-group`
- `PUT /api/update-group`
- `DELETE /api/delete-group`
- `POST /api/group/allow`
- `POST /api/group/reject`
- `POST /api/group/leave`
- `GET /api/group/requests`

### Chat
- `POST /api/chat/send`
- `GET /api/chat/messages`
- `GET /api/chat/unread`
- `POST /api/chat/read`
- `POST /api/group/chat/send`
- `GET /api/group/chat`

### Recommendation
- `POST /api/recommend/user`
- `GET /api/recommend/group`

---

## How to Run

1. Create an `.env` file in the `/backend` and add the required [environment variables](#environment-variables)  

2. Set your credentials in `docker-compose.yml` 
    
```sh
# set creds
environment:
MYSQL_ROOT_PASSWORD: "1234!"
MYSQL_DATABASE: travel
MYSQL_USER: user
MYSQL_PASSWORD: "1234!"
    
# pass
healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h localhost -u root -p1234! || exit 1"]
```  

2. Start the Containers:  

```sh
# build and start the containers
docker-compose up -d --build
```  

3. Stop the Containers:  

```sh
# stops and removes the containers and networks
docker-compose down -v
```  

4. Server runs on:  
    - Frontend: `http://localhost`
    - Backend: `http://localhost:5000`


### Develope backend

<b>env</b>

```sh
# env
python3 -m venv venv

source venv/bin/activate

pip3 install -r requirements.txt
```  

<b>database</b>

```sh 
# set your own creds
mysql -u $username -p < main.sql
```

<b>run</b>

```sh
python3 app.py
```  

Docs: [swagger](docs/swagger.yml)  
Test: [postman](docs/postman_collection.json)  


## License

This project is licensed under the [MIT License](/LICENSE).
