#-*- coding: utf-8  -*-

import json
import requests

node_rpc_url = "https://api.cocosbcx.net"

headers = {"content-type": "application/json"}

def request_post(req_data, is_assert=True):
    response = json.loads(requests.post(node_rpc_url, data = json.dumps(req_data), headers = headers).text)
    # print('>> {} {}\n{}\n'.format(req_data['method'], req_data['params'], response))
    #print('>>{} {}\n'.format(req_data['method'], req_data['params']))
    if is_assert:
        assert 'error' not in response
    return response

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
    votes = []
    for witness in witnesses_data:
        if witness:
            votes.append(witness["vote_id"])
    return votes

def get_committee_members_votes(members=[]):
    committee_data = get_node_committee_members(members)
    #print(committee_data)
    votes = []
    for committee in committee_data:
        if committee:
            votes.append(committee["vote_id"])
    return votes


def get_active_vote_ids():
    active_witnesses = get_global_properties()["active_witnesses"]
    #print(active_witnesses)
    witness_vote_ids = get_witnesses_votes(active_witnesses)
    #print(witness_vote_ids)

    active_members = get_global_properties()["active_committee_members"]
    committee_vote_ids = get_committee_members_votes(active_members)
    #print(committee_vote_ids)
    return witness_vote_ids + committee_vote_ids

def get_all_vote_ids():
    witness_count = get_witness_count()
    #print(witness_count)
    witnesses = []
    for i in range(1, witness_count+1):
        witnesses.append("1.6."+str(i))
    #print(witnesses)
    witness_vote_ids = get_witnesses_votes(witnesses)
    #print(witness_vote_ids)

    committee_count = get_committee_count()
    #print(committee_count)
    members = []
    for i in range(0, committee_count+1):
        members.append("1.5."+str(i))
    #print(members)
    committee_vote_ids = get_committee_members_votes(members)
    #print(committee_vote_ids)
    return witness_vote_ids + committee_vote_ids

def main():
    ids = get_active_vote_ids()
    print("active vote object ids: \n{}".format(json.dumps(ids)))

    ids = get_all_vote_ids()
    print("\nall vote object ids: \n{}".format(json.dumps(ids)))
    pass

if __name__ == '__main__':
    main()


