def routing_policy():
    policy = {
        'policy': [
            {
                'name':'all', #node_data['config']['vars']['routing-policy']
                'default-action': {
                    'policy-result': 'accept' #node_data['config']['vars']['routing-policy-action']
                }
            }
        ]
    }
    return policy