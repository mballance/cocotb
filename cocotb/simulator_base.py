'''
Created on Dec 31, 2019

@author: ballance
'''

class SimulatorBase():
    """
    Defines the API that simulators are expected to provide 
    """
    
    def __init__(self):
        pass
    
    
    def register_timed_callback(self, sim_steps, callback, hndl):
        """Register a callback to be delivered after 'sim_steps' time"""
    
    def deregister_callback(self, hndl):
        """Removes a previously-registered callback"""