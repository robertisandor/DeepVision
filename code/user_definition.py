ec2_address = "ec2-3-83-100-104.compute-1.amazonaws.com"

key_file = "/Documents/Keys/msds603.pem"

user = "ec2-user"

# without /
git_repo_name = "product-analytics-group-project-deepvision"
git_user_id = "MSDS698"  # repo creator


def git_credentials():
    git_user = input('Input your git user:\n')
    return git_user
