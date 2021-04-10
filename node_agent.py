import docker,json,os,time

class Agent:


    def __init__(self):
        self.client = docker.from_env()
        self.existing_containers_cache=[]
        self.spec_path="/var/run"
        self.new_containers=[]

    def getHostContainers(self):
        all_containers=self.client.containers.list(filters={"label": "type=GCS"})
        del self.existing_containers_cache[:]
        for container in all_containers:
            self.existing_containers_cache.append(container.name)


    def getSpecContainers(self):
        for filename in os.listdir(self.spec_path):
            if filename.endswith(".json"):
                file_loc=self.spec_path+"/"+filename;
                file_stream=open(file_loc, "r")
                raw_container_spec = file_stream.read()
                try:
                    container_spec = json.loads(raw_container_spec)
                    self.new_containers.append(container_spec)
                except ValueError:
                    print("Decoding JSON has failed")

    def deleteContainer(self,name1):
        container1=self.client.containers.list(filters={'name': name1})
        container1[0].stop()
        container1[0].remove()
        print("Deleted Container ",name1)

    def createContainer(self,name1,port1,image1,volume1,labels1):
        container=self.client.containers.run(name=name1,image=image1,ports=port1,volumes=volume1,labels=labels1,detach=True)
        print("Created Container ",name1)
        return container

    def checkChangeInContainers(self):
        for service in self.existing_containers_cache:
            flag=False
            for spec_service in self.new_containers:
                if service == spec_service["name"]:
                    flag=True
                    break
            if not flag:
                self.deleteContainer(service)

        for spec_service in self.new_containers:
            spec_service_name = spec_service["name"]
            flag=False
            if spec_service_name in self.existing_containers_cache:
                flag=True
                
            if not flag:
                if "port" not in spec_service:
                    spec_service["port"]=""
                if "volume" not in spec_service:
                    spec_service["volume"]=""
                self.createContainer(spec_service["name"],spec_service["port"],spec_service["image"],spec_service["volume"],spec_service["labels"])


    def run(self):
        while True:
            del self.existing_containers_cache[:]
            del self.new_containers[:]
            self.getHostContainers()
            self.getSpecContainers()
            self.checkChangeInContainers()
            time.sleep(5)


p1 = Agent()
p1.run()
