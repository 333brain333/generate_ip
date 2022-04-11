#!/usr/bin/env python3
#-*-coding: utf-8 -*-

'''
Telegram bot.
Generates next free ip from office network and adds it into a reserved list. 
Removes reserved ips from list.
Generates list of current reserved ips with description.
'''
import pandas as pd
import subprocess
import syslog
import os
#import logging
from ipaddress import IPv4Network
from threading import Thread


def run(command):
    '''
    Starts subprocess and waits untill it exits. Reads stdout after subpocess completes. 
    '''
    #syslog.syslog(syslog.LOG_INFO, 'Subprocess: "' + command + '"')
    #print(f"command: {command}")
    try:
        command_line_process = subprocess.Popen(
            command,
            shell = True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        process_output, _ =  command_line_process.communicate()
        #syslog.syslog(syslog.LOG_DEBUG, process_output.decode('utf-8'))
    except (OSError) as exception:

        syslog.syslog(syslog.LOG_ERR, exception)
        return False
    #else:
    #    syslog.syslog(syslog.LOG_INFO, 'Subprocess finished')
    #print("command out: ",process_output.decode('utf-8'))
    return process_output.decode('utf-8')



def generate_list(path:str, subnet:str)->pd.DataFrame:
    '''
    Returns string with a list of reserved ips in it.
    At request scans network in order find and add new ip that was never added by user before.
    '''
    df = pd.read_csv(path)
    out = run(f'nmap -sn {subnet}')
    for line in out.splitlines():
        if 'Nmap scan report for' in line:
            ip = line.split()[-1:][0].strip('(|)')
            if len(set(list(df.loc[:,'IP'])+[ip]))>len(set(df.loc[:,'IP'])):
                df.loc[df.shape[0]] = ['Nmap_added', '',ip,'','','']
    df.to_csv(path, index=False)
            

def generate_ip(path:str, subnet:str, data:dict)->pd.DataFrame:
    '''
    Returns next free ip and saves it into reserved list.
    '''
    df = pd.read_csv(path)
    network = IPv4Network(subnet)
    hosts_iterator = [str(host) for host in network.hosts() if str(host) not in df.loc[:,'IP'].values]
    df.loc[df.shape[0],'Устройство'] = data['Device name']            # input("Device name:")
    df.loc[df.shape[0]-1,'MAC адрес'] = data['Mac']                     # input("MAC:")
    df.loc[df.shape[0]-1,'Описание'] = data['Description']              # input("Description:")
    df.loc[df.shape[0]-1,'Ответственный'] = data['Who is in charge']     # input("Who is in charge:")
    df.loc[df.shape[0]-1,'Серийный номер'] = data['Serial number']      # input("Serial number:")
    for ip in hosts_iterator:
        p_ping = subprocess.Popen(["ping", "-c", "1", "-W", "1", ip],
                                    shell = False, stdout = subprocess.PIPE)
        if p_ping.wait() == 0:
            continue
        else:
            print(f'Your IP: {ip}')
            df.loc[df.shape[0]-1, 'IP'] = ip
            df.to_csv(path, index=False)
            return ip

def remove_ip(path:str, ip:str)->str:
    '''
    Removes ip from reserved list.
    '''
    df = pd.read_csv(path)
    if any(df[df['IP'].str.contains(ip) == True]['IP']):
        df.drop(df[df["IP"]==ip].index, inplace=True)
        df.to_csv(path, index=False)
        return 'Deleted'
    else:
        return 'No such'




if __name__=='__main__':
    ip_config ={
        'Device name': '',
        'Mac': '',
        'Description': '',
        'Who is in charg': '',
        'Serial number': ''
    } 
    chat_ids = set()
    subnet = '192.168.4.0/24'
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    path = f'{cur_dir}/external_dir/reserved_list.csv' 
    generate_list(path, subnet)
    generate_ip(path,subnet, ip_config)
    #remove_ip(path, 'lskdjfsdkjf')

    
