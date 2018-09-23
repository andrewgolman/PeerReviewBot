from github import Github, GithubException
import config

GH = Github(config.github_access_token)

class ApiException(Exception):
    pass

# gets rep name from url
def parseRepositoryFullName(repository_url):
    pos = repository_url.rfind("/")
    if pos == -1:
        raise ApiException
    pos = repository_url.rfind("/", 0, pos)
    if pos == -1:
        raise ApiException
    return repository_url[pos + 1:]

# returns issue number
def create_issue(reviewee, reviewer, task_name, repository_url):
    name = parseRepositoryFullName(repository_url)

    try:
        repo = GH.get_repo(name)
        issue = repo.create_issue("Review of " + reviewee + " by " + reviewer + " of task " + task_name)
    except GithubException:
        raise ApiException
    return issue.number

# issue number is that returned by create_issue
def issue_closed(repository_url, issue_number):
    name = parseRepositoryFullName(repository_url)
    if not name:
        return 1

    try:
        repo = GH.get_repo(name)
        issue = repo.get_issue(issue_number)
    except GithubException:
        raise ApiException
    return issue.state == "closed"