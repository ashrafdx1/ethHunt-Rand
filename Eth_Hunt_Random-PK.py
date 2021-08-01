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
eth_address_list = set([line.split('\n')[0].lower()for line in open("eth_address.txt",'r')])
screen_print_after_keys = 100000
#==============================================================================
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
    
    print('Starting thread:', r)

    while True:
        if match.is_set():
            return

        with counter.get_lock():
            counter.value += 1

        privateKey = os.urandom(32).hex()
        acct = web3.eth.Account.privateKeyToAccount(privateKey)
        eth_addr = acct.address.lower()

        if (k+1)%screen_print_after_keys == 0: 
            print('[+] Total Keys Checked : {0}  [ Speed : {1:.2f} Keys/s ]  Current ETH: {2}'.format(counter.value, counter.value/(time.time() - st), eth_addr))

#        print(eth_address_list.count(str(eth_addr[:]))> 0)
#        print(eth_addr[:] in eth_address_list)
        if eth_addr[:] in eth_address_list:
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
