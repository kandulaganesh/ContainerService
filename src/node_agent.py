import docker,json,os,time,requests

class Agent:


    def __init__(self):
        self.client = docker.from_env()
        self.existing_containers_cache=[]
        self.new_containers=[]
        self.nodeId=0
        self.floating_ip="172.17.0.50"

    def apiRequest(self,operation="GET"):
        resp=None
        url="http://{}:2379/v2/keys/scheduled/node{}".format(self.floating_ip,self.nodeId)
        try:
            if operation == "GET":
                resp = requests.get(url)
            elif operation == "PUT":
                url="http://{}:2379/v2/keys/nodestatus/node{}/healthy".format(self.floating_ip,self.nodeId)
                payload={"value": "true","ttl": 20}
                resp=requests.put(url,data=payload)
        except:
            print("Failed to connect to etcd")
        return resp

    def getHostContainers(self):
        all_containers=self.client.containers.list(all=True,filters={"label": "type=GCS"})
        del self.existing_containers_cache[:]
        for container in all_containers:
            self.existing_containers_cache.append(container.name)

    def convert_string_to_json(self, string_data):
        json_data = json.loads(string_data)
        return json_data

    def marshal_the_code(self,service_info_in_json):
        containers = []
        if "errorCode" in service_info_in_json:
            return None
        if "nodes" not in service_info_in_json['node']:
            return containers
        for service in service_info_in_json['node']['nodes']:
            svc_spec = service['value']
            svc_spec = self.convert_string_to_json(svc_spec)
            containers.append(svc_spec)
        return containers

    def convert_response_to_json(self,response):
        try:
            response=response.json()
        except:
           response={"errorCode": "Failed to Decode json"}
        return response

    def getSpecContainers(self):
        resp=self.apiRequest()
        containers=self.convert_response_to_json(resp)
        temp = self.marshal_the_code(containers)
        if temp != None:
            del self.new_containers[:]
            self.new_containers=temp
       
    def deleteContainer(self,name1):
        container1=self.client.containers.list(all=True,filters={'name': name1})
        container1[0].stop()
        container1[0].remove()
        print("Deleted Container ",name1)

    def createContainer(self,name1,port1,image1,volume1,labels1):
        labels1["nodeId"]=str(labels1["nodeId"])
        container=None
        try:
            container=self.client.containers.run(name=name1,image=image1,ports=port1,volumes=volume1,labels=labels1,detach=True)
            print("Created Container ",name1)
        except:
            print("Failed to Create Container ",name1)
        return container

    def nodeRegistration(self):
        self.apiRequest("PUT")

    def checkChangeInContainers(self):
        temp=self.existing_containers_cache.copy()
        for service in temp:
            flag=False
            for spec_service in self.new_containers:
                if service == spec_service["name"]:
                    flag=True
                    break
            if not flag:
                self.deleteContainer(service)
                self.existing_containers_cache.remove(service)

        temp=self.new_containers.copy()
        for spec_service in temp:
            spec_service_name = spec_service["name"]
            flag=False
            if spec_service_name in self.existing_containers_cache:
                flag=True
                
            if not flag:
                if "port" not in spec_service:
                    spec_service["port"]=""
                if "volume" not in spec_service:
                    spec_service["volume"]=""
                self.createContainer(spec_service["name"],spec_service["port"],
                                     spec_service["image"],spec_service["volume"],
                                     spec_service["labels"])
                self.existing_containers_cache.append(spec_service)

    def run(self):
        self.nodeId=os.environ.get('nodeId')
        if "floating_ip" in os.environ:
            self.floating_ip=os.environ["floating_ip"]
        while True:
            self.nodeRegistration()
            self.getHostContainers() # Call first Host Containers and then Spec Containers
            self.getSpecContainers()
            self.checkChangeInContainers()
            time.sleep(5)


p1 = Agent()
p1.run()
