
from time import time, sleep
from urllib import response
import requests
import xml.etree.ElementTree as ET 

magma_calc_url = "http://magma.maths.usyd.edu.au/xml/calculator.xml"

class MagmaResponse:
    def __init__(self, response):
        self.response = response
        self.headers = {}
        self.results = []
        self.has_error = False
        self.__parse__magma(response)
        
    """
        <calculator>
        <headers>
            <max_time>120</max_time>
            <max_input>50000</max_input>
            <seed>295288489</seed>
            <version>2.28-12</version>
            <time>0.010</time>
            <memory>32.09MB</memory>
            <warning>An error occurred. See the output for details.</warning>
        </headers>
        <results>
            <line>9</line>
            <line/>
            <line>>> sleep(1500)</line>
            <line>   ^</line>
            <line>User error: Identifier 'sleep' has not been declared or assigned</line>
            <line/>
        </results>
        </calculator>  
    """
    def __parse__magma(self, response):
        root = ET.fromstring(response)
        for child in root:
            if child.tag == 'headers':
                for header in child:
                    self.headers[header.tag] = header.text
                    if header.tag == 'warning':
                        self.has_error = True
            elif child.tag == 'results':
                for result in child:
                    if result.text is not None:
                        self.results.append(result.text)
        return self    
        
    def get_results(self, raise_error=True):
        if self.has_error and raise_error:
            raise Exception(f"Error in Magma: {self.results}")
        return self.results
        
last_request_time = time() - 30
def invoke_online_command(command):
    """
    Invokes the online magma calculator with the given command.
    """
    # global last_request_time
    
    # if time() - last_request_time < 10:
    #     sleep(30)
    # last_request_time = time()
    r = requests.post(magma_calc_url, data={'input': command})
    
    return MagmaResponse(r.text)


# res = invoke_online_command("""
#                     a:=2;
#                     b:=3;
#                     a+b  
#                       """)

# print(res.get_results())