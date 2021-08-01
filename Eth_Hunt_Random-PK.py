# -*- coding: utf-8 -*-
"""
@Original author: iceland
@modifier author: ashrafdx1
"""
import time
import sys
#**************************************************************
import os
import web3
from web3 import Web3
#**************************************************************
from multiprocessing import Manager, Event, Process, Queue, Value, cpu_count
#==============================================================================
#eth_address_list = [line.split(',')[0] for line in open("eth_address_lower2021-Aug-01__07_17_30.txt",'r')]
#eth_address_list = set(eth_address_list)
with open('eth_address.txt') as f:
    eth_address_list_u = f.readlines()
eth_address_list = eth_address_list_u
for i in range(len(eth_address_list_u)):
    eth_address_list[i] = eth_address_list_u[i].lower()
#print(eth_address_list)
screen_print_after_keys = 100000
#==============================================================================
prefix = '0x'
def getAddr(prefix,PK):
    """This function get address from private key,
        returns the address as a string"""

    acct = web3.eth.Account.privateKeyToAccount(PK)
    if acct.address[:len(prefix)] == prefix: 
        return acct.address
#==============================================================================
def hunt_ETH_address(cores='all'):  # pragma: no cover

    available_cores = cpu_count()

    if cores == 'all':
        cores = available_cores
    elif 0 < int(cores) <= available_cores:
        cores = int(cores)
    else:
        cores = 1

    counter = Value('L')
    match = Event()
    queue = Queue()

    workers = []
    for r in range(cores):
        p = Process(target=generate_key_address_pairs, args=(counter, match, queue, r))
        workers.append(p)
        p.start()

    for worker in workers:
        worker.join()

    keys_generated = 0
    while True:
        time.sleep(1)
        current = counter.value
        if current == keys_generated:
            if current == 0:
                continue
            break
        keys_generated = current
        s = 'Total Keys generated: {}\r'.format(keys_generated)

        sys.stdout.write(s)
        sys.stdout.flush()

    private_key, address = queue.get()
    print(f'\n\n********************Address found:  {address}')
    print(f'********************Private Key:  {private_key}')
    l = input('saved to file, press anything to exit')

#==============================================================================
def generate_key_address_pairs(counter, match, queue, r):  # pragma: no cover
    st = time.time()
    k = 0
    privateKey = os.urandom(32)
    privateKey = privateKey.hex()
    eth_addr = getAddr(prefix,privateKey)
    print('Starting thread:', r, 'base: ',eth_addr)

    while True:
        if match.is_set():
            return

        with counter.get_lock():
            counter.value += 1

        privateKey = os.urandom(32)
        privateKey = privateKey.hex()
        #eth_addr = getAddr(prefix,privateKey)
        acct = web3.eth.Account.privateKeyToAccount(privateKey)
        eth_addr = acct.address.lower()

        if (k+1)%screen_print_after_keys == 0: 
            print('[+] Total Keys Checked : {0}  [ Speed : {1:.2f} Keys/s ]  Current ETH: {2}'.format(counter.value, counter.value/(time.time() - st), eth_addr))
        for i in eth_address_list:
            if eth_addr[:32] == i[:32]:
                match.set()
                queue.put_nowait((privateKey, eth_addr))
                with open(f'ETH_found_{eth_addr}.txt','a') as fw:
                    fw.write(eth_addr + '\n')
                    fw.write(privateKey)
                return
            
        k += 1

#==============================================================================

if __name__ == '__main__':
    print('[+] Starting.........Wait.....')
    hunt_ETH_address(cores=2)




    
