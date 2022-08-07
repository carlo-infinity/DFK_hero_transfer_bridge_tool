# This script is ported directly from jupyter notebook prototype, the organisation in
# the .py version may be not as intuitive, suggest to port it back to notebook format
# to view it better
# 
# This tool requires the open source DFK library from https://github.com/0rtis/dfktools
# (22 July 2022 version). Additionally, a modification to the library is required and
# is stated below.
# 
# Please do not distribute this source code directly, but instead share the github link
# containing the code. This is to discourage sharing of code and software directly which
# may lead to malicious actors trying to scam the others through modified code.
#
# Thank you, hope this tool may be of use to you. - Carlo Infinity

### Please apply the following changes to meditation.py  (added contract_address as input)

#     def get_hero_meditation(hero_id, contract_address, rpc_address):
#         w3 = Web3(Web3.HTTPProvider(rpc_address))
#
#         contract_address = Web3.toChecksumAddress(contract_address)
#         contract = w3.eth.contract(contract_address, abi=ABI)
#
#         result = contract.functions.getHeroMeditation(hero_id).call()
#         if result[0] == 0:
#             return None
#         return result

print('''
------------------------------------------------------
DISCLAIMER

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY 
OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT 
LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS 
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO 
EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE 
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, 
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, 
ARISING FROM, OUT OF OR IN CONNECTION WITH THE 
SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
------------------------------------------------------
''')

print('''
Welcome to using the hero transfer/bridge tool. 
This is a free software provided by Carlo Infinity, 
the founder of DFK auto FARM waifu project. This 
tool allows you to mass transfer or bridge your 
heroes without requiring clicking or through metamask. 

Please make sure you have read everything (readme.txt, 
disclaimer.txt, github) before proceeding. Make sure 
that you have downloaded the program from official 
github page and verify the sha256 checksum. DO NOT USE 
if you suspect the software has been tampered with.

If this is your first time using, suggest to try with 
a test account first to familiarise.

(C) Copyright by Carlo Infinity. All rights reserved.

''')

print('Tool is initialising...')
print()

import os
import sys
import logging
import configparser
import getpass

from web3 import Web3
import requests
import time
import datetime

from auctions.auction import Auction
import auctions.hero.sale_auctions as hero_sales
import auctions.hero.rent_auctions as hero_rental

from hero.hero import Hero
import hero.hero_core as hero_core
import bridge.hero_bridge as hero_bridge
import meditation.meditation as meditation

import quests.quest_v1 as quest_v1
import quests.quest_v2 as quest_v2

import quests.quest_core_v1 as quest_core_v1
import quests.quest_core_v2 as quest_core_v2

from quests.utils import utils as quest_utils

log_format = '%(asctime)s|%(name)s|%(levelname)s: %(message)s'

logger = logging.getLogger("DFK-quest")
logger.setLevel(logging.DEBUG)
logger.disabled = True  # disable logging

##### System function

def confirm_exit():
    time.sleep(0.05)
    exit_text = getpass.getpass('Press enter to exit the program...')
    raise Exception('Program has stopped.')

def time_now():
    return datetime.datetime.now().isoformat(' ', 'seconds')

##### Users have to agree to the terms before using

print('''
Please read and agree with the terms of usage:

1. Only use the official software downloaded from github
2. Make sure your computer is free of malware
3. Exercise caution when dealing with your private key
4. Do not distribute the software or code to others 
     (instead, you may share the official github link)
5. Carlo Infinity takes no responsibility on any incidents
   that occur from using this software. Be it from your
   own mistake or from an unintended bug. Do your due 
   diligence and check the source code on github.

''')

time.sleep(0.05)
input_text   = input('To agree and proceed, type "yes" and press enter: ')
confirmation = input_text.replace('"','').replace("'",'').lower().strip()

if confirmation != 'yes':
    print('You have typed "{}", tool will not proceed'.format(input_text))
    confirm_exit()

##### Load config from config.ini

print('Reading config.ini...')

config_filename = 'config.ini'

if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
else:
    application_path = os.path.abspath('')

config_location = os.path.join(application_path, config_filename)

conf = configparser.ConfigParser()
conf.read(config_location)

conf.sections()

def get_conf_var(subject, key, fallback=None):
    if subject in conf:
        return conf[subject].get(key, fallback)
    else:
        return fallback

def get_conf_bool(subject, key, fallback=None):
    if subject in conf:
        return conf[subject].getboolean(key, fallback)
    else:
        return fallback

try:
    ########################
    ##### MAIN SETTING #####
    ########################
    
    # mode = 'transfer' or 'bridge'
    mode = get_conf_var('Settings', 'mode', 'transfer').lower().replace('"', '').replace("'",'').strip()
    
    # receiver address of the sent heroes
    receiver_address = get_conf_var('Settings', 'receiver_address', '0x0000000000000000000000000000000000000000').replace('"', '').replace("'",'').strip()

    # whether to send all heroes
    flag_send_all = get_conf_bool('Settings', 'send_all_heroes', False)
    
    # bridging option: bridge from which realm? 
    bridge_from = get_conf_var('Bridging', 'bridge_from', 'serendale').lower().replace('"', '').replace("'",'').strip()
    
    
    ### RPC for Harmony
    rpc_harmony = get_conf_var('Harmony RPC', 'rpc_server', 'https://api.harmony.one').replace('"', '').replace("'",'').strip()
    
    # gas gwei, stop and warning limit
    harmony_gas_gwei = float(get_conf_var('Harmony RPC', 'gas_gwei', 105))

    
    ### RPC for DFKchain
    rpc_dfkchain = get_conf_var('DFKchain RPC', 'rpc_server', 'https://subnets.avax.network/defi-kingdoms/dfk-chain/rpc').replace('"', '').replace("'",'').strip()
    
    # gas gwei, stop and warning limit
    dfkchain_gas_gwei = float(get_conf_var('DFKchain RPC', 'gas_gwei', 1.6))
    
    ###################
    ##### ADVANCE #####
    ###################
    
    ### Bridge Fee
    sd_bridge_fee = float(get_conf_var('Bridge Fee', 'sd_bridge_fee', 0.016))
    cv_bridge_fee = float(get_conf_var('Bridge Fee', 'cv_bridge_fee', 0.004))
                          
except Exception as e:
    print('config.ini is not in correct format, please double check...')
    print('Error: [{}]'.format(e))
    confirm_exit()

print('config.ini loaded...')


# validate the settings
print('Validating the settings from config...')

if mode not in ['transfer', 'bridge']:
    print('Mode [{}] is not supported'.format(mode))
    confirm_exit()

if receiver_address == '0x0000000000000000000000000000000000000000':
    print('Please input a valid receiver_address [incorrect 0x: {}]'.format(receiver_address))
    confirm_exit()
    
if mode == 'bridge' and bridge_from not in ['serendale', 'crystalvale']:
    print('Incorrect bridge_from setting: [{}] not supported'.format(bridge_from))
    confirm_exit()

# convert receiver_address to Web3 toChecksumAddress
try:
    receiver_address = Web3.toChecksumAddress(receiver_address)
except Exception as e:
    print('Error when converting receiver_address to checksum')
    print('Error: [{}]'.format(e))
    confirm_exit()

##### Get the list of heroes to be sent

heroes_filename = 'heroes.txt'
heroes_file_location = os.path.join(application_path, heroes_filename)

heroes = []
if not flag_send_all:
    # read in text from heroes.txt
    i = 0
    with open(heroes_file_location, 'r') as f:
        for line in f:
            i += 1
            line = line.replace(',', ' ').replace('\t', ' ').strip()
            
            # skip comments or empty line
            if line == '' or line[0] == '#':
                continue
            
            # extract hero_id from line
            try:
                splitted = line.split(' ')
                hero_id  = int(splitted[0])
                heroes += [hero_id]
            
            except Exception as e:
                print('Error occurred at line {}: [{}]'.format(i, e))
                print('Text that caused error: "{}"'.format(line))
                confirm_exit()
                
    print('heroes.txt loaded, {} heroes will be sent'.format(len(heroes)))

##### General Utility Tool

log_filename = 'log.txt'
log_file_location = os.path.join(application_path, log_filename)

# write text to log file (open and close as needed since users might close at any time)
def log(text):
    with open(log_file_location, 'a') as f:
        f.write(text)
        f.write('\n')

# write to log file as well as print to stdout
def print_log(text):
    print(text)
    log(str(text))
    

graphql = 'https://defi-kingdoms-community-api-gateway-co06z8vi.uc.gateway.dev/graphql'

def query_graphql(query, graphql_address):
    max_try = 5
    while max_try > 0:
        try:
            r = requests.post(graphql_address, json={'query': query}, timeout=30)
            if r.status_code != 200:
                raise Exception("HTTP error " + str(r.status_code) + ": " + r.text)
            data = r.json()
            return data['data']
        except Exception as e:
            max_try -= 1
            if max_try == 0:
                raise e
            print(e)
            print('Retrying after 5 seconds')
            time.sleep(5)

# query strings
str_query_network = '''
query {
  hero(id: %s) {
    id
    network
  }
}
'''

str_query_profile_name = '''
query {
  profile(id: "%s") {
    id
    name
  }
}    
'''

SD = 'serendale'
CV = 'crystalvale'

tx_timeout = 180

class DFK_tool():
    
    rpc = {
        SD: rpc_harmony,
        CV: rpc_dfkchain
    }
    
    w3 = {
        SD: Web3(Web3.HTTPProvider(rpc[SD])),
        CV: Web3(Web3.HTTPProvider(rpc[CV]))
    }
    
    gas_gwei = {
        SD: harmony_gas_gwei,
        CV: dfkchain_gas_gwei
    }
    
    hero_tool = {
        SD: Hero(hero_core.SERENDALE_CONTRACT_ADDRESS,   rpc[SD], logger), 
        CV: Hero(hero_core.CRYSTALVALE_CONTRACT_ADDRESS, rpc[CV], logger)
    }
    
    sale_auction = {
        SD: Auction(hero_sales.SERENDALE_CONTRACT_ADDRESS  , rpc[SD], logger),
        CV: Auction(hero_sales.CRYSTLAVALE_CONTRACT_ADDRESS, rpc[CV], logger)
    }
    
    rent_auction = {
        SD: Auction('0x65DEA93f7b886c33A78c10343267DD39727778c2', rpc[SD], logger),
        CV: Auction('0x8101CfFBec8E045c3FAdC3877a1D30f97d301209', rpc[CV], logger)
    }
    
    # bridge_info
    bridge = {
        SD: {
            'contract': hero_bridge.SERENDALE_CONTRACT_ADDRESS, # sender contract
            'chain_id': hero_bridge.CRYSTALVALE_CHAIN_ID,       # receiver chain id
            'cost'    : w3[SD].toWei(sd_bridge_fee, 'ether')
        },
        CV: {
            'contract': hero_bridge.CRYSTALVALE_CONTRACT_ADDRESS, # sender contract
            'chain_id': hero_bridge.SERENDALE_CHAIN_ID,           # receiver chain id
            'cost'    : w3[CV].toWei(cv_bridge_fee, 'ether')
        }
    }
    
    questV2 = {
        SD: quest_v2.Quest(quest_core_v2.SERENDALE_CONTRACT_ADDRESS, rpc[SD], logger),
        CV: quest_v2.Quest(quest_core_v2.CRYSTALVALE_CONTRACT_ADDRESS, rpc[CV], logger)
    }
    
    questV1 = {
        SD: quest_v1.Quest(rpc[SD], logger),
        CV: None
    }
    
    meditation_contract = {
        SD: meditation.CONTRACT_ADDRESS,
        CV: '0xD507b6b299d9FC835a0Df92f718920D13fA49B47'
    }
    
    
    ### query from graphql    
    # query the realm hero is in
    def query_realm(self, hero_id):
        query = str_query_network % hero_id
        hero = query_graphql(query, graphql)['hero']
        network = hero['network']
        return 'serendale' if network == 'hmy' else 'crystalvale'
    
    # query an 0x address' profile name
    def query_profile_name(self, account_address):
        query = str_query_profile_name % account_address
        profile = query_graphql(query, graphql)['profile']
        profile_name = profile['name']
        return profile_name
        
        
    ### query from blockchain
    # get account 0x from private key
    def get_account_address(self, private_key, realm):
        return self.w3[realm].eth.account.privateKeyToAccount(private_key).address
    
    # get nonce from account
    def get_nonce(self, account_address, realm):
        return self.w3[realm].eth.getTransactionCount(account_address)
    
    # get all heroes from an account (not on tavern)
    def get_users_heroes(self, account_address, realm):
        return self.hero_tool[realm].get_users_heroes(account_address)
    
    # get all heroes for sale from an account
    def get_sale_heroes(self, account_address, realm):
        return self.sale_auction[realm].get_user_auctions(account_address)
    
    # return whether the account owns the hero
    def have_hero(self, hero_id, account_address, realm):
        return self.hero_tool[realm].get_owner(hero_id) == account_address
    
    ### hero utility
    # transfer a hero to an address
    def transfer_hero(self, hero_id, private_key, receiver_address, realm):
        # make sure sender and receiver address are different
        account_address = self.get_account_address(private_key, realm)
        if account_address == receiver_address:
            raise Exception('ERROR: Sender and receiver address is the same!')            
        max_try = 5
        while max_try > 0:
            try:
                nonce = self.get_nonce(account_address, realm)
                self.hero_tool[realm].transfer(hero_id, private_key, nonce, receiver_address, 
                                               self.gas_gwei[realm], tx_timeout)
                print_log('Hero {} is transferred to {}'.format(hero_id, receiver_address))
                return
            except Exception as e:
                print_log(e)
                max_try -= 1
            
        
    # bridge a hero to another realm
    def bridge_hero(self, hero_id, private_key, origin_realm):
        realm = origin_realm
        account_address = self.get_account_address(private_key, realm)    
        max_try = 5
        while max_try > 0:
            try:
                nonce = self.get_nonce(account_address, realm)
                tx = hero_bridge.send_hero(self.bridge[realm]['contract'], hero_id, self.bridge[realm]['chain_id'],  
                                           self.bridge[realm]['cost'], private_key, nonce, self.gas_gwei[realm], 
                                           tx_timeout, self.rpc[realm], logger)
                transactionHash = tx['logs'][0]['transactionHash'].hex()
                print_log('Hero {} is bridged from {} to the other side'.format(hero_id, origin_realm))
                print_log('Transaction Hash: {}'.format(transactionHash))
                return transactionHash
            except Exception as e:
                if str(e) == 'execution reverted: ERC721: transfer caller is not owner nor approved':
                    raise e
                print_log(e)
                max_try -= 1               

    
    ### rental auction
    # check whether hero is on rent auction
    def is_for_hire(self, hero_id, realm):
        return self.rent_auction[realm].is_on_auction(hero_id)
    
    # unlist a hero from rental auction
    def unrent_hero(self, hero_id, private_key, realm):
        account_address = self.get_account_address(private_key, realm)
        max_try = 5
        while max_try > 0:
            try:
                nonce = self.get_nonce(account_address, realm)
                self.rent_auction[realm].cancel_auction(hero_id, private_key, nonce, self.gas_gwei[realm], tx_timeout)
                print_log('Hero {} unlisted for hire'.format(hero_id))
                return
            except Exception as e:
                print_log(e)
                max_try -= 1
    
    # check whether hero is on sale auction
    def is_for_sale(self, hero_id, realm):
        return self.sale_auction[realm].is_on_auction(hero_id)
    
    # unlist a hero from sales auction
    def unsell_hero(self, hero_id, private_key, realm):
        account_address = self.get_account_address(private_key, realm)
        max_try = 5
        while max_try > 0:
            try:
                nonce = self.get_nonce(account_address, realm)
                self.sale_auction[realm].cancel_auction(hero_id, private_key, nonce, self.gas_gwei[realm], tx_timeout)
                print_log('Hero {} unlisted for sale'.format(hero_id))
                return
            except Exception as e:
                print_log(e)
                max_try -= 1
                
        
    # check if hero is on meditation
    def is_on_meditation(self, hero_id, realm):
        if meditation.get_hero_meditation(hero_id, self.meditation_contract[realm], self.rpc[realm]):
            return True
        else:
            return False

    # get quest info
    def get_quest_info_v2(self, hero_id, realm):
        return quest_utils.human_readable_quest(self.questV2[realm].get_hero_quest(hero_id))

    def is_questing_v2(self, hero_id, realm):   # maybe obsolete? TODO: use is_hero_questing functionality
        quest_info = self.get_quest_info_v2(hero_id, realm)
        return True if quest_info else False     

    def get_quest_info_v1(self, hero_id, realm):
        return quest_utils.human_readable_quest(self.questV1[realm].get_hero_quest(hero_id))

    def is_questing_v1(self, hero_id, realm):   # maybe obsolete?
        quest_info = self.get_quest_info_v1(hero_id, realm)
        return True if quest_info else False
 
              

tool = DFK_tool()

##### setup private key

# get private key
try:
    print('')
    private_key = getpass.getpass('Please paste your private key (for windows, right click to paste) and press enter: ').strip()
    account_address = tool.get_account_address(private_key, CV)
except Exception as e:
    print('Error on private key')
    print('- Error: [{}]'.format(e))
    confirm_exit()
    
# get user's profile
try:
    username = tool.query_profile_name(account_address)
except Exception as e:
    time.sleep(1)
    print('Unable to get DFK username...')
    print('- Error: [{}]'.format(e))
    username = 'No username found'
    
print('Tool is set to {} heroes from account {} ({})'.format(mode, account_address, username))


# confirm destination address is the same for bridging, or different for transferring
if mode == 'bridge' and receiver_address != account_address:
    print('Config error: receiver address is not the same as your 0x address (for bridging)...')
    print('Sender 0x: {}'.format(account_address))
    print('Receiver 0x: {}'.format(receiver_address))
    confirm_exit()

if mode == 'transfer' and receiver_address == account_address:
    print('You cannot transfer heroes to the same account...')
    print('Sender 0x: {}'.format(account_address))
    print('Receiver 0x: {}'.format(receiver_address))
    confirm_exit()

##### Start hero transfer / bridge sequence

# get all heroes to be transferred/bridged if sending all heroes
if flag_send_all:
    heroes_SD = tool.get_users_heroes(account_address, SD)
    heroes_CV = tool.get_users_heroes(account_address, CV)
    sale_heroes_SD = tool.get_sale_heroes(account_address, SD)
    sale_heroes_CV = tool.get_sale_heroes(account_address, CV)
    
    if mode == 'transfer':
        heroes = heroes_SD + heroes_CV + sale_heroes_SD + sale_heroes_CV
    elif mode == 'bridge':
        if bridge_from == 'serendale':
            heroes = heroes_SD + sale_heroes_SD
        else:
            heroes = heroes_CV + sale_heroes_CV

# terminate program if there is no hero in the account
if len(heroes) == 0:
    print('Your 0x address does not have hero...')
    confirm_exit()

# get receiver's profile
try:
    receiver_name = tool.query_profile_name(receiver_address)
except Exception as e:
    receiver_name = 'No username found'

# confirm with user regarding bridging the heroes
print('')
text_num_hero = '{} hero{}'.format(len(heroes), 'es' if len(heroes) > 1 else '')
print('You will {} {} to {} ({})'.format(mode, text_num_hero, receiver_address, receiver_name))
print('* Heroes will be unlisted from sales and rental tavern before sending...')
print('* Heroes who are questing/meditating will not be sent')
print('')

time.sleep(0.05)
input_text   = input('Please check the 0x, and confirm by typing "yes" and press enter: ')
confirmation = input_text.replace('"','').replace("'",'').lower().strip()

if confirmation != 'yes':
    print('You have typed "{}", tool will not proceed'.format(input_text))
    confirm_exit()
    

print_log('--------------------------------------------------')
print_log('[{}]'.format(time_now()))

# check if hero reach the destination correctly
def check_received(hero_id, receiver_address, realm):
    print('Veriying the {} process...'.format(mode))
    received = False
    while not received:
        try:
            received = tool.hero_tool[realm].get_owner(hero_id) == receiver_address
        except Exception as e:
            print('Error during verification: [{}]'.format(e))
            received = False
        
        if not received:
            print('Hero {} has not reached the destination...'.format(hero_id))
            print('* If hero not bridged successfully after an hour, please open a ticket with Synapse')
            print('')
            time.sleep(0.05)
            input_text = input('Type "check" to check again, or "skip" to continue: ')
            input_text = input_text.replace('"','').replace("'",'').lower().strip()
               
            if input_text == 'skip':
                return
            elif input_text == 'check':
                continue
            else:
                print('You have typed "{}", tool will not proceed'.format(input_text))
                confirm_exit()
            
        else:
            print_log('Hero {} has successfully reached the destination'.format(hero_id))

# transfer a hero from a 0x to another
def execute_send_hero(hero_id, skip_confirmation=False):
    realm = tool.query_realm(hero_id) if mode == 'transfer' else bridge_from
    
    # skip if hero is questing
    if realm == SD:
        is_questing = tool.is_questing_v1(hero_id, realm) or tool.is_questing_v2(hero_id, realm)
    else:
        is_questing = tool.is_questing_v2(hero_id, realm)
        
    if is_questing:
        print_log('Skip hero {}: currently questing...'.format(hero_id))
        raise Exception('Skip Hero')
    
    # skip if hero is meditating
    is_meditating = tool.is_on_meditation(hero_id, realm)
    if is_meditating:
        print_log('Skip hero {}: currently on meditation...'.format(hero_id))
        raise Exception('Skip Hero')
    
    # unlist hero from sale or rental tavern
    if tool.is_for_hire(hero_id, realm):
        tool.unrent_hero(hero_id, private_key, realm)
    if tool.is_for_sale(hero_id, realm):
        tool.unsell_hero(hero_id, private_key, realm)
        
    # skip if hero do not belong to account
    if not tool.have_hero(hero_id, account_address, realm):
        print_log('Skip hero {}: not owned by account...'.format(hero_id))
        raise Exception('Skip Hero')
        
    # transfer or bridge the hero if own the hero
    if mode == 'transfer':
        tool.transfer_hero(hero_id, private_key, receiver_address, realm)
        dest_realm = realm
    elif mode == 'bridge':
        try:
            tx = tool.bridge_hero(hero_id, private_key, bridge_from)
            if tx:
                bridge_tx_id[hero_id] = tx
            dest_realm = CV if realm == SD else SD
        except Exception as e:
            if str(e) == 'execution reverted: ERC721: transfer caller is not owner nor approved':
                print_log('')
                print_log('Your account has not approve bridge hero transaction, please approve in dock!')
                raise Exception('Transaction Not Approved')
            print('Failed to bridge hero {}'.format(hero_id))
            print('- Error: [{}]'.format(e))
            return
        
    
    # check if hero is received
    if not skip_confirmation:
        check_received(hero_id, receiver_address, dest_realm)
    

# function to transfer or bridge a hero
def send_hero(hero_id, skip_confirmation=False):
    # use global definition of flag_skip
    global flag_skip
    
    # confirm with user to send the hero
    if not skip_confirmation:
        print('')
        print('The program will {} hero {} now'.format(mode, hero_id))
        time.sleep(0.05)
        input_text = input('Type "yes" to send this hero, type "yes all" to send all heroes without confirmation: ')
        confirmation = input_text.replace('"','').replace("'",'').lower().strip()
        
        if confirmation == 'yes all':
            skip_confirmation = True
            flag_skip = True
    
    # transfer or bridge the hero
    if skip_confirmation or confirmation == 'yes':
        try:
            execute_send_hero(hero_id, skip_confirmation)
        except Exception as e:
            if str(e) == 'Transaction Not Approved':
                confirm_exit()
            if str(e) == 'Skip Hero':
                return
            print('Error encountered when sending: [{}]'.format(e))
            
    else:
        print('You have typed "{}", tool will stop now...'.format(input_text))
        confirm_exit()

# keep a list of bridging tx id
bridge_tx_id = {}

# transfer or bridge the heroes
global flag_skip
flag_skip = False
for hero_id in heroes:
    # check if user want to confirm the sending
    send_hero(hero_id, flag_skip)

# verify once all heroes were sent
print_log('{} completed!'.format(mode))
print_log('')

if mode == 'bridge':
    dest_realm = CV if bridge_from == SD else SD

failed_heroes = []
for hero_id in heroes:
    if mode == 'transfer':
        try:
            realm    = tool.query_realm(hero_id)
            received = tool.have_hero(hero_id, receiver_address, realm)
        except Exception as e:
            received = False
    if mode == 'bridge':
        try:
            received = tool.have_hero(hero_id, receiver_address, dest_realm)
        except Exception as e:
            received = False
    if not received:
        failed_heroes += [hero_id]

if len(failed_heroes) >= 1:
    print_log("The following heroes are not in the receiver's 0x address:")
    print_log('* Please check whether they are questing/on meditation, see log.txt for details...')
    print_log('* If heroes are not successfully bridged within 1 hour, please open a ticket with Synapse (in Discord)')
    print_log('* Transaction Hash is also available in log.txt')
    print_log('')

    for hero_id in failed_heroes:
        print_log(str(hero_id))
        if mode == 'bridge':
            if hero_id in bridge_tx_id:
                print_log(bridge_tx_id[hero_id])
                print_log('')
else:
    print_log('All heroes have arrived their destination 0x address!')
    
confirm_exit()
                



