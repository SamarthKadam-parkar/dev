from git import Repo


repo = Repo("C:/Users/samarth.kadam/Dev")

with open("contributions/commit_logs.txt", "w", encoding="utf-8") as file:
    
    file.write("--- LOCAL COMMIT HISTORY ---\n")

    for commit in repo.iter_commits(max_count=10):
        file.write(f"SHA: {commit.hexsha} | Author: {commit.author.name} | Msg: {commit.message.strip()} | Time: {commit.authored_datetime}\n")
