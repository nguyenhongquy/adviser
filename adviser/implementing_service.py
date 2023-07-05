# FIRST SET UP ENVIRONMENT

import sys
import os
from typing import List
import time
sys.path.append(os.path.abspath('../..'))

from utils.topics import Topic
from services.service import Service, PublishSubscribe, RemoteService

from utils.domain.domain import Domain
from utils.domain.jsonlookupdomain import JSONLookupDomain
from utils.logger import DiasysLogger, LogLevel

from services.hci import ConsoleInput, ConsoleOutput
from services.nlu import HandcraftedNLU
from services.bst import HandcraftedBST
from services.policy import HandcraftedPolicy
from services.nlg import HandcraftedNLG
from services.domain_tracker import DomainTracker

from services.service import DialogSystem

from torch.utils.tensorboard import SummaryWriter
from services.policy.rl.experience_buffer import NaivePrioritizedBuffer
from services.simulator import HandcraftedUserSimulator
# from services.policy import DQNPolicy
from services.stats.evaluation import PolicyEvaluator

# Create the first service
# this service listens to 2 topics (A and B), and publish 2 topics
class ConcatenateService(Service):
    "subcribe to 2 topics and publish 2 output topics"
    @PublishSubscribe(sub_topics=['A','B'], pub_topics=['C','D'])
    def concatenate(self, A: int = None, B: str = None) -> dict(C=str, D=str):
        print("Concatenating ", A, "and", B)
        result = str(A) + " " + B
        if A == 3:
            return {"D": result}
        else:
            return {"C": result}

# Create the second service
# generate messages that the first service listens to 
class PrintService(Service):
    @PublishSubscribe(sub_topics=['D'], pub_topics=[Topic.DIALOG_END])
    def print_d(self, D: str):
        "print the content of D [the concatenate message] then publish the end dialogue signal"
        print(f"RECEIVED D={D}")
        return {Topic.DIALOG_END: True}

    @PublishSubscribe(sub_topics=['start'])
    def turn_start(self, start: bool = True):
        "start the comunication and send something"
        a = 1
        while a < 4:
            time.sleep(0.5)
            self.send_a(a)
            a += 1
        time.sleep(0.5)
        self.send_b()

    @PublishSubscribe(pub_topics=["A"])
    def send_a(self, a: int):
        print("SENDING A=", a)
        return {"A": a}

    @PublishSubscribe(pub_topics=['B'])
    def send_b(self):
        print("sending B")
        return {"B": "messaged dropped!"}
    
# concatenate_service = ConcatenateService()
# print_service = PrintService()
# ds = DialogSystem(services=[concatenate_service, print_service], debug_logger = None)
# ds.print_inconsistencies()
# ds.draw_system_graph(name="graph1")

# logger = DiasysLogger(console_log_lvl=LogLevel.NONE, file_log_lvl=LogLevel.DIALOGS)

# # running a dialog
# ds.run_dialog(start_signals={'start': True})
# ds.shutdown

# print("not stuck in a dialog loop")

class ConcatenateServiceWithDomain(Service):
    def __init__(self, domain: str = "mydomain"):
        """ NEW: domain name! """
        Service.__init__(self, domain=domain)

    @PublishSubscribe(sub_topics=["A", "B"], pub_topics=["C", "D"])
    def concatenate(self, A: int = None, B: str = None) -> dict(C=str,D=str):
        """ NOTE: This function did not change at all """
        print("CONCATENATING ", A, "AND ", B)
        result = str(A) + " " + B
        if A == 3:
            return {'D/superhero': result}
        else:
            return  {'C/superhero': result}


super_domain = JSONLookupDomain(name='superhero')
# the jsonlookupdomain provide querying functionality for an sqlite-db and and access to an ontology/json file
concatenate_service = ConcatenateService()
# concatenate_service = ConcatenateServiceWithDomain(super_domain)
print_service = PrintService()
ds = DialogSystem(services=[concatenate_service, print_service], debug_logger = None)
ds.print_inconsistencies()
ds.draw_system_graph(name="graph1")

logger = DiasysLogger(console_log_lvl=LogLevel.NONE, file_log_lvl=LogLevel.DIALOGS)

# running a dialog
ds.run_dialog(start_signals={'start': True})
ds.shutdown

print("not stuck in a dialog loop")
