'''
Created on Dec 31, 2019

@author: ballance
'''

class Info():
    
    def __init__(self):
        self.sim_name    = "unknown"
        self.sim_version = "unknown"
        self.argv = []
    
    def set_sim_name(self, name):
        self.sim_name = name
    
    def set_sim_version(self, version):
        self.sim_version = version
