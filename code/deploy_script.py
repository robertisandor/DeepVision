import paramiko
import os
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

    git_user = git_credentials()

    stdin, stdout, stderr = ssh.exec_command("git config " +
                                             "--global " +
                                             "credential.helper store")



    stdin, stdout, stderr = ssh.exec_command(f"cd {git_repo_name}")

    # Try cloning the repo
    if b"" == stderr.read():

        git_pull_command = f"cd {git_repo_name} ; git pull"
        stdin, stdout, stderr = ssh.exec_command(git_pull_command)

    else:
        git_clone_command = f"git clone https://{git_user}" +\
                            "@github.com/" + \
                            git_user_id + "/" + git_repo_name + f".git"

        stdin, stdout, stderr = ssh.exec_command(git_clone_command)
        print(stdout.read())
        print(stderr.read())


def create_or_update_environment(ssh, git_repo_name):
    """
    Creates/update python environment with the repo's .yaml file.

    :param ssh: paramiko.SSHClient class
    :return: None
    """

    repo_path = 'code/'
    stdin, stdout, stderr = ssh.exec_command(f"cd ~/.conda/envs/MSDS603")

    # Try cloning the repo
    if b"" == stderr.read():
        stdin, stdout, stderr = ssh.exec_command(f"conda env create -f \
        ~/{git_repo_name}/{repo_path}environment.yml")
 
    else:
        stdin, stdout, stderr = ssh.exec_command(f"conda env update \
        -f ~/{git_repo_name}/{repo_path}environment.yml")

        print(stdout.read())
        print(stderr.read())


def print_port(ssh, server_path):
    '''
    Prints the port number in which the app runs according to the .flaskenv file.

    :param ssh: paramiko ssh client (connected)
    :param server_path: path to the application directory (where .flaskenv is located)
    :return: None
    '''

    stdin, stdout, stderr = ssh.exec_command(f"cat {os.path.join(server_path,'.flaskenv')}")

    # print(stdout.read().decode("utf-8").split('\n'))

    for line in stdout.read().decode("utf-8").split('\n'):
        if 'FLASK_RUN_PORT' in line: info = line; break

    print(f"App running in port number {info.split('=')[1]}")


def launch_application(ssh, server_path=f'~/{git_repo_name}/code'):
    '''
    Launch application server_path under the MSDS603 environment and print port.

    :param ssh: paramiko ssh.Client (already connected)
    :param server_path: path to directory where run_app.py is located.
    :return: None
    '''

    #first_command = 'conda activate MSDS603'

    second_command = f'cd {server_path}'

    third_command = 'sudo ~/.conda/envs/MSDS603/bin/flask run'

    stdin, stdout, stderr = ssh.exec_command(second_command + ' ; ' + third_command)

    print(stdout.read())
    print(stderr.read())

    print_port(ssh, server_path)


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

    ssh = ssh_client()
    ssh_connection(ssh, ec2_address, user, key_file)
    git_clone_pull(ssh, git_user_id, git_repo_name)
    create_or_update_environment(ssh, git_repo_name)
    # set_crontab(ssh)
    launch_application(ssh)
    close(ssh)


if __name__ == '__main__':
    main()
