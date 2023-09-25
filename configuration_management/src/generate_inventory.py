def generate_inventory(inventory_content, host_name):
    host_line = f"{host_name} ansible_connection=ansible.netcommon.httpapi ansible_user=admin ansible_password=NokiaSrl1! ansible_network_os=nokia.srlinux.srlinux"
    inventory_content.append(host_line)
    return inventory_content