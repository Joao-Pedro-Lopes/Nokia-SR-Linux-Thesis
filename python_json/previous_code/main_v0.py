import sys
import json

filename = sys.argv[-1]

cfg_dict = {}

interface_cfg_template = {
    "name": "",
    "description": "",
    "admin_state": "enable",
}

subinterface_cfg_template = {
    "index": "",
    "admin-state": "enable",
    "ipv4": {
        "address": [
            {
                "ip-prefix": ""
            }
        ]
    }
}

def removeNewLine(value):
    return ''.join(value.splitlines())

with open(filename) as topo_file:
    i = 0
    for line in topo_file:
        print(i)
        base = line.lstrip() #remove spaces from the beggining of the line

        if (cfg_dict):
            els = list(cfg_dict.items())
            
        if (base.startswith("leaf") or base.startswith("spine")):
            base = removeNewLine(base).split(":")[0]
            cfg_dict[base] = {} #add a new network device config   
        
        if (base.startswith("interface:")):
            base_aux = base.split(": ", )
            flag = base_aux[0]
            content = removeNewLine(base_aux[1])

            #print(els[-1])
            #print(flag, content)

            content_list = list(content.split(", "))

            for interface in content_list:
                interface_cfg = interface_cfg_template.copy() #to avoid write over the same dict
                interface_cfg["name"] = interface
                if (flag in cfg_dict[els[-1][0]]):
                    cfg_dict[els[-1][0]][flag].append(interface_cfg)
                else:
                    cfg_dict[els[-1][0]][flag] = list()
                    cfg_dict[els[-1][0]][flag].append(interface_cfg)
        
        if (base.startswith("subinterface:")):
            base_aux = base.split(": ", )
            flag = base_aux[0]
            content = removeNewLine(base_aux[1])

            #print(els[-1])
            #print(flag, content)

            content_list = list(content.split(", "))
            interface_pos = 0
            for subinterface in content_list:
                subinterface_cfg = subinterface_cfg_template.copy() #to avoid write over the same dict
                subinterface_cfg["index"] = subinterface
                #print(cfg_dict[els[-1][0]]["interface"][interface_pos])
                #interface_pos += 1
                if (flag in cfg_dict[els[-1][0]]["interface"][interface_pos]):
                    cfg_dict[els[-1][0]]["interface"][interface_pos][flag].append(subinterface_cfg)
                    interface_pos += 1
                else:
                    cfg_dict[els[-1][0]]["interface"][interface_pos][flag] = list()
                    cfg_dict[els[-1][0]]["interface"][interface_pos][flag].append(subinterface_cfg)
                    interface_pos += 1

        """ if (base.startswith("ipv4-address:")): #error in variables behind
            base_aux = base.split(": ", )
            flag_aux = base_aux[0].split("-")
            flag_ipv4 = flag_aux[0]
            flag_address = flag_aux[1]
            content = removeNewLine(base_aux[1])

            #print(els[-1])
            #print(flag_ipv4, flag_address, content)

            content_list = list(content.split(", "))
            pos = 0
            for ip in content_list:
                print(ip)
                print(cfg_dict[els[-1][0]]["interface"][pos])
                cfg_dict[els[-1][0]]["interface"][0]["subinterface"][0][flag_ipv4][flag_address][0]["ip-prefix"] = ip
                print(cfg_dict[els[-1][0]])
                pos += 1 """

        i+= 1

            


""" print(cfg_dict["leaf1"])
print(cfg_dict["leaf2"])
print(cfg_dict["spine1"]) """

#print(cfg_dict)

json_object = json.dumps(cfg_dict["leaf1"], indent = 4) 
print(json_object)
