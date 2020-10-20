#-*- coding: utf-8  -*-

import sys
import json
import requests
import operator
import argparse

#node_rpc_url = "https://api.cocosbcx.net"
node_rpc_url = "http://127.0.0.1:8049"
#node_rpc_url = "http://10.22.0.17:8049"
#node_rpc_url = "http://10.22.0.14:8049"

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
        for supporter in obj["supporters"]:
            self.supporters[supporter[0]] = supporter[1]

        if obj["id"].startswith("1.6."):
            self.is_witness = True
        else:
            self.is_witness = False

        if self.is_witness:
            self.account = obj["witness_account"]
        else:
            self.account = obj["committee_member_account"]
        
        self.total_votes = obj["total_votes"]
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

    def __str__(self):
        #return "id:{}, url:{}, vote_id:{}, account:{}, total_votes:{}, work_status:{}, supporters:{}".format(
        #        self.id, self.self.vote_id, self.account, self.total_votes, self.work_status, self.supporters)
        return "id:{}, url:{}, vote_id:{}, account:{}, total_votes:{}, work_status:{}".format(
                self.id, self.url, self.vote_id, self.account, self.total_votes, self.work_status)

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

# curl https://api.cocosbcx.net -d '{"id":1, "method":"call", "params":[0,"get_global_properties",[]]}' && echo ""
def get_global_properties():
    req_data = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": [0, "get_global_properties", []],
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

def get_account_votes(vote_objects=[], is_witness=True, vote_accounts=[]):
    result = {}
    vote_obj_list = None
    if is_witness:
        vote_obj_list = get_witnesses_votes(vote_objects)
    else:
        vote_obj_list = get_committee_members_votes(vote_objects)
    # print(vote_obj_list)

    for id, vote_obj in vote_obj_list.items():
        print("\nvote_obj: {}\n".format(vote_obj))
        supporters = vote_obj.supporters
        supporters_keys = supporters.keys()
        votes = {
            "total_votes": int(vote_obj.total_votes)
        }
        for vote_account in vote_accounts:
            vaule = None
            if vote_account in supporters_keys:
                votes[vote_account] = supporters[vote_account]
            else:
                votes[vote_account] = "No Vote Support"
        result[id] = votes
    return result

def vote_find(vote_object=None, vote_accounts=[]):
    if not vote_accounts:
        print("vote accounts empty")
        return
    result = {}
    if not vote_object:
        full_accounts = get_full_accounts(vote_accounts)
        for full_account in full_accounts:
            account, detail = full_account[0], full_account[1]
            account_votes = {}
            if not detail["votes"]:
                account_votes = "No Vote"
            else:
                for obj in detail["votes"]:
                    vote_obj = VoteObj(obj)
                    supporters = vote_obj.supporters
                    if supporters and account in supporters.keys():
                        #print("\n>>>>>>>>>>>>>> {}, vote_object_id: {}, vote_id: {}".format(account, vote_obj.id, vote_obj.vote_id))
                        #print("supporters.keys: ", supporters.keys())
                        account_votes[vote_obj.id] = [vote_obj.vote_id, supporters[account]]
                        #account_votes[vote_obj.id] = supporters[account]
                    else:
                        account_votes[vote_obj.id] = [vote_obj.vote_id, "Supporter Vote miss"]
                        print("\n---------------- {} -----------------: vote_object_id: {}, vote_id: {}".format(account, vote_obj.id, vote_obj.vote_id))
                        print("supporters.keys: ", supporters.keys())
            result[account] = account_votes
    else:
        is_witness, id = get_vote_object_id(vote_object)
        result = get_account_votes([id], is_witness, vote_accounts)
    return result

if __name__ == '__main__':
    print('>> sys.argv: {}'.format(sys.argv))
    parser = argparse.ArgumentParser(description='manual to this script')
    parser.add_argument('-o', '--vote_object', type=str, help='vote object, witness or committee, if None: find account vote detail', default=None)
    parser.add_argument('-a', '--vote_accounts', nargs='+', help='<Required> vote account list', required=True)
    args = parser.parse_args()
    print(">> parse args: {}\n".format(parser.parse_args()._get_kwargs()))

    vote_object = args.vote_object
    vote_accounts = args.vote_accounts

    result = vote_find(vote_object, vote_accounts)
    print(json.dumps(result, indent=4))

