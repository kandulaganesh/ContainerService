import json,requests,os,time

class MasterAgent:
    def apiRequest(self, operation, path, payload=None, name=None):
        '''
            url format: http://127.0.0.1:2379/v2/keys/fooDir/
        '''
        url = self._url(path)
        resp = None
        if operation == "GET":
            resp = requests.get('{}{}'.format(url,name))
        if operation == "PUT":
            resp = requests.put('{}{}'.format(url,name), data=payload)
        if operation == "DELETE":
            resp = requests.delete('{}{}'.format(url,name))
        return resp

    def _url(self, path):
        return 'http://127.0.0.1:2379/v2/keys/' + path + '/'

    def convert_json_to_string(self, json_data):
        str_data = json.dumps(json_data)
        return str_data

    def convert_string_to_json(self, string_data):
        json_data = json.loads(string_data)
        return json_data

    def post_new_service_in_etcd(self, service_name, service):
        str_service=self.convert_json_to_string(service)
        payload={'value':str_service}
        self.apiRequest("PUT","unscheduled",payload,service_name)

    def scheduled_service_on_node(self,node_id,container_spec_in_json):
        path="scheduled/node{}".format(node_id)
        conatiner_spec_in_str=self.convert_json_to_string(container_spec_in_json)
        payload={'value':conatiner_spec_in_str}
        self.apiRequest("PUT",path,payload,container_spec_in_json["name"])

    def schedule_the_unscheduled_containers(self):
        containers=self.apiRequest("GET","unscheduled",None,"")
        containers=containers.json()
        for container in containers['node']['nodes']:
            svc_spec=container['value']
            svc_spec=self.convert_string_to_json(svc_spec)
            self.scheduled_service_on_node(1,svc_spec)

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
        for container in spec_containers:
            self.post_new_service_in_etcd(container["name"],container)

    def run(self):
        while True:
            spec_containers=self.get_new_services()
            self.post_spec_to_etcd(spec_containers)
            self.scheduler()
            time.sleep(15)

p1=MasterAgent()
p1.run()
