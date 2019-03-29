from getpass import getpass


ec2_address = "ec2-3-80-157-90.compute-1.amazonaws.com"

key_file = "/Documents/Keys/msds697.pem"

apikey = "AIzaSyCY-x0Jk5rsVnP8w-Ozn3YwzUmK6nUcvHU"

user = "ec2-user"

git_repo_name = "product-analytics-group-project-deepvision"
git_user_id = "MSDS698"  # repo creator

orig_coord = '37.7909,-122.3925'
dest_coord = '37.7765,-122.4506'
output_file_name = 'output.txt'


def git_credentials():
    git_user = input('Input your git user:\n')
    git_password = getpass('Input your git password:\n')
    return git_user, git_password
