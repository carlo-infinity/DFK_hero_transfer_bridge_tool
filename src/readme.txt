How to use
----------

1. Open config.ini with any text editor to change the settings
* Do not paste private key in the config.ini

- Set the mode to transfer or bridge hero
- Set the receiver address to the account that will receive the hero
- For bridging, set the receiver address to be the same as your sender address
- Set whether you want to send all heroes, or input your heroes in heroes.txt
- For bridging only, set the origin realm to bridge from, i.e., if you are
  sending from Harmony to DFKchain, then set it to be 'serendale'

2. Double click hero_transfer_bridge_tool to run the software

3. Program may take a while to start (~1 minute, be patient)

4. Follow the instruction on the screen

5. Paste your account private key when prompted, and press enter when done (Note: your private key will not shown on the screen)
* For windows system, a single right click on the blank region means you have pasted your private key, just press enter right after

6. Continue follow the prompts on the screen

- Confirm by typing 'yes'
- Type 'yes all' to send your heroes without future confirmation
- For bridging, sometimes hero takes a while to arrive, type 'check' to check again if the hero has arrived, or type 'skip' to proceed with the next hero, any other text will stop the program

7. Once all heroes are transferred/bridged, check the summary to see if any hero has not been successfully transferred. Check log.txt to find out if there's any issue


Tips:
a. Verify the sha256 checksum (check against GitHub / Discord)
b. Try with a test account first to learn how to use this tool
c. Protect your private key at all cost and do not accidentally share it away. After you pasted your private key, copy some random text to remove the private key from clipboard




