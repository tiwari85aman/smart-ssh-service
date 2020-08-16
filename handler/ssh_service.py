import socket


class SshHandler(object):
    def __init__(self):
        self.filename = "/home/aman/.ssh/config"

    def read_config(self):
        with open(self.filename) as f:
            content = f.readlines()
        content = [x.strip() for x in content]

        final = {}
        properties = {}
        host = None
        for line in content:
            if line.strip() == "":
                continue
            value = line.split(" ")
            if value[0].upper() == "HOST":
                if properties:
                    final[host] = properties
                    properties = {"localForward": []}
                    host = value[1]
                else:
                    properties = {"localForward": []}
                    host = value[1]
            else:
                if value[0].upper() == "LOCALFORWARD":
                    temp = " ".join(value[1:])
                    binding = {"hostPort": temp.split(" ")[0],
                               "remoteIp": temp.split(" ")[1].split(":")[0],
                               "remotePort": temp.split(" ")[1].split(":")[1]}
                    properties["localForward"].append(binding)
                else:
                    properties[value[0]] = " ".join(value[1:])
        else:
            if properties:
                final[host] = properties
        return final

    def add_config(self, data):
        current_config = self.read_config()
        current_config[data.pop("Host")] = data
        with open(self.filename, mode="w+") as f:
            for host, config in current_config.items():
                f.writelines("HOST {}\n".format(host))
                for key, value in config.items():
                    if key.lower() == 'localforward':
                        for eachForward in value:
                            f.writelines(
                                "\tLocalForward {hostPort} {remoteIp}:{remotePort}\n".format(
                                    hostPort=eachForward["hostPort"],
                                    remoteIp=eachForward["remoteIp"],
                                    remotePort=eachForward[
                                        "remotePort"]))
                    else:
                        f.writelines("\t{key} {value}\n".format(key=key, value=value))
        return "Saved new host", True

    def edit_config(self, host, data):
        current_config = self.read_config()
        if host in current_config.keys():
            current_config.pop(host)
            current_config[data.pop("Host")] = data
            with open(self.filename, mode="w+") as f:
                for host, config in current_config.items():
                    f.writelines("HOST {}\n".format(host))
                    for key, value in config.items():
                        if key.lower() == 'localforward':
                            for eachForward in value:
                                f.writelines(
                                    "\tLocalForward {hostPort} {remoteIp}:{remotePort}\n".format(
                                        hostPort=eachForward["hostPort"],
                                        remoteIp=eachForward["remoteIp"],
                                        remotePort=eachForward[
                                            "remotePort"]))
                        else:
                            f.writelines("\t{key} {value}\n".format(key=key, value=value))
            return "Host updated", True
        else:
            return "Host doesn't exist", False

    def get_local_forward(self):
        config = self.read_config()
        forwarding = []
        for host, config in config.items():
            for each in config["localForward"]:
                each["host"] = host
            forwarding.extend(config["localForward"])
        return forwarding, True

    def get_ping_status(self):
        config = self.read_config()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = {"online": [], "offline": []}
        for host, config in config.items():
            socket_result = sock.connect_ex((config["Hostname"], int(config["Port"])))
            host_data = {"Host": host, "Hostname": config["Hostname"]}
            if socket_result:
                result["offline"].append(host_data)
            else:
                result["online"].append(host_data)
            sock.close()
        return result, True
