This is a script which will populate JSON data to be inserted in to an ElasticSearch DB.

The data will be populated from ParaSoft CPPUnit static code analyser result. The static code analyser will
product the output in xml format. What we do here is Read and parse the xml and populate an array of dictionary
where each index represents the severity of the error. Under each dictionary we store the warning type and count of the
specific warning type.

[[{severity_1_type_1:count},{severity_1_type_2:count},...],[{severity_2_type_1:count},{severity_2_type_2:count},...]]


Once the above array of dictionary is created, we iterate through each dictionary and extract the count variable .Then create the JSON
insert statement for that particular warning message that number of times.

Note: The input XML file is not attached with this because of confidentiality obligations. The sample JSON input file which can be used
to insert the data into Elastis search is also attached. How to insert the data in to elastic search will be displayed once this
script is executed.
To run this script issue the command as below

python JSONMaker.py OUTPUT_FILE_CREATED_BY_PARASOFTANALYZER.xml COMPONENT_NAME

This will create a file called ElasticSearchInsertFile.COMPONENT_NAME 

To insert in to Elastic search execute the below command

curl -H "Content-Type: application/json" -XPOST localhost:9200/staticanalysis_comp/severity/_bulk --data-binary @ElasticSearchInsertFile.COMPONENT_NAME

Where 
Localhost:9200        ==> machine where Elastic search is running

9200                  ==> port where it is listening

staticanalysis_comp   ==> index name 

severity              ==> type



