import subprocess


def transfer_and_cleanup_files(
        local_identity_file, remote_user, remote_host, remote_directory,
        local_directory, filename_pattern="final_*.mp3"
):
    """
    Transfers files from a remote server to a local directory using scp and
    then deletes the files from the remote server using ssh.

    :param local_identity_file: Path to the local SSH identity file
    :param remote_user: Username for the remote server
    :param remote_host: Hostname or IP address of the remote server
    :param remote_directory: Directory on the remote server containing the files
    :param local_directory: Local directory to transfer the files to
    :param filename_pattern: Pattern of filenames to transfer and delete (default is "final_*.mp3")
    """
    # Construct the SCP command
    scp_command = [
        "scp",
        "-i", local_identity_file,
        "-r", f"{remote_user}@{remote_host}:{remote_directory}/{filename_pattern}",
        local_directory
    ]

    # Construct the SSH command
    ssh_command = [
        "ssh",
        "-i", local_identity_file,
        f"{remote_user}@{remote_host}",
        f"rm {remote_directory}/{filename_pattern}"
    ]

    try:
        # Run the SCP command
        result = subprocess.run(scp_command, capture_output=True, text=True, check=True)
        print("SCP Command Output:\n", result.stdout)

        # Run the SSH command
        result = subprocess.run(ssh_command, capture_output=True, text=True, check=True)
        print("SSH Command Output:\n", result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        print(e.stderr)
