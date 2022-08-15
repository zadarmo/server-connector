# server_connector

A simple tool for developers to perform operations on server with just a few line of codes.

# install
```cmd
pip i server_connector
```

# Usage
Before you perform operations on server, you need to initialize a `ServerConnector object`:
```python
from server_connector import server
server_info = {
    "ip": "your server ip",
    "username": "xxx",
    "password": "xxx"
}
sc = server.ServerConnector(server_info)
```

## File operations
### `uploadFile(localPath, remotePath)`
Upload a file from client to server.
```python
sc.uploadFile("./xxx.txt", "/<directory>/xxx.txt")
```
Directory will be created recursively if it does not exist on server.

### `downloadFile(remotePath, localPath)`
Download a file from server to client.
```python
sc.downloadFile("/<directory>/xxx.txt", "./xxx.txt")
```

### `deleteFile(remotePath)`
Delete a file from server.
```python
sc.downloadFile("/path/to/your/file")
```

## Directory operations
### `uploadDir(localPath, remotePath)`
Upload a directory from client to server.
```python
sc.uploadDir("./xxx", "/<directory>")
```
The xxx directory will be uploaded to `/<directory>/xxx` on server.

### `downloadDir(remotePath, localPath)`
Download a directory from server to client.
```python
sc.downloadDir("/<directory>/xxx", "./")
```


### `deleteDir(remotePath)`
Delete a directory from server.
```python
sc.deleteDir("/path/to/your/directory")
