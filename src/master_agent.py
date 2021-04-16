import json,requests,os,time,netifaces

class MasterAgent:

    def apiRequest(self, operation, path, payload=None, name=None, base_path="keys"):
        '''
            url format: http://127.0.0.1:2379/v2/keys/fooDir
        '''
        url = self._url(path, base_path)
        resp = None
        try:
            if operation == "GET":
                resp = requests.get('{}{}'.format(url,name))
            if operation == "PUT":
                resp = requests.put('{}/{}'.format(url,name), data=payload)
            if operation == "DELETE":
                resp = requests.delete('{}/{}'.format(url,name))
        except:
            print("Failed to connect to etcd")
        return resp

    def _url(self, path, base_path):
        url = "http://127.0.0.1:2379/v2/{}/{}".format(base_path,path)
        return url

    def convert_json_to_string(self, json_data):
        str_data = json.dumps(json_data)
        return str_data

    def convert_string_to_json(self, string_data):
        json_data = json.loads(string_data)
        return json_data

    def post_new_service_in_etcd(self, json_service):
        service_name=json_service['name']
        str_service=self.convert_json_to_string(json_service)
        payload={'value':str_service}
        self.apiRequest("PUT","unscheduled",payload,service_name)

    def scheduled_service_on_node(self,node_id,container_spec_in_json):
        path="scheduled/node{}".format(node_id)
        container_spec_in_json["labels"]["nodeId"]=node_id
        conatiner_spec_in_str=self.convert_json_to_string(container_spec_in_json)
        payload={'value':conatiner_spec_in_str}
        self.apiRequest("PUT",path,payload,container_spec_in_json["name"])

    def delete_the_service_config_from_etcd(self, path, svc_spec_in_json):
        self.apiRequest("DELETE",path,None,svc_spec_in_json["name"])

    def marshal_the_code(self, service_info_in_json):
        containers = []
        if "errorCode" in service_info_in_json:
            return containers
        if "nodes" not in service_info_in_json['node']:
            return containers
        for service in service_info_in_json['node']['nodes']:
            svc_spec = service['value']
            svc_spec = self.convert_string_to_json(svc_spec)
            containers.append(svc_spec)
        return containers

    def schedule_the_unscheduled_containers(self):
        containers=self.apiRequest("GET","unscheduled",None,"")
        if containers == None:
            return
        containers=containers.json()
        containers=self.marshal_the_code(containers)
        for container in containers:
            self.scheduled_service_on_node(1,container)
            self.delete_the_service_config_from_etcd("unscheduled",container)

    def scheduler(self):
        self.schedule_the_unscheduled_containers()

    def get_new_services(self):
        new_containers=[]
        spec_path="/var/specs"
        for filename in os.listdir(spec_path):
            if filename.endswith(".json"):
                file_loc=spec_path+"/"+filename
                file_stream=open(file_loc, "r")
                raw_container_spec = file_stream.read()
                try:
                    container_spec = json.loads(raw_container_spec)
                    new_containers.append(container_spec)
                except ValueError:
                    print("Decoding JSON has failed")
        return new_containers

    def post_spec_to_etcd(self, spec_containers):
        self.post_new_service_in_etcd(spec_containers)

    def get_service_config_of_node_from_etcd(self, node_id):
        path="scheduled/node{}".format(node_id)
        containers=self.apiRequest("GET",path,None,"")
        if containers == None:
            return []
        containers=containers.json()
        containers = self.marshal_the_code(containers)
        return containers

    def get_service_config_from_etcd(self):
        config_containers = []
        container=self.get_service_config_of_node_from_etcd(1)
        config_containers.extend(container)
        return config_containers

    def is_current_etcd_leader(self):
        resp = self.apiRequest("GET","self",None,"","stats")
        if resp == None:
            return False
        data=resp.json()
        if data["state"] == "StateLeader":
            return True
        return False

    def config_floating_ip(self, is_leader):
        netifaces.ifaddresses('eth_float')
        is_float_ip = netifaces.AF_INET in netifaces.ifaddresses('eth_float')
        if is_leader:
            if is_float_ip == False:
                print("Floating ip found is 0.0.0.0")
                os.system("ifconfig eth_float 172.17.0.50 netmask 255.255.255.255")
        else:
            if is_float_ip == True:
                print("Floating ip found is 172.17.0.50")
                os.system("ip addr del 172.17.0.50/32 dev eth_float")

    def compare_config(self, spec_containers, config_containers):
        index=-1
        for service in config_containers:
            index=index+1
            flag=False
            for spec_service in spec_containers:
                if service["name"] == spec_service["name"]:
                    flag=True
                    break
            if not flag:
                node_id=service["labels"]["nodeId"]
                path="scheduled/node{}".format(node_id)
                print("Deleting Service ",service["name"])
                self.delete_the_service_config_from_etcd(path,service)
                config_containers.pop[index]

        for spec_service in spec_containers:
            spec_service_name = spec_service["name"]
            flag=False
            for service in config_containers:
                if spec_service_name == service['name']:
                    flag=True
            if not flag:
                if "port" not in spec_service:
                    spec_service["port"]=""
                if "volumes" not in spec_service:
                    spec_service["volumes"]=""
                print("Found new service ",spec_service["name"])
                self.post_spec_to_etcd(spec_service)
                config_containers.append(spec_service)

    def run(self):
        while True:
            is_leader=self.is_current_etcd_leader()
            print("Am i leader ",is_leader)
            if is_leader:
                spec_containers=self.get_new_services()
                config_containers=self.get_service_config_from_etcd()
                self.compare_config(spec_containers, config_containers)
                self.scheduler()
            self.config_floating_ip(is_leader)
            time.sleep(15)

p1=MasterAgent()
p1.run()
