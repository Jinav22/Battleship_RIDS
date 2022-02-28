from github import Github
from github import InputGitAuthor


author = InputGitAuthor(
        "Jinav",
        "jinavgala@gmail.com"
    )


def github_setup(TOKEN, file_path):
    g = Github(TOKEN) # PERSONAL ACCESS TOKEN
    repo = g.get_repo(file_path)
    return repo


def update_github_file(repo, file_name, update):
    file = repo.get_contents(file_name)
    data = file.decoded_content.decode("utf-8") # Get raw string data
    message = str(len(data.split('\n')))
    data += ( '\n' + message + "," + update)
    # print(data, len(data))
    return data, message


def push(repo, file_name, message, content):
    global author
    contents = repo.get_contents(file_name)  # Retrieve old file to get its SHA and path
    repo.update_file(contents.path, message, content, contents.sha, author=author)  # Add, commit and push branch



'''
def update_and_push(TOKEN, file_path, file_name, update):
    repos = github_setup(TOKEN, file_path)
    updated_data, message = update_github_file(repos, file_name, update)
    push(repos, file_name, message, updated_data)
'''

