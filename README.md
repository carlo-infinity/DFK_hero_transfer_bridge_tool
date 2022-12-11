#### !! Please be noted this tool does not work for bridging to/from Klaytn chain (Serendale 2)


### DFK hero transfer bridge tool

Welcome. This is a simple tool to mass transfer and bridge heroes for the DFK game. It is a free tool provided by Carlo Infinity, the founder of the DFK auto FARM waifu project ([Discord](https://discord.com/invite/4kqXg5nBYe)). The tool is built with ease of use in mind, please do your due diligence and exercise standard security procedure when using the tool. Due to it being a free tool, support is not provided, please make sure you know what you are doing. Read all documents, including on how to use from readme.txt

#### Features

- Mass tranferring and bridging of your heroes in one setup
- Verifying of the receiver's DFK username
- Check whether heroes have successfully arrived at the destination 0x

#### Download

Executables for Windows, MacOS and Ubuntu are provided below together with their sha256 checksum. For security best practice, verify the checksum here as well as the ones posted in Discord.

[Windows](https://github.com/carlo-infinity/DFK_hero_transfer_bridge_tool/blob/main/hero-transfer-wins.zip)  
`b13af029be9efb4d3d7faa2c329dcb6817033d3b4b1ea16edcc9d4947f6df50e`

[MacOS](https://github.com/carlo-infinity/DFK_hero_transfer_bridge_tool/blob/main/hero-transfer-macos.zip)  
`e80b135d0f127b73620466232a05882f44f40a317d3b6dc0c9403ebcf4ede60b`

[Ubuntu](https://github.com/carlo-infinity/DFK_hero_transfer_bridge_tool/blob/main/hero-transfer-ubuntu.zip)  
`b0fffd98c258d8eaf50bd722172e69570095f6eadd3070daa374e9bd1eeb4e2a`


#### Dependency

If you want to use the code and modify for personal use, you will also need to get the [open source dfktools](https://github.com/0rtis/dfktools). The version used by our script is freezed on 22 July 2022. If you are using a newer version, you might need to modify based on the [changes](https://github.com/0rtis/dfktools/commits/master). Thank you 0rtis for providing such a wonderful tool.


#### Configuration

Change the settings in config.ini, you will need to open it by any text editor (notepad, textedit, etc). Adjust the settings based on your need. For bridging, you will need to set the receiver address to be the same as sender address, as well as whether you are bridging from which realm to which (serendale or crystalvale). Example below, the other settings are optional and you can just use the default.

```[Settings]
# choose between 'transfer' or 'bridge'
mode = 'transfer'

# please input the receiver's 0x address
# (input your own 0x for bridging)
receiver_address = '0x0000000000000000000000000000000000000000'

# whether to send (transfer or bridge) all heroes (true/false)
# if false, please input the hero ids in heroes.txt (1 per line)
send_all_heroes = true

[Bridging]
# set which realm to bridge from, choose 'serendale' or 'crystalvale'
# ignore this if you are transferring heroes only
# (note: not the destination)
bridge_from = 'serendale'
```

#### How to use

Please read the readme.txt on the details on how to use the program. Note that you will need to export your private key for the program to transfer/bridge your heroes. Please make your own judgement whether you want to export the private key of your main account. There is always more risk when you are exporting and handling your private key directly. 

If you feel that your private key is compromised (eg you pasted to discord), immediately take action and move all your assets to another account!
