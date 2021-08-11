# SSH client for Windows 10

References:
- https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse
- https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_keymanagement

## Install SSH client

1. Launch PowerShell as an Administrator ([link](https://www.howtogeek.com/194041/how-to-open-the-command-prompt-as-administrator-in-windows-8.1/)).

2. Type `Get-WindowsCapability -Online | ? Name -like 'OpenSSH*'` and enter.

        Get-WindowsCapability -Online | ? Name -like 'OpenSSH*'
        
        # This should return the following output:
        
        Name  : OpenSSH.Client~~~~0.0.1.0
        State : NotPresent
        Name  : OpenSSH.Server~~~~0.0.1.0
        State : NotPresent

3. Type `Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0` and enter.

## Install Windows Terminal

1. Download and install [Windows Terminal from Microsoft Store](https://aka.ms/terminal)

## Initial use of SSH

1. Launch PowerShell using [Windows Terminal](https://github.com/microsoft/terminal).

2. Follow [this](https://docs.microsoft.com/en-us/windows-server/administration/openssh/openssh_install_firstuse#initial-use-of-ssh) instruction.

> Once you have installed the OpenSSH Server on Windows, you can quickly test it using PowerShell from any Windows device with the SSH Client installed. In PowerShell type the following command:
>
>         ssh username@servername
>         # The first connection to any server will result in a message similar to the following:
>         
>         The authenticity of host 'servername (10.00.00.001)' can't be established.
>         ECDSA key fingerprint is SHA256:(<a large string>).
>         Are you sure you want to continue connecting (yes/no)?
>
> The answer must be either "yes" or "no". Answering Yes will add that server to the local system's list of known ssh hosts.

## Generate SSH key

1. Launch PowerShell using [Windows Terminal](https://github.com/microsoft/terminal).

2. Type `ssh-keygen` and enter.

        ssh-keygen
        
        # This should return the following output:
        
        Generating public/private rsa key pair.
        Enter file in which to save the key (C:\Users\.../.ssh/id_rsa):
        Enter passphrase (empty for no passphrase):
        Enter same passphrase again:

3. Check your SSH public key using command below.

        type ~\.ssh\id_rsa.pub
