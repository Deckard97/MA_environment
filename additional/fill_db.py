import requests
import random
from faker import Faker

fake = Faker()
fake.seed_instance(0)

# Endpoint configuration
base_url = "http://vm-d69d62d7.test-server.ag"

# Define number of users
num_users = 10

# Store created users
created_users = []

def create_user():
    user_url = f"{base_url}/users"

    # Generate user data
    user_data = {
        "user": {
            "email": fake.email(),
            "password": "password",  # Using a constant password for all users
            "username": fake.user_name()
        }
    }

    # Send POST request to create user
    response = requests.post(user_url, json=user_data)
    if response.status_code == 201:
        print("User created:", user_data["user"]["username"])
        created_users.append(user_data["user"])
    else:
        print("Failed to create user. Status Code:", response.status_code)
        print("Response:", response.text)

def login_users():
    login_url = f"{base_url}/users/login"

    for user in created_users:
        # Log in the user
        login_payload = {"user": {"email": user["email"], "password": user["password"]}}
        response = requests.post(login_url, json=login_payload)
        
        if response.status_code != 200:
            print(f"Failed to log in user {user['username']}")
            continue

        # Extract the token from the response
        token = response.json()["user"]["token"]
        user['token'] = token

def create_articles():
    article_url = f"{base_url}/articles"

    for user in created_users:
        # Create an article
        article_payload = {
            "article": {
                "title": fake.sentence(),
                "description": fake.text(),
                "body": fake.text(),
                "tagList": [fake.word(), fake.word()]
            }
        }
        headers = {"Authorization": f"Token {user['token']}"}
        response = requests.post(article_url, json=article_payload, headers=headers)
        
        if response.status_code == 200:
            print(f"Article created successfully for user {user['username']}")
        else:
            print(f"Failed to create article for user {user['username']}")

def get_articles():
    articles_url = f"{base_url}/articles"
    articles_response = requests.get(articles_url)
    
    if articles_response.status_code != 200:
        print("Failed to fetch articles")
        return

    articles = articles_response.json().get("articles", [])
    return articles

def post_comments():
    articles_url = f"{base_url}/articles"
    articles_response = requests.get(articles_url)
    
    if articles_response.status_code != 200:
        print("Failed to fetch articles")
        return

    articles = articles_response.json().get("articles", [])
    
    if not articles:
        print("No articles found")
        return

    # Seed the random number generator for consistency
    random.seed(0)

    for user in created_users:
        # Pick a random article
        article = random.choice(articles)
        slug = article["slug"]
        token = user.get("token")

        if not token:
            print(f"User {user['username']} does not have a token, skipping...")
            continue

        # Post a comment to the random article
        comment_url = f"{base_url}/articles/{slug}/comments"
        headers = {"Authorization": f"Token {token}"}
        comment_body = {"comment": {"body": fake.sentence()}}
        
        response = requests.post(comment_url, json=comment_body, headers=headers)
        
        if response.status_code != 201:
            print(f"Failed to post comment for user {user['username']}")
            continue

        print(f"User {user['username']} posted a comment on article {slug}")

def favorite_articles():
    articles = get_articles()
    if not articles:
        print("No articles available to favorite")
        return
    
    for user in created_users:
        token = user.get("token")
        if not token:
            print(f"User {user['username']} is not logged in")
            continue
        
        # Pick a random article
        random_article = random.choice(articles)
        slug = random_article["slug"]
        
        # Construct the favorite article URL
        favorite_url = f"{base_url}/articles/{slug}/favorite"
        
        # Set up the headers
        headers = {"Authorization": f"Token {token}"}
        
        # Send the request to favorite the article
        response = requests.post(favorite_url, headers=headers)
        if response.status_code == 200:
            print(f"User {user['username']} favorited article {slug}")
        else:
            print(f"Failed to favorite article {slug} for user {user['username']}")


# Create users
for _ in range(num_users):
    create_user()

# Login users and save auth token
login_users()

# Create articles for users
create_articles()

# Do the commenting
post_comments()

# Do the favoriting
favorite_articles()