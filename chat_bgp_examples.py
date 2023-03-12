"network-instance": [
    {
      "name": "default",
      "interface": [
        {
          "name": "ethernet-1/1.0"
        },
        {
          "name": "ethernet-1/2.0"
        },
        {
          "name": "system0.0"
        }
      ],
      "protocols": {
        "bgp": {
          "autonomous-system": 201,
          "router-id": "10.0.1.1",
          "group": [
            {
              "group-name": "eBGP-underlay",
              "export-policy": "all",
              "import-policy": "all"
            }
          ],
          "ipv4-unicast": {
            "admin-state": "enable"
          },
          "neighbor": [
            {
              "peer-address": "192.168.11.1",
              "peer-as": 101,
              "peer-group": "eBGP-underlay"
            },
            {
              "peer-address": "192.168.12.1",
              "peer-as": 102,
              "peer-group": "eBGP-underlay"
            }
          ]
        }
      }
    },
    {
      "name": "mgmt",
      "type": "ip-vrf",
      "admin-state": "enable",
      "description": "Management network instance",
      "interface": [
        {
          "name": "mgmt0.0"
        }
      ],
      "protocols": {
        "linux": {
          "import-routes": true,
          "export-routes": true,
          "export-neighbors": true
        }
      }
    }
  ],
  "routing-policy": {
    "policy": [
      {
        "name": "all",
        "default-action": {
          "accept": {
          }
        }
      }
    ]
  }
}







"network-instance": [
  {
    "name": "default",
    "interface": [
      {
        "name": "ethernet-1/49.0"
      },
      {
        "name": "system0.0"
      }
    ],
    "protocols": {
      "bgp": {
        "autonomous-system": 101,
        "router-id": "10.0.0.1",
        "group": [
          {
            "group-name": "eBGP-underlay",
            "export-policy": "all",
            "import-policy": "all",
            "peer-as": 201
          }
        ],
        "ipv4-unicast": {
          "admin-state": "enable"
        },
        "neighbor": [
          {
            "peer-address": "192.168.11.2",
            "peer-group": "eBGP-underlay"
          }
        ]
      }
    }
  },
  {
    "name": "mgmt",
    "type": "ip-vrf",
    "admin-state": "enable",
    "description": "Management network instance",
    "interface": [
      {
        "name": "mgmt0.0"
      }
    ],
    "protocols": {
      "linux": {
        "import-routes": true,
        "export-routes": true,
        "export-neighbors": true
      }
    }
  }
],
"routing-policy": {
  "policy": [
    {
      "name": "all"
    }
  ]
}


""" 
leaf1
{
  "protocols:bgp": {
    "autonomous-system": 101,
    "router-id": "10.0.0.1",
    "group": {
      "eBGP-underlay": {
        "export-policy": "all",
        "import-policy": "all",
        "peer-as": 201,
        "neighbor": {
          "192.168.11.2": {}
        }
      }
    },
    "ipv4-unicast": {
      "admin-state": "enable"
    }
  }
} """


""" 
spine 1
{
  "protocols:bgp": {
    "autonomous-system": 201,
    "router-id": "10.0.1.1",
    "group": {
      "eBGP-underlay": {
        "export-policy": "all",
        "import-policy": "all",
        "neighbor": {
          "192.168.11.1": {
            "peer-as": 101
          },
          "192.168.12.1": {
            "peer-as": 102
          }
        }
      }
    },
    "ipv4-unicast": {
      "admin-state": "enable"
    },
    "neighbor": {
      "192.168.11.1": {
        "peer-group": "eBGP-underlay"
      },
      "192.168.12.1": {
        "peer-group": "eBGP-underlay"
      }
    }
  }
} """


enter candidate
    /routing-policy {
        policy all {
            default-action {
                policy accept
            }
        }
    }
    /tunnel-interface vxlan1 {
        vxlan-interface 1 {
            type bridged
            ingress {
                vni 1
            }
        }
    }
    /network-instance default {
        interface ethernet-1/49.0 {
        }
        interface system0.0 {
        }
        protocols {
            bgp {
                autonomous-system 101
                router-id 10.0.0.1
                group eBGP-underlay {
                    export-policy all
                    import-policy all
                    peer-as 201
                    ipv4-unicast {
                        admin-state enable
                    }
                }
                group iBGP-overlay {
                    export-policy all
                    import-policy all
                    peer-as 100
                    ipv4-unicast {
                        admin-state disable
                    }
                    evpn {
                        admin-state enable
                    }
                    local-as 100 {
                    }
                    timers {
                        minimum-advertisement-interval 1
                    }
                }
                neighbor 10.0.0.2 {
                    admin-state enable
                    peer-group iBGP-overlay
                    transport {
                        local-address 10.0.0.1
                    }
                }
                neighbor 192.168.11.2 {
                    peer-group eBGP-underlay
                }
            }
        }
    }

    /network-instance vrf-1 {
        type mac-vrf
        admin-state enable
        interface ethernet-1/1.0 {
        }
        vxlan-interface vxlan1.1 {
        }
        protocols {
            bgp-evpn {
                bgp-instance 1 {
                    admin-state enable
                    vxlan-interface vxlan1.1
                    evi 111
                }
            }
            bgp-vpn {
                bgp-instance 1 {
                    route-target {
                        export-rt target:100:111
                        import-rt target:100:111
                    }
                }
            }
        }
    }

    /interface ethernet-1/1 {
        vlan-tagging true
        subinterface 0 {
            type bridged
            admin-state enable
            vlan {
                encap {
                    untagged {
                    }
                }
            }
        }
    }
    /interface ethernet-1/49 {
        subinterface 0 {
            ipv4 {
                address 192.168.11.1/30 {
                }
            }
        }
    }
    /interface system0 {
        admin-state enable
        subinterface 0 {
            ipv4 {
                address 10.0.0.1/32 {
                }
            }
        }
    }
commit now
