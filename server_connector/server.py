import os
import paramiko
from stat import S_ISDIR


class ServerConnector(object):
    def __init__(self, serverInfo: dict):
        """
        Initialize the connection between client and server.

        Parameters
        ----------
        serverInfo : dict
            serverInfo (map): The information of server, including ip, username and password
        """
        self.ip = serverInfo["ip"]
        self.username = serverInfo["username"]
        self.password = serverInfo["password"]

        # build a connection towards port 22
        self.trans = paramiko.Transport((self.ip, 22))
        self.trans.connect(username=self.username,
                           password=self.password)

        # construct a SFTP object
        self.sftp = paramiko.SFTPClient.from_transport(
            self.trans)

        # construct a SSH object
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.ip, port=22, username=self.username,
                         password=self.password, compress=True)
        print("server connector has been initialized...")

    # file operation

    def uploadFile(self, localpath: str, remotepath: str):
        """
        Upload a file from client.
        """
        directory = "/".join(remotepath.split("/")[:-1])
        try:
            self.sftp.stat(directory)
        except FileNotFoundError:
            # directory not exist on server if exception raised
            # mkdir recursively if directory not exist
            self.ssh.exec_command("mkdir -p " + directory)

        self.sftp.put(localpath=localpath, remotepath=remotepath)
        print(f"File {localpath} upload success")

    def downloadFile(self, remotepath: str, localpath: str):
        """
        Download a file from server.
        """
        self.sftp.get(remotepath=remotepath, localpath=localpath)
        print(f"File {remotepath} download success")

    def deleteFile(self, remotepath: str):
        """
        Delete a file from server.
        """
        self.sftp.remove(remotepath)
        print(f"File {remotepath} delete success")

    # directory operation
    def uploadDir(self, localpath: str, remotepath: str):
        """
        Upload a directory from client.
        """
        if not os.path.isdir(localpath):
            raise Exception(f"The path {localpath} is not a directory.")

        basename = os.path.basename(localpath)
        for root, dirs, files in os.walk(localpath):
            for f in files:
                # the tail of the path that is truncated at the position of basename from localpath
                bsnameIdx = root.index(basename)
                tmpDir = root[(bsnameIdx):]
                tmpDir = tmpDir.replace("\\", "/")

                # server directory that will be created
                serverDir = f"{remotepath}/{tmpDir}"

                # use ssh to mkdir on server, cause sftp.mkdir cannot make nesting directories
                self.ssh.exec_command('mkdir -p ' + serverDir)

                # upload file
                self.uploadFile(os.path.join(root, f), f"{serverDir}/{f}")

    def downloadDir(self, remotepath: str, localpath: str):
        """
        Download a directory from server.
        """
        self.sftp.chdir(os.path.split(remotepath)[0])
        parent = os.path.split(remotepath)[1]
        try:
            os.mkdir(localpath)
        except FileExistsError:
            pass
        for path, _, files in self.sftp_walk(parent):
            try:
                os.mkdir(self.remotepath_join(localpath, path))
            except FileExistsError:
                pass
            for filename in files:
                self.downloadFile(self.remotepath_join(path, filename),
                                  os.path.join(localpath, path, filename))

    def deleteDir(self, remotepath: str):
        """
        Delete a directory from server.
        """
        for f in self.sftp.listdir_attr(remotepath):
            serverFile = f"{remotepath}/{f.filename}"
            if S_ISDIR(f.st_mode):  # dir
                self.deleteDir(serverFile)
            else:  # file
                self.sftp.remove(serverFile)
        self.sftp.rmdir(remotepath)
        print(f"Directory {remotepath} deleted.")

    def sftp_walk(self, remotepath):
        # Kindof a stripped down  version of os.walk, implemented for
        # sftp.  Tried running it flat without the yields, but it really
        # chokes on big directories.
        path = remotepath
        files = []
        folders = []
        for f in self.sftp.listdir_attr(remotepath):
            # print(S_ISDIR(f.st_mode))
            if S_ISDIR(f.st_mode):
                folders.append(f.filename)
            else:
                files.append(f.filename)
        yield path, folders, files
        for folder in folders:
            new_path = self.remotepath_join(remotepath, folder)
            for x in self.sftp_walk(new_path):
                yield x

    def remotepath_join(self, *args):
        #  Bug fix for Windows clients, we always use / for remote paths
        return '/'.join(args)

    def release(self):
        """
        Release resources of the connection.
        """
        self.ssh.close()
        self.sftp.close()
        self.trans.close()
