# xmd
simple wrapper to run local/remote unix/windows command in same interface

#How to use

Remote:
factory=RemoteFactory(is_local, is_win, hostname=, username, password)
Local:
factory=LocalFactory(is_local, is_win, hostname, username, password)


connector=Commander(factory)

connector.run(['ifconfig'])
  
print connector.out_put
print connector.command
print connector.status_code
