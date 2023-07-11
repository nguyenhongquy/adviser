import sys, os, time, json, random
from typing import List
from collections import defaultdict

from utils.domain.jsonlookupdomain import JSONLookupDomain
from services.service import Service, PublishSubscribe, DialogSystem

from services.hci import ConsoleInput, ConsoleOutput
from utils.logger import DiasysLogger, LogLevel


sys.path.append('../soloist')
os.environ['CUDA_VISIBLE_DEVICES'] = '2' # should be available at test time

from soloist.server import *
# args.model_name_or_path = '../soloist/examples/recipe/recipe_models_all_10e'
args.model_name_or_path = '../soloist/examples/recipe/recipe_models_noneg_10e'
print("imported recipe model")
args.length = 100
main()

def parse(sampled_results):
    candidates = []
    for system_response in sampled_results:
        system_response = system_response.split('system :')[-1]
        system_response = ' '.join(word_tokenize(system_response))
        system_response = system_response.replace('[ ','[').replace(' ]',']')
        candidates.append(system_response)

    candidates_bs = []
    for system_response in sampled_results:
        system_response = system_response.strip()
        system_response = system_response.split('system : ')[0]
        system_response = system_response.split('dp : ')[0]
        system_response = ' '.join(system_response.split()[:])
        svs = system_response.split(';')
        bs_state = {}
        for sv in svs:
            if '=' in sv:
                s,v = sv.strip().split('=')
                s = s.strip()
                v = v.strip()
                bs_state[s] = v
        candidates_bs.append(copy.copy(bs_state))

    candidates_w_idx = [(idx, v) for idx,v in enumerate(candidates)]
    candidates = sorted(candidates_w_idx, key=functools.cmp_to_key(compare))


    idx, response = candidates[-1]
    states = candidates_bs[idx]
    return states, response

def compare(key1, key2):
    key1 = key1[1]
    key2 = key2[1]
    if key1.count('[') > key2.count('['):
        return 1
    elif key1.count('[') == key2.count('['):
        return 1 if len(key1.split()) > len(key2.split()) else -1
    else:
        return -1  

def predictor(context, max_turn = 14):
    context_formated = []
    for idx, i in enumerate(context):
        if idx % 2 == 0:
            context_formated.append(f'user : {i}')
        else:
            context_formated.append(f'system : {i}')    
    sampled_results = sample(context_formated[-max_turn:])
    belief_states, response = parse(sampled_results)

    return response, belief_states

def get_response(context):
    response, belief_states = predictor(context)
    return response, belief_states


# Input modules (just allow access to terminal for text based dialog)
# user_in: (sub_topics=[Topic.DIALOG_END], pub_topics=["gen_user_utterance"])
user_in = ConsoleInput(domain="")
# user_out: (sub_topics=["sys_utterance"], pub_topics=[Topic.DIALOG_END])
user_out = ConsoleOutput(domain="")


class WizardService(Service):
    def __init__(self, domain=None, logger=None,
                sub_topic_domains = {'gen_user_utterance': '',
                                    'sys_utterance': ''}):
        Service.__init__(self, domain=domain)
        self.memory = []

    @PublishSubscribe(sub_topics=["gen_user_utterance"], pub_topics=["sys_utterance"])
    def generate_sys_utterance(self, gen_user_utterance):
        if gen_user_utterance == '':
            return {'sys_utterance': 'Please chat with the agent'}
        elif 'bye' in gen_user_utterance:
            return {'sys_utterance': 'Good bye'}
        else:
            response = self.say_something_meaningful(gen_user_utterance)
            self.memory.append(response)
            return {'sys_utterance': response}
    
    def say_something_meaningful(self, gen_user_utterance):
        self.update_memory(gen_user_utterance)
        print(f"***History tracker: {self.memory}***\n")
        response, bs = get_response(self.memory)
        print(f"***Belief States tracker: {bs}***\n")
        return response
    
    def update_memory(self, utterance):
        self.memory.append(utterance.strip())
        return None
        

    
logger = DiasysLogger(console_log_lvl=LogLevel.DIALOGS)

wizard_service = WizardService()
ds = DialogSystem(services=[user_in, user_out, wizard_service])

error_free = ds.is_error_free_messaging_pipeline()
if not error_free:
    ds.print_inconsistencies()

ds.draw_system_graph()

number_dialogues = 1
for _ in range(number_dialogues):
    print("begin chatting")
    ds.run_dialog({'gen_user_utterance': ""})

ds.shutdown()
