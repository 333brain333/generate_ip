#!/usr/bin/env python3
'''
Telegram bot.
Generates next free ip from Cognitive's Moscow office network and adds it into a reserved list. 
Removes reserved ips from list.
Generates list of current reserved ips with description.
'''
import pandas as pd
import subprocess
import syslog
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
    df=pd.read_csv(path)
    out = run(f'nmap -sn {subnet}')
    for line in out.splitlines():
        if 'Nmap scan report for' in line:
            ip = line.split()[-1:]
            if len(set(list(df.loc[:,'IP'])+ip))>len(set(df.loc[:,'IP'])):
                df.loc[df.shape[0]] = ['Nmap_added', '',ip[0],'','','']
    df.to_csv(path, index=False)
    return df
            

def generate_ip(path:str, subnet:str)->pd.DataFrame:
    '''
    Returns next free ip and saves it into reserved list.
    '''
    df=pd.read_csv(path)
    network = IPv4Network(subnet)
    hosts_iterator = [str(host) for host in network.hosts() if str(host) not in df.loc[:,'IP'].values]
    df.loc[df.shape[0], 'IP'] = hosts_iterator[0]
    df.loc[df.shape[0]-1,'Устройство'] = input("Device name:")
    df.loc[df.shape[0]-1,'MAC адрес'] = input("MAC:")
    df.loc[df.shape[0]-1,'Описание'] = input("Description:")
    df.loc[df.shape[0]-1,'Ответственный'] = input("Who is in charge:")
    df.loc[df.shape[0]-1,'Серийный номер'] = input("Serial number:")
    print(f'Your IP: {hosts_iterator[0]}')
    df.to_csv(path, index=False)


def remove_ip(path:str, ip:str)->str:
    '''
    Removes ip from reserved list.
    '''
    df=pd.read_csv(path)
    if ip in df['IP']:
        df.drop(df[df["IP"]==ip].index, inplace=True)
        df.to_csv(path, index=False)
    else:
        print('No such IP')




if __name__=='__main__':
    chat_ids = set()
    subnet = '192.168.4.0/24'
    path = '/home/andrew/Documents/generate_ip/reserved_list.csv'
    #generate_list(reserved_list_path, subnet)
    #generate_ip(path,subnet)
    remove_ip(path, 'lskdjfsdkjf')

    