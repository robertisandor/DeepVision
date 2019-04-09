from getpass import getpass


ec2_address = "ec2-52-42-97-222.us-west-2.compute.amazonaws.com"

key_file = "/.AWSkp/r0mer0mOregon.pem"

user = "ec2-user"

git_repo_name = "product-analytics-group-project-deepvision"
git_user_id = "MSDS698"  # repo creator


def git_credentials():
    git_user = input('Input your git user:\n')
    return git_user
