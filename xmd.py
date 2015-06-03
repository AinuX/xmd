'''
Created on May 28, 2015

@author: Ainux
'''
import spur
import abc
from abc import ABCMeta
import winrm
import sys




class AbstractFactory(object):
    
    __metaclass__=ABCMeta
    
    def __init__(self, is_local, is_win=False, **kwargs):
        
        self.is_local=is_local
        self.is_win=is_win
        self.kwargs=kwargs
    
    @abc.abstractmethod
    def create_client(self):
        pass
    @property
    def get_type(self):
        return self.is_win
    
class LocalFactory(AbstractFactory):
    
    def create_client(self):
        if self.is_local:
            return LocalCommander()

class RemoteFactory(AbstractFactory):
    def create_client(self):
        if not self.is_local:
            if self.is_win:
                return RemoteWinCommander(**self.kwargs)
            else:
                return RemoteUnixCommander(**self.kwargs)
        
            
class LocalCommander():
    
    def __call__(self):
        return spur.LocalShell()            
        
class RemoteUnixCommander():
    
    def __init__(self, **kwargs):
        self.kwargs=kwargs

    def __call__(self):

        try:
            return spur.SshShell(hostname=self.kwargs['hostname'], username=self.kwargs["username"],password=self.kwargs["password"],\
                                 missing_host_key=spur.ssh.MissingHostKey.accept, shell_type=spur.ssh.ShellTypes.sh, port=22)
        finally:
        #except CommandInitializationError as e:
            return spur.SshShell(hostname=self.kwargs['hostname'], username=self.kwargs["username"],password=self.kwargs["password"],\
                                 missing_host_key=spur.ssh.MissingHostKey.accept, shell_type=spur.ssh.ShellTypes.minimal, port=22)         

class RemoteWinCommander():
    """
    Enable WinRM on remote host

    Enable basic WinRM authentication (Good only for troubleshooting. For hosts in a domain it is better to use Kerberos authentication.)
    Allow unencrypted message passing over WinRM (not secure for hosts in a domain but this feature was not yet implemented.)

        winrm set winrm/config/client/auth @{Basic="true"}
        winrm set winrm/config/service/auth @{Basic="true"}
        winrm set winrm/config/service @{AllowUnencrypted="true"}

    """
    def __init__(self,**kwargs):
        self.kwargs=kwargs
        
    def __call__(self):
        
        return winrm.Session(target=self.kwargs["hostname"],auth=(self.kwargs["username"],self.kwargs["password"]))
        

class Commander():
    
    def __init__(self, factory):
        self.client=factory.create_client().__call__()
        self.is_win=factory.get_type
    
    def run(self, *args):
        self.args= args
        if self.is_win:
            cmd=self.args[0][0].split()[0]
            args=[' '.join(self.args[0][0].split()[1:])]
            try:
                self.result=self.client.run_cmd(cmd, *args)
            except winrm.exceptions.WinRMTransportError:
                print "Connection timed out"
                print "Please check the network connection, or remember to enable WinRM on the remote target\n"
                print 'winrm set winrm/config/client/auth @{Basic="true"}\n\
                       winrm set winrm/config/service/auth @{Basic="true"}\n\
                       winrm set winrm/config/service @{AllowUnencrypted="true"}\n'
                sys.exit(-1)
                
        else:
            self.result=self.client.run(*self.args)
        return self.result
 
    @property
    def out_put(self):
        if self.is_win:
            return self.result.std_out
        else:
            return self.result.output
    
    @property
    def status_code(self):
        if self.is_win:
            return self.result.status_code
        else:
            return self.result.return_code
    
    @property
    def command(self):
        return ' '.join(self.args[0])
