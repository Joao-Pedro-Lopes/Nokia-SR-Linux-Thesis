#!/bin/bash

#full configuration script
docker run --network host --rm -it \
    -v $(pwd):/ansible \
    -v ~/.ssh:/root/.ssh \
    -v /etc/hosts:/etc/hosts \
    ghcr.io/hellt/ansible:6.6.0 ansible-playbook -i inventory-full.yml $@

#individual configuration script
#docker run --network host --rm -it \
#    -v $(pwd):/ansible \
#    -v ~/.ssh:/root/.ssh \
#    -v /etc/hosts:/etc/hosts \
#    ghcr.io/hellt/ansible:6.6.0 ansible-playbook -i inventory-individual.yml $@

# to test out container 
# docker run --rm -it \
#     -v $(pwd):/ansible \
#     -v ~/.ssh:/root/.ssh \
#     -v /etc/hosts:/etc/hosts \
#     --entrypoint bash \
#     ghcr.io/hellt/ansible:6.6.0
