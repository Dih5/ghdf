"""ghdf - Download datasets from github"""

__version__ = '0.1.0'
__author__ = 'Dih5 <dihedralfive@gmail.com>'
__all__ = []

import pandas as pd

from github import Github

# TODO: Load from env
TOKEN = None


class iter_cutoff:
    def __init__(self, limit, gen):
        self.limit = limit
        self.gen = iter(gen)
        self.i = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.i < self.limit:
            self.i += 1
            return next(self.gen)

        raise StopIteration


def connect(token=None):
    global g
    g = Github(token if token is not None else TOKEN)


if TOKEN is None:
    print("No default token was set. Call connect(<token>) before using the package")
else:
    connect()


def _get_repo_info(a):
    return {"description": a.description,
            # "releases": len(list(a.get_releases())),
            "forks": a.forks_count,
            "stargazers": a.stargazers_count,
            "topics": list(a.get_topics()),
            "languages": list(a.get_languages()),
            # "comments": list(a.get_comments()),
            "full_name": a.full_name,
            "is_fork": a.fork,
            }


def get_repo_info(repo):
    """

    Args:
        repo str: Full name of the repo. E.g.: "numpy/numpy".

    Returns:

    """
    return pd.DataFrame([_get_repo_info(g.get_repo(repo))])


def get_user_repos(user, forks=True, cutoff=100):
    query = f"user:{user} fork:{'true' if forks else 'false'}"
    return pd.DataFrame(_get_repo_info(repo) for repo in
                        iter_cutoff(cutoff, g.search_repositories(query, sort="updated", order="desc")))


def _get_issue_info(i):
    return {"title": i.title,
            "body": i.body,
            "assignees": i.assignees,
            "comments": i.comments,
            "labels": [a.name for a in list(i.get_labels())],
            "pull_request": i.pull_request,
            "repository": i.repository.full_name,
            "url": i.url,
            "user": i.user.login
            }


def get_repo_issues(repo, only_open=True, cutoff=100):
    kwargs = {}
    if only_open:
        kwargs["state"] = "open"
    return pd.DataFrame(_get_issue_info(issue) for issue in iter_cutoff(cutoff, g.get_repo(repo).get_issues(**kwargs)))


def get_user_issues(user, cutoff=100):
    return pd.DataFrame(_get_issue_info(issue) for issue in iter_cutoff(cutoff, g.search_issues(f"user:{user}")))


def get_user_graph(user, max_depth=0):
    followers = {}
    following = {}
    to_search = {g.get_user(user)}
    next_search = set()

    depth = 0
    while depth <= max_depth:
        for user in list(to_search):
            user_name = user.login
            if user_name not in followers:  # not scrapped
                print("scrapping %s" % user_name)
                follower_list = list(user.get_followers()) if user.followers else []
                followers[user_name] = [f.login for f in follower_list]

                following_list = list(user.get_following()) if user.following else []
                following[user_name] = [f.login for f in following_list]

                next_search |= set(follower_list) | set(following_list)

        depth += 1
        to_search = next_search

    return followers, following, next_search


def to_edge_list(followers, following=None):
    if followers is None:
        followers = {}
    if following is None:
        following = {}
    # Paris of follower, followee
    output = sum([[(x, a) for x in b] for a, b in followers.items()], []) + sum(
        [[(a, x) for x in b] for a, b in following.items()], [])

    return list(set(output))
