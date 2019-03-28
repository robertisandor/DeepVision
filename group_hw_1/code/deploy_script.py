import paramiko
from os.path import expanduser
from user_definition import *


def ssh_client():
    """Return ssh client object"""
    return paramiko.SSHClient()


def ssh_connection(ssh, ec2_address, user, key_file):
    """
    Establish an ssh connection.

    :param ssh: paramiko.SSHClient class
    :param ec2_address: (str) ec2 instance address
    :param user: (str) ssh username
    :param key_file: (str) location of the AWS
                     key from the root directory
    :return: None
    """
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ec2_address, username=user,
                key_filename=expanduser("~") + key_file)
    return ssh


def git_clone_pull(ssh, git_user_id, git_repo_name):
    """
    Clone/Updates 'git_repo_name' repository.

    :param ssh: paramiko.SSHClient class
    :return: None
    """
    stdin, stdout, stderr = ssh.exec_command("git --version")


    stdin, stdout, stderr = ssh.exec_command("git config --global credential.helper store")

    # Try cloning the repo
    if (b"" is stderr.read()):
        git_clone_command = f"git clone https://{git_user}:{git_password}@github.com/" + \
                            git_user_id + "/" + git_repo_name + ".git"

        stdin, stdout, stderr = ssh.exec_command(git_clone_command)
        # print(stdout.read())
        # print(stderr.read())

    # Pull if already exists
    if (b'already exists' in stderr.read()):
        git_pull_command = f"cd {git_repo_name} ; git pull"
        stdin, stdout, stderr = ssh.exec_command(git_pull_command)
        #
        # print(stdout.read())
        # print(stderr.read())


def create_or_update_environment(ssh, git_repo_name):
    """
    Creates/update python environment with the repo's .yaml file.

    :param ssh: paramiko.SSHClient class
    :return: None
    """
    stdin, stdout, stderr = ssh.exec_command(f"conda update conda")
    print(stdout.read())
    print(stderr.read())

    repo_path = 'group_hw_1/code/'

    stdin, stdout, stderr = ssh.exec_command(f"conda env create -f \
    ~/{git_repo_name}/{repo_path}environment.yml")
    print(stdout.read())
    print(stderr.read())
    if (b'already exists' in stderr.read()):
        stdin, stdout, stderr = ssh.exec_command(f"conda env update \
        -f ~/{git_repo_name}/{repo_path}environment.yml")
        print(stdout.read())
        print(stderr.read())


def set_crontab(ssh, time_code='* * * * *'):
    """
    Set job periodically according to time_code.

    :param ssh: paramiko.SSHClient class.
    :param file_location: (str) location of the file
                          from the root directory.
    :param file_location: (str) code for the crontab.
    :return: None
    """

    use_python = '~/.conda/envs/MSDS603/bin/python '

    file_location = '/group_hw_1/code/calculate_driving_time.py'

    file_complete_location = expanduser("~") + file_location


    command = time_code + ' ' + use_python + ' ' + file_complete_location

    stdin, stdout, stderr = ssh.exec_command(f"echo '{command}' >> tmp_job")
    #
    # print(stdout.read())
    # print(stderr.read())

    stdin, stdout, stderr = ssh.exec_command('crontab tmp_job')

    # print(stdout.read())
    # print(stderr.read())

    stdin, stdout, stderr = ssh.exec_command('rm tmp_job')

    # print(stdout.read())
    # print(stderr.read())

def close(ssh):
    """
    Closes the SSH connection.

    :param ssh: paramiko.SSHClient class
    :return: None
    """
    ssh.close()


def main():
    """
    Main function.

    :return:  None
    """

    # ec2_address = "ec2-12-123-123-123.us-west-2.compute.amazonaws.com"
    # user = "ec2-user"
    # key_file = "/.ssh/msan603.pem"

    ssh = ssh_client()
    ssh_connection(ssh, ec2_address, user, key_file)
    git_clone_pull(ssh, git_user_id, git_repo_name)
    create_or_update_environment(ssh, git_repo_name)
    set_crontab(ssh)
    close(ssh)


if __name__ == '__main__':
    main()
