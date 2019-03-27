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

    # Try cloning the repo
    if (b"" is stderr.read()):
        git_clone_command = "git clone https://github.com/" + \
                            git_user_id + "/" + git_repo_name + ".git"
        stdin, stdout, stderr = ssh.exec_command(git_clone_command)

    # Pull if already exists
    if (b'already exists' in stderr.read()):
        git_pull_command = f"cd {git_repo_name} ; git pull"
        ssh.exec_command(git_pull_command)


def create_or_update_environment(ssh, git_repo_name):
    """
    Creates/update python environment with the repo's .yaml file.

    :param ssh: paramiko.SSHClient class
    :return: None
    """
    stdin, stdout, stderr = ssh.exec_command(f"conda env create -f \
    ~/{git_repo_name}/environment.yml")

    if (b'already exists' in stderr.read()):
        stdin, stdout, stderr = ssh.exec_command(f"conda env update \
        -f ~/{git_repo_name}/environment.yml")
        print(stdout.read())


def set_crontab(ssh, file_location, time_code='* * * * *'):
    """

    :param ssh: paramiko.SSHClient class
    :param file_location: (str) location of the file
                          from the root directory
    :return: None
    """

    use_python = '~/.conda/envs/MSDS603/bin/python '

    file_complete_location = expanduser("~") + file_location

    command = ('crontab -e ; ' + time_code +
               use_python + file_complete_location)

    ssh.exec_command(command)


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
    set_crontab(ssh, file_location)
    close(ssh)


if __name__ == '__main__':
    main()
