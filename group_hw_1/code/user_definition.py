from getpass import getpass


ec2_address = "ec2-54-201-196-51.us-west-2.compute.amazonaws.com"

key_file = "/.AWSkp/r0mer0mOregon.pem"

apikey = "sdfgjlkdfasdfasdffasdfsdf"

user = "ec2-user"

git_repo_name = "product-analytics-group-project-deepvision"
git_user_id = "MSDS698" # repo creator

orig_coord = '37.7909,-122.3925'
dest_coord = '37.7765,-122.4506'
output_file_name = 'output.txt'


git_user = input('Input your git user:\n')
git_password = getpass('Input your git password:\n')
