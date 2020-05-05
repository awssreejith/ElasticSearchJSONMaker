import sys
import os
import time
try:
    import xml.sax
except:
    print("xml parser load error")
    
sev_1_Map = {}
sev_2_Map = {}
sev_3_Map = {}
sev_4_Map = {}
  
sev_Array = (None,sev_1_Map,sev_2_Map,sev_3_Map,sev_4_Map)
global_id  = ""
global_severity = ""
        
class CPPUnitResult( xml.sax.ContentHandler ):
    def __init__(self):
        self.CurrentData = ""
        self.authTot = ""
        self.authUrg = ""
        self.total = ""

   # Call when an element starts
    def startElement(self, tag, attributes):
        global sev_Array 
        global global_id
        global global_severity
        
        intTotal = 0
        intSeverity = 0
        self.CurrentData = tag
        authTot = ""
        authUrg = ""
        total = ""
        category = ""
        description = ""
        id = ""
        severity = ""
        if tag == "Rule":
            category = attributes["cat"]
            description = attributes["desc"]
            id = attributes["id"]
            severity = attributes["sev"]
            global_id = id
                
            global_severity = severity
            
        if tag == "Stats":
            authTot = attributes["authTot"]
            authUrg = attributes["authUrg"]
            total = attributes["total"]
            if len(global_id) > 0 and len(global_severity) > 0 and len(total) > 0:
                intTotal = int(total)
                intSeverity = int(global_severity)
                
            if intSeverity > 0:
                sev_Array[intSeverity][global_id] = intTotal
            global_id  = ""
            global_severity = ""
                

    def characters(self, content):
        if self.CurrentData == "authTot":
            self.authTot = content
        elif self.CurrentData == "authUrg":
            self.authUrg = content
        elif self.CurrentData == "total":
            self.total = content
            
#####Our XML parseReader and json popuator class

class JSONCreator():
    def __init__(self,component,XMLParser,XMLfile, Handler):
        self.parser     = XMLParser
        self.Handler    = Handler
        self.XMLfile    = XMLfile
        self.component  = component
        self.outFile    = None
        fileName        = "ElasticSearchInsertFile."+self.component
        
        self.parser.setFeature(xml.sax.handler.feature_namespaces, 0)
        self.parser.setContentHandler(self.Handler)
        
        try:
            self.outFile = open(fileName,"w");
        except:
            print("Error in opening output JSON file. Program exiting")
            sys.exit(-3)
     

    def parse(self):
        print("Parsing the "+self.XMLfile+" file"+"\n")
        self.parser.parse(self.XMLfile)
        
    
    def createTableJSON(self):
        severityVal = 0
        total = 0
        for ele in sev_Array:
            if ele != None:
                severityVal+=1
                print("Creating document data for Severity - "+str(severityVal)+" warnings"+"\n")
                for ele2 in ele:
                    if ele[ele2] > 0:
                        total = ele[ele2]+total
                        for idx in range(0,ele[ele2]):
                            self.outFile.write("{\"index\":{}}"+"\n")
                            self.outFile.write("{"+"\"Error_Type\" : "+"\""+ele2 +"\""+","+"\"Severity\" : "+str(severityVal)+"}"+"\n")
        return total,self.outFile
    
''' 

DON'T USE THIS FUNCTION. THIS IS AN EXPERIMENTAL ROUTINE!!!
def insertTableIntoIndex(component,host,port):

    idxName = "/staticanalysis_"+component
    deleteCommand = "curl -H \"Content-Type: application/json\" -XDELETE "+host+":"+str(port)+idxName
    print("Deleting the previous index. If there are no previous index, the script will simply return warning JSON. No Action required")
    os.system(deleteCommand)
    
    #create new documents
    print ("Creating new index with the populated document")
    docName = "severity"
    createCommand = "curl -H \"Content-Type: application/json\" -XPOST "+host+":"+str(port)+idxName+"/"+docName+"/_bulk --data-binary  @ElasticSearchInsertFile.txt"
                     
    os.system(createCommand)
    print("\n"+"\n"+"script sleeps for 30 seconds till entire data is inserted"+"\n"+"\n")
    time.sleep(30)
    print("Insert completed. Please verify using the below command in a command prompt.It must show a field named count with non zero value")
    print("curl -H \"Content-Type: application/json\" -XGET "+host+":"+str(port)+idxName+"/"+"_count")
'''   
    

    
if  __name__ == "__main__":

    goAhead = True if len(sys.argv) == 3 else False
    if(goAhead == False):
        print("Usage Error")
        sys.exit(-1)
   

    parser    = xml.sax.make_parser() 
    Handler   = CPPUnitResult()   
    xmlfile   = sys.argv[1]
    component = sys.argv[2]
    host      = "localhost" #experimental
    port      = 9200 #experimental
    idxName   = "/staticanalysis_"+component
    docName   = "severity"
    
    JSONcreator = JSONCreator(component, parser, xmlfile, Handler)  

    try:
        JSONcreator.parse()
    except:
        print("Error in parsing XML file. Program exiting")
        sys.exit(-2)
        
    print("Input XML file parsed succesfully")   

    total,outFile = JSONcreator.createTableJSON()
       
    print("Total rows to be inserted = "+str(total)+"\n")
    print ("Run the below command to insert the data in Elastic Search DB"+"\n")
    
    print("curl -H \"Content-Type: application/json\" -XPOST "+host+":"+str(port)+idxName+"/"+docName+"/_bulk --data-binary @"+outFile.name)
