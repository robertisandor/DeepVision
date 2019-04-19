ec2_address = "ec2-18-204-196-209.compute-1.amazonaws.com"
# ec2_address = "ec2-52-15-162-15.us-east-2.compute.amazonaws.com"

key_file = "./deepvision.pem"
# key_file = "./deepVision.pem"

user = "ec2-user"

# without /
git_repo_name = "product-analytics-group-project-deepvision"
git_user_id = "MSDS698"  # repo creator


def git_credentials():
    git_user = input('Input your git user:\n')
    return git_user
