'''
Created on Dec 31, 2019

@author: ballance
'''
from cocotb.scheduler import Scheduler
from cocotb.log import SimLog

class Context():
    """Collects core cocotb execution elements"""
    
    def __init__(self, info, sim):
        self.info = info
        self.simulator = sim
        self.scheduler = Scheduler()
        self.log = SimLog('cocotb')