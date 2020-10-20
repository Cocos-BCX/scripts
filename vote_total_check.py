#-*- coding: utf-8  -*-

import sys
import json
import requests
import operator
import argparse

node_rpc_urls = {
        "mainnet-fn": "https://api.cocosbcx.net",
        "fn-prod01": "http://10.22.0.14:8049",
        "fn-prod02": "http://10.22.0.7:8049",
        "fn-prod03": "http://10.22.0.17:8049",
        "fn-prod04": "http://10.22.0.3:8049"
}

chain_env_key = "fn-prod02"
#node_rpc_url = "https://api.cocosbcx.net"
node_rpc_url = node_rpc_urls[chain_env_key]

headers = {"content-type": "application/json"}

def request_post(req_data, is_assert=True):
    response = json.loads(requests.post(node_rpc_url, data=json.dumps(req_data), headers=headers).text)
    # print('>>{} {}\n'.format(req_data['method'], req_data['params']))
    if is_assert:
        assert 'error' not in response
    return response

###################### class Vote Object
class VoteObj(object):
    def __init__(self, obj):
        self.id = obj["id"]
        self.url = obj["url"]
        self.vote_id = obj["vote_id"]
        self.supporters = {}
        self.supporters_total = 0
        for supporter in obj["supporters"]:
            self.supporters[supporter[0]] = supporter[1]
            self.supporters_total += int(supporter[1]["amount"])

        if obj["id"].startswith("1.6."):
            self.is_witness = True
        else:
            self.is_witness = False

        if self.is_witness:
            self.account = obj["witness_account"]
        else:
            self.account = obj["committee_member_account"]

        self.account_obj = get_objects(self.account)[0]
        self.vote_freeze = 0
        
        if "asset_locked" in self.account_obj:
            if self.is_witness:
                if "witness_freeze" in self.account_obj["asset_locked"]:
                    self.vote_freeze = int(self.account_obj["asset_locked"]["witness_freeze"]["amount"])
            else:
                if "committee_freeze" in self.account_obj["asset_locked"]:
                    self.vote_freeze = int(self.account_obj["asset_locked"]["committee_freeze"]["amount"])
        self.total_votes = int(obj["total_votes"])
        self.work_status = obj["work_status"]

    def __eq__(self, other):
        return operator.eq(self.__dict__, other.__dict__)

    def show_supporters_different(self, other):
        print("basic data: \n{}\n{}".format(self, other))
        other_supporters = other.supporters
        different = {}
        for id, vote in self.supporters.items():
            other_vote = None
            if id in other_supporters.keys():
                other_vote = other_supporters[id]
            if not operator.eq(vote, other_vote):
                different[id] = [vote, other_vote]
        print("votes detail different: \n", different)

    def total_check(self):
        return self.total_votes - self.vote_freeze == self.supporters_total

    def __str__(self):
        return "id:{}, url:{}, vote_id:{}, account:{}, work_status:{}, total_votes:{}, supporters_total: {}, vote_freeze: {}".format(
                self.id, self.url, self.vote_id, self.account, self.work_status, self.total_votes, self.supporters_total, self.vote_freeze)

##########################

def get_full_accounts(accounts):
    try:
        req_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": [0, "get_full_accounts", [accounts, False]],
                "id":1
                }
        return request_post(req_data)["result"]
    except Exception as e:
        print(repr(e))
    return None

def get_objects(id):
    try:
        req_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": [0, "get_objects", [[id]]],
                "id":1
                }
        return request_post(req_data)["result"]
    except Exception as e:
        print(repr(e))
    return None

def get_account_by_name(name):
    try:
        req_data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": [0, "get_account_by_name", [name]],
                "id":1
                }
        return request_post(req_data)["result"]
    except Exception as e:
        print(repr(e))
    return None

# curl https://api.cocosbcx.net -d '{"id":1, "method": "call", "params": [0, "get_witnesses", [["1.6.23"]]]}' && echo ""
# curl http://127.0.0.1:8049 -d '{"id":1, "method": "call", "params": [0, "get_witnesses", [["1.6.23"]]]}' && echo ""
def get_node_witness(witnesses=["1.6.1", "1.6.2"]):
    req_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": [0, "get_witnesses", [witnesses]],
            "id":1
            }
    return request_post(req_data)["result"]

def get_node_committee_members(members=["1.5.1", "1.5.2"]):
    req_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": [0, "get_committee_members", [members]],
            "id":1
            }
    return request_post(req_data)["result"]

def get_witness_count():
    req_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": [0, "get_witness_count", []],
            "id":1
            }
    return request_post(req_data)["result"]

def get_committee_count():
    req_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": [0, "get_committee_count", []],
            "id":1
            }
    return request_post(req_data)["result"]

def get_witnesses_votes(witnesses=[]):
    witnesses_data = get_node_witness(witnesses)
    votes = {}
    for witness in witnesses_data:
        votes[witness["id"]] = VoteObj(witness)
        #if witness["id"] == "1.6.23":
        #    print(witness)
    return votes

def get_committee_members_votes(members=[]):
    witnesses_data = get_node_committee_members(members)
    votes = {}
    for committee in witnesses_data:
        if committee:
            votes[committee["id"]] = VoteObj(committee)
    return votes

def get_vote_object_id(vote_object):
    # return is_witness, vote_object_id
    if vote_object.startswith("1.5"):
        return False, vote_object
    elif vote_object.startswith("1.6"):
        return True, vote_object
    else:
        # TODO support account_name account_id
        pass

def vote_object_total_vote_check(members, is_witness=True):
    result = {}
    vote_obj_list = []
    if is_witness:
        vote_obj_list = get_witnesses_votes(members)
    else:
        vote_obj_list = get_committee_members_votes(members)

    for id in vote_obj_list:
        vote_obj = vote_obj_list[id]
        key = "{}-{}".format(vote_obj.account_obj["name"], id)
        if not vote_obj.total_check():
            result[key] = {
                "check": False,
                "total_votes": vote_obj.total_votes,
                "supporters": vote_obj.supporters_total,
            }
    return result

def vote_check_total(vote_object=None):
    result = {}
    if not vote_object:
        witness_count = get_witness_count()
        witnesses = []
        for i in range(1, witness_count+1):
            witnesses.append("1.6."+str(i))
        witness_check_result = vote_object_total_vote_check(witnesses)
        # print("witness_check_result: ", witness_check_result)

        committee_count = get_committee_count()
        members = []
        for i in range(0, committee_count+1):
            members.append("1.5."+str(i))
        committee_check_result = vote_object_total_vote_check(members, False)
        # print("committee_check_result: ", committee_check_result)
        result = witness_check_result.copy() 
        result = result.update(committee_check_result)
    else:
        is_witness, id = get_vote_object_id(vote_object)
        result = vote_object_total_vote_check([id], is_witness)
    return result

if __name__ == '__main__':
    print('>> sys.argv: {}'.format(sys.argv))
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-o', '--vote_object', type=str, help='vote object, witness or committee, if None: check all', default=None)
    args = parser.parse_args()
    print(">> parse args: {}\n".format(parser.parse_args()._get_kwargs()))
    vote_object = args.vote_object

    result = vote_check_total(vote_object)
    print("chain_env_key: {}, url: {}".format(chain_env_key, node_rpc_urls[chain_env_key]))
    if result:
        print("check result: ", json.dumps(result, indent=4))
    else:
        if not vote_object:
            vote_object = "All Witnesses and Committee_members"
        print("\n{} check done. No Errors.".format(vote_object))

