from dotenv import load_dotenv
from os import getenv
import requests
import praw
# import pprint


load_dotenv()

reddit = praw.Reddit(
    client_id=getenv("CLIENT_ID"),
    client_secret=getenv("CLIENT_SECRET"),
    refresh_token=getenv("REFRESH_TOKEN"),
    user_agent=getenv("USER_AGENT"),
)

# Find out what posts are already on the website so we don't perform
# unnecessary requests
response = requests.get(
    getenv("BASE_URL") +
    "/api/posts/",
    auth=(getenv("USER_USERNAME"), getenv("USER_PASSWORD"))
    )

post_ids = []
for post in response.json()["results"]:
    post_ids.append(post["id"])


subreddit: praw.reddit.Subreddit = reddit.subreddit("transplace")
for submission in subreddit.stream.submissions():
    # In case I ever need to figure out
    # all the properties a submission has
    # ["images"][0]["resolutions"][-1]["url"]
    # pprint.pprint(vars(submission))

    if submission.archived:
        print(submission.title, "ARCHIVED")
        continue
    
    if submission.id in post_ids:
        print("In site already")
        continue

    data = {
        "id": submission.id,
        "title": submission.title,
        "content": None,
        "message_type": "User Content",
        "reddit_url": submission.shortlink,
        "owner_id": 1,
    }

    # If the post is an image post
    # We have to do it this way bc PRAW does funny stuff
    try:

        if submission.preview["enabled"]:
            print(submission.title, "IMAGE")

            data["file_url"] = submission.url

        if "video" in submission.post_hint:
            data["file_url"] = submission.preview["images"][0]["resolutions"][-1]["url"]

    except BaseException as e:
        print(e)
    
    post_ids.append(submission.id)

    requests.post(
        getenv("BASE_URL") +
        "/api/posts/",
        data=data,
        auth=(getenv("USER_USERNAME"), getenv("USER_PASSWORD"))
    )

print(post_ids)