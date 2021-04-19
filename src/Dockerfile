FROM python:3.9.4
RUN pip install etcd3 pyvim python-etcd requests netifaces docker
RUN apt-get update -y
RUN apt-get install net-tools -y
RUN mkdir -p /var/specs
COPY master_agent.py /bin/.
COPY node_agent.py /bin/.
CMD ["python","/bin/master_agent.py"]
