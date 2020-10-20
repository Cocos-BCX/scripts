# -*- coding:utf-8 -*-
import math
import numpy as np
import json
import requests

#define
GRAPHENE_100_PERCENT                = 10000
GRAPHENE_1_PERCENT                  = (GRAPHENE_100_PERCENT/100)
GRAPHENE_IRREVERSIBLE_THRESHOLD     = (70 * GRAPHENE_1_PERCENT)

node_rpc_url = "https://api.cocosbcx.net"

headers = {"content-type": "application/json"}

def request_post(req_data, is_assert=True):
    response = json.loads(requests.post(node_rpc_url, data=json.dumps(req_data), headers=headers).text)
    # print('>>{} {}'.format(req_data['method'], req_data['params']))
    if is_assert:
        assert 'error' not in response
    return response

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

def partition_arg_topK(matrix, K, axis=0):
    """
        perform topK based on np.argpartition
        :param matrix: to be sorted
        :param K: select and sort the top K items
        :param axis: 0 or 1. dimension to be sorted.
        :return:
    """
    a_part = np.argpartition(matrix, K, axis=axis)
    # print('axis: {}'.format(axis))
    if axis == 0:
        row_index = np.arange(matrix.shape[1 - axis])
        a_sec_argsort_K = np.argsort(matrix[a_part[0:K, :], row_index], axis=axis)
        return a_part[0:K, :][a_sec_argsort_K, row_index]
    else:
        column_index = np.arange(matrix.shape[1 - axis])[:, None]
        a_sec_argsort_K = np.argsort(matrix[column_index, a_part[:, 0:K]], axis=axis)
        return a_part[:, 0:K][column_index, a_sec_argsort_K]

def update_last_irreversible_block():
    witness_last_blocks = []
    gpo = get_objects("2.0.0")[0]
    dpo = get_objects("2.1.0")[0]
    last_irreversible_block_num = dpo['last_irreversible_block_num']
    print("id: {}, head_block_number: {}, last_irreversible_block_num: {}\n".format(
        dpo['id'],dpo['head_block_number'], dpo['last_irreversible_block_num']))
    active_witnesses = gpo['active_witnesses']
    for witness_id in active_witnesses:
        witness = get_objects(witness_id)[0]
        last_confirmed_block_num = witness['last_confirmed_block_num']
        witness_last_blocks.append(last_confirmed_block_num)
        witness_account_obj = get_objects(witness["witness_account"])[0]
        if last_confirmed_block_num < last_irreversible_block_num - 11:
            print("\033[1;32;40mwitness:{}, account: {}, last_confirmed_block_num: {}\033[0m".format(
                witness['id'], witness_account_obj["name"], last_confirmed_block_num))
        else:
            print("witness:{}, account: {}, last_confirmed_block_num: {}".format(
                witness['id'], witness_account_obj["name"], last_confirmed_block_num))

    witness_size = len(witness_last_blocks) 
    offset = math.floor(((GRAPHENE_100_PERCENT - GRAPHENE_IRREVERSIBLE_THRESHOLD) * witness_size / GRAPHENE_100_PERCENT))
    # print('>> witness size: {}, offset: {}'.format(witness_size, offset))

    block_nums = np.array(witness_last_blocks)
    print('\nwitness size: {}, offset: {}, offset block_num: {}'.format(witness_size, offset, block_nums[offset]))
    part_numbers = np.partition(block_nums, offset)
    # print('\npartition sort: ', part_numbers)

    new_last_irreversible_block_num = part_numbers[offset]
    print('\nlast_irreversible_block_num    : {}'.format(last_irreversible_block_num))
    print('new_last_irreversible_block_num: {}'.format(new_last_irreversible_block_num))
    msg = ""
    if new_last_irreversible_block_num > last_irreversible_block_num:
        msg = ">> [DB]update_last_irreversible_block: {}".format(new_last_irreversible_block_num)
    else:
        msg = ">> Don't update_last_irreversible_block"
    print("\033[1;32;40m{}\033[0m".format(msg))

def main():
    update_last_irreversible_block()
    dpo = get_objects("2.1.0")[0]
    print("id: {}, head_block_number: {}, last_irreversible_block_num: {}".format(
        dpo['id'],dpo['head_block_number'], dpo['last_irreversible_block_num']))

if __name__ == '__main__':
    main()


'''
dev@ubuntu:~/data/CocosBCX/scripts$ python3 calc_last_irreversible_block.py 
id: 2.1.0, head_block_number: 12456780, last_irreversible_block_num: 12456768

witness:1.6.15, account: blockchainkeys, last_confirmed_block_num: 12456777
witness:1.6.17, account: cpower, last_confirmed_block_num: 12456779
witness:1.6.20, account: dongdongxixi2020, last_confirmed_block_num: 12420111
witness:1.6.23, account: chainplay-bp, last_confirmed_block_num: 12456773
witness:1.6.25, account: bigcocos, last_confirmed_block_num: 12456776
witness:1.6.26, account: ladys-bp, last_confirmed_block_num: 12456767
witness:1.6.27, account: cocostomoon, last_confirmed_block_num: 12456778
witness:1.6.29, account: moonriver, last_confirmed_block_num: 12450926
witness:1.6.34, account: imcocos-bp, last_confirmed_block_num: 12456768
witness:1.6.35, account: cocos-ying, last_confirmed_block_num: 12456775
witness:1.6.36, account: we-chat, last_confirmed_block_num: 12456780

witness size: 11, offset: 3, offset block_num: 12456773

last_irreversible_block_num    : 12456768
new_last_irreversible_block_num: 12456768
>> Don't update_last_irreversible_block
id: 2.1.0, head_block_number: 12456781, last_irreversible_block_num: 12456773
dev@ubuntu:~/data/CocosBCX/scripts$ 
dev@ubuntu:~/data/CocosBCX/scripts$ python3 calc_last_irreversible_block.py 
id: 2.1.0, head_block_number: 12456783, last_irreversible_block_num: 12456776

witness:1.6.15, account: blockchainkeys, last_confirmed_block_num: 12456777
witness:1.6.17, account: cpower, last_confirmed_block_num: 12456779
witness:1.6.20, account: dongdongxixi2020, last_confirmed_block_num: 12420111
witness:1.6.23, account: chainplay-bp, last_confirmed_block_num: 12456782
witness:1.6.25, account: bigcocos, last_confirmed_block_num: 12456776
witness:1.6.26, account: ladys-bp, last_confirmed_block_num: 12456781
witness:1.6.27, account: cocostomoon, last_confirmed_block_num: 12456778
witness:1.6.29, account: moonriver, last_confirmed_block_num: 12450926
witness:1.6.34, account: imcocos-bp, last_confirmed_block_num: 12456783
witness:1.6.35, account: cocos-ying, last_confirmed_block_num: 12456784
witness:1.6.36, account: we-chat, last_confirmed_block_num: 12456780

witness size: 11, offset: 3, offset block_num: 12456782

last_irreversible_block_num    : 12456776
new_last_irreversible_block_num: 12456777
>> [DB]update_last_irreversible_block: 12456777
id: 2.1.0, head_block_number: 12456784, last_irreversible_block_num: 12456777
dev@ubuntu:~/data/CocosBCX/scripts$ 
'''
