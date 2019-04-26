
# ec2_address = "ec2-54-200-214-28.us-west-2.compute.amazonaws.com"
ec2_address = "ec2-3-19-63-10.us-east-2.compute.amazonaws.com"

# key_file = ".AWSkp/r0mer0mOregon.pem"
key_file = "./deepVision.pem"

user = "ec2-user"

# without /
git_repo_name = "product-analytics-group-project-deepvision"
git_user_id = "MSDS698"  # repo creator


def git_credentials():
    git_user = input('Input your git user:\n')
    return git_user
