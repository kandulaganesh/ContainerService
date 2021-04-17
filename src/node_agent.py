import docker,json,os,time,requests

class Agent:


    def __init__(self):
        self.client = docker.from_env()
        self.existing_containers_cache=[]
        self.new_containers=[]
        self.nodeId=0

    def getHostContainers(self):
        all_containers=self.client.containers.list(filters={"label": "type=GCS"})
        del self.existing_containers_cache[:]
        for container in all_containers:
            self.existing_containers_cache.append(container.name)

    def convert_string_to_json(self, string_data):
        json_data = json.loads(string_data)
        return json_data

    def marshal_the_code(self,service_info_in_json):
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

    def getSpecContainers(self):
        resp=None
        url="http://172.17.0.50:2379/v2/keys/scheduled/node{}".format(self.nodeId)
        try:
            resp = requests.get(url)
        except:
            resp=None
            print("Failed to connect to etcd")
        if resp == None:
            return self.existing_containers_cache
        containers=resp.json()
        self.new_containers = self.marshal_the_code(containers)

    def deleteContainer(self,name1):
        container1=self.client.containers.list(filters={'name': name1})
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

        temp=self.new_containers
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
        while True:
            del self.existing_containers_cache[:]
            del self.new_containers[:]
            self.getHostContainers() # Call first Host Containers and then Spec Containers
            self.getSpecContainers()
            self.checkChangeInContainers()
            time.sleep(5)


p1 = Agent()
p1.run()
