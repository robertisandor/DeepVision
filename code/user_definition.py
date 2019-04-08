from getpass import getpass


ec2_address = "ec2-35-162-133-15.us-west-2.compute.amazonaws.com"

key_file = "/.AWSkp/r0mer0mOregon.pem"

apikey = "AIzaSyCY-x0Jk5rsVnP8w-Ozn3YwzUmK6nUcvHU"

user = "ec2-user"

git_repo_name = "product-analytics-group-project-deepvision"
git_user_id = "MSDS698"  # repo creator


def git_credentials():
    git_user = input('Input your git user:\n')
    # git_password = getpass('Input your git password:\n')
    return git_user#, git_password
