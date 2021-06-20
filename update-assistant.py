#
#
# main() will be run when you invoke this action
#
# @param Cloud Functions actions accept a single parameter, which must be a JSON object.
#
# @return The output of this action, which must be a JSON object.
#
#
import sys, json
import pandas as pd
import csv
import os
import types
from botocore.client import Config
import ibm_boto3
#from ibm_watson import AssistantV1
from watson_developer_cloud import AssistantV1
from watson_developer_cloud import DiscoveryV1
#from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


def main(dict):
    
    discovery = DiscoveryV1(
    version='2019-04-30',
    iam_apikey=dict['discovery_key'])
    
    assistant = AssistantV1( version='2020-04-01', iam_apikey= dict['assistant_key'])
    
    services_dict=extractInfoFromDiscovery(discovery,dict)
    createFile(services_dict, dict)
    
    entities_list= list(services_dict.keys())
    updateAssistant(assistant,entities_list, dict)
    
 
    
    """
    response=assistant.create_dialog_node(
    workspace_id=dict['workspace_id'],
    dialog_node='test',
    conditions="#plans",
    #previous_sibling='node_2_1591571634368',
    output= l,
    title='Greetings2',
    node_type='frame',
     
    ).get_result()"""
    
    
    
    
    """
    response=assistant.get_dialog_node(
    workspace_id=dict['workspace_id'],
    dialog_node='node_2_1591571634368'
    ).get_result()"""

   
    
    return { 'message': 'hey' }
    

#Extracting info from discovery (plan title and description)    
def extractInfoFromDiscovery(discovery,dict):
    services={}
    query=discovery.query(dict["environment_id"], dict["collection_id"], passages=True, offset=1)
    n= query.result['matching_results']-1
    
    
    for i in range(n):
        title= query.result['results'][i]['title'][0]
        description = query.result['results'][i]['text']
        services[title] = description
        
    return services    
    
#Create CSV file that has the extracting info and upload it to COS    
def createFile(services_dict, dict):
    client = ibm_boto3.client(service_name='s3',
    ibm_api_key_id=dict['cos_key'],
    ibm_service_instance_id= dict['cos_service_id'],
   # ibm_auth_endpoint="https://iam.eu-gb.bluemix.net/oidc/token",
    config=Config(signature_version='oauth'),
    endpoint_url="https://s3.us-south.objectstorage.service.networklayer.com")
    
    body = client.get_object(Bucket='etipoc-cos',Key='ServiceList.csv')['Body']
    if not hasattr(body, "__iter__"): body.__iter__ = types.MethodType( __iter__, body )
    
    cols=['entity','description']
    table=pd.DataFrame(columns= cols)  
    for k,v in services_dict.items():
         table=table.append({'entity':k.lower(), 'description':v}, ignore_index=True)
       
    #print('{}\n'.format(table))   
    
    table.to_csv('ServiceList2.csv', index=False)
    try:
        res=client.upload_file(Filename="ServiceList2.csv", Bucket='etipoc-cos',Key='ServiceList.csv')
    except Exception as e:
        print(Exception, e)
    else:
        print('File Uploaded')

#Get only titles of plans to use them as entities        
def getEntities(entities_list):
    #print (entities_list)
    plans_name=[]
    for entity in entities_list:
        plans_name.append(CreateValue(entity))
    return plans_name    

#Updating the Assistant services'entity with the values that
#We got from getEntities function
def updateAssistant(assistant, entities_list, dict):
    response= assistant.update_entity(
    workspace_id=dict['workspace_id'],
    entity='services',
    new_values= getEntities(entities_list)
    ).get_result()
    
    updateServicesNodeOptions(assistant, entities_list, dict)
    
    #print(response)
    

#Access the Services dialog node and update the option labels and values    
def updateServicesNodeOptions(assistant, entities_list ,dict):
    
    option_elements=[]

    for entity in entities_list:
        option_value= DialogNodeOutputOptionsElementValue(InputData(entity))
        option_elements.append(DialogNodeOutputOptionsElement(entity,option_value))
    
    output_generic= [DialogNodeOutputGeneric("option", options=option_elements, title="Choose a plan:")]
    response=assistant.update_dialog_node(
    workspace_id=dict['workspace_id'],
    dialog_node='node_2_1591984644503',
    new_output= DialogNodeOutput(output_generic)  ,
    ).get_result()
   
    
    
    
    
    
class CreateValue(object):
    """
    CreateValue.

    :attr str value: The text of the entity value. This string must conform to the following restrictions:  - It cannot contain carriage return, newline, or tab characters.  - It cannot consist of only whitespace characters.  - It must be no longer than 64 characters.
    :attr object metadata: (optional) Any metadata related to the entity value.
    :attr list[str] synonyms: (optional) An array containing any synonyms for the entity value. You can provide either synonyms or patterns (as indicated by **type**), but not both. A synonym must conform to the following restrictions:  - It cannot contain carriage return, newline, or tab characters.  - It cannot consist of only whitespace characters.  - It must be no longer than 64 characters.
    :attr list[str] patterns: (optional) An array of patterns for the entity value. You can provide either synonyms or patterns (as indicated by **type**), but not both. A pattern is a regular expression no longer than 128 characters. For more information about how to specify a pattern, see the [documentation](https://console.bluemix.net/docs/services/conversation/entities.html#creating-entities).
    :attr str value_type: (optional) Specifies the type of value.
    """

    def __init__(self,
                 value,
                 metadata=None,
                 synonyms=None,
                 patterns=None,
                 value_type=None):
        """
        Initialize a CreateValue object.

        :param str value: The text of the entity value. This string must conform to the following restrictions:  - It cannot contain carriage return, newline, or tab characters.  - It cannot consist of only whitespace characters.  - It must be no longer than 64 characters.
        :param object metadata: (optional) Any metadata related to the entity value.
        :param list[str] synonyms: (optional) An array containing any synonyms for the entity value. You can provide either synonyms or patterns (as indicated by **type**), but not both. A synonym must conform to the following restrictions:  - It cannot contain carriage return, newline, or tab characters.  - It cannot consist of only whitespace characters.  - It must be no longer than 64 characters.
        :param list[str] patterns: (optional) An array of patterns for the entity value. You can provide either synonyms or patterns (as indicated by **type**), but not both. A pattern is a regular expression no longer than 128 characters. For more information about how to specify a pattern, see the [documentation](https://console.bluemix.net/docs/services/conversation/entities.html#creating-entities).
        :param str value_type: (optional) Specifies the type of value.
        """
        self.value = value
        self.metadata = metadata
        self.synonyms = synonyms
        self.patterns = patterns
        self.value_type = value_type

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a CreateValue object from a json dictionary."""
        args = {}
        if 'value' in _dict:
            args['value'] = _dict['value']
        else:
            raise ValueError(
                'Required property \'value\' not present in CreateValue JSON')
        if 'metadata' in _dict:
            args['metadata'] = _dict['metadata']
        if 'synonyms' in _dict:
            args['synonyms'] = _dict['synonyms']
        if 'patterns' in _dict:
            args['patterns'] = _dict['patterns']
        if 'value_type' in _dict:
            args['value_type'] = _dict['value_type']
        if 'type' in _dict:
            args['value_type'] = _dict['type']
        return cls(**args)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata
        if hasattr(self, 'synonyms') and self.synonyms is not None:
            _dict['synonyms'] = self.synonyms
        if hasattr(self, 'patterns') and self.patterns is not None:
            _dict['patterns'] = self.patterns
        if hasattr(self, 'value_type') and self.value_type is not None:
            _dict['type'] = self.value_type
        return _dict

    def __str__(self):
        """Return a `str` version of this CreateValue object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other
        
        
        
        
class DialogNodeOutput(object):
    """
    The output of the dialog node. For more information about how to specify dialog node
    output, see the
    [documentation](https://cloud.ibm.com/docs/services/assistant/dialog-overview.html#complex).

    :attr list[DialogNodeOutputGeneric] generic: (optional) An array of objects describing
    the output defined for the dialog node.
    :attr DialogNodeOutputModifiers modifiers: (optional) Options that modify how
    specified output is handled.
    """

    def __init__(self, generic=None, modifiers=None, **kwargs):
        """
        Initialize a DialogNodeOutput object.

        :param list[DialogNodeOutputGeneric] generic: (optional) An array of objects
        describing the output defined for the dialog node.
        :param DialogNodeOutputModifiers modifiers: (optional) Options that modify how
        specified output is handled.
        :param **kwargs: (optional) Any additional properties.
        """
        self.generic = generic
        self.modifiers = modifiers
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DialogNodeOutput object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'generic' in _dict:
            args['generic'] = [
                DialogNodeOutputGeneric._from_dict(x)
                for x in (_dict.get('generic'))
            ]
            del xtra['generic']
        if 'modifiers' in _dict:
            args['modifiers'] = DialogNodeOutputModifiers._from_dict(
                _dict.get('modifiers'))
            del xtra['modifiers']
        args.update(xtra)
        return cls(**args)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'generic') and self.generic is not None:
            _dict['generic'] = [x._to_dict() for x in self.generic]
        if hasattr(self, 'modifiers') and self.modifiers is not None:
            _dict['modifiers'] = self.modifiers._to_dict()
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def __setattr__(self, name, value):
        properties = {'generic', 'modifiers'}
        if not hasattr(self, '_additionalProperties'):
            super(DialogNodeOutput, self).__setattr__('_additionalProperties',
                                                      set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(DialogNodeOutput, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this DialogNodeOutput object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other    
        
        
class DialogNodeOutputGeneric(object):
  
    def __init__(self,
                 response_type,
                 values=None,
                 selection_policy=None,
                 delimiter=None,
                 time=None,
                 typing=None,
                 source=None,
                 title=None,
                 description=None,
                 preference=None,
                 options=None,
                 message_to_human_agent=None):
       
        self.response_type = response_type
        self.values = values
        self.selection_policy = selection_policy
        self.delimiter = delimiter
        self.time = time
        self.typing = typing
        self.source = source
        self.title = title
        self.description = description
        self.preference = preference
        self.options = options
        self.message_to_human_agent = message_to_human_agent

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DialogNodeOutputGeneric object from a json dictionary."""
        args = {}
        if 'response_type' in _dict:
            args['response_type'] = _dict.get('response_type')
        else:
            raise ValueError(
                'Required property \'response_type\' not present in DialogNodeOutputGeneric JSON'
            )
        if 'values' in _dict:
            args['values'] = [
                DialogNodeOutputTextValuesElement._from_dict(x)
                for x in (_dict.get('values'))
            ]
        if 'selection_policy' in _dict:
            args['selection_policy'] = _dict.get('selection_policy')
        if 'delimiter' in _dict:
            args['delimiter'] = _dict.get('delimiter')
        if 'time' in _dict:
            args['time'] = _dict.get('time')
        if 'typing' in _dict:
            args['typing'] = _dict.get('typing')
        if 'source' in _dict:
            args['source'] = _dict.get('source')
        if 'title' in _dict:
            args['title'] = _dict.get('title')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'preference' in _dict:
            args['preference'] = _dict.get('preference')
        if 'options' in _dict:
            args['options'] = [
                DialogNodeOutputOptionsElement._from_dict(x)
                for x in (_dict.get('options'))
            ]
        if 'message_to_human_agent' in _dict:
            args['message_to_human_agent'] = _dict.get('message_to_human_agent')
        return cls(**args)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'response_type') and self.response_type is not None:
            _dict['response_type'] = self.response_type
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = [x._to_dict() for x in self.values]
        if hasattr(self,
                   'selection_policy') and self.selection_policy is not None:
            _dict['selection_policy'] = self.selection_policy
        if hasattr(self, 'delimiter') and self.delimiter is not None:
            _dict['delimiter'] = self.delimiter
        if hasattr(self, 'time') and self.time is not None:
            _dict['time'] = self.time
        if hasattr(self, 'typing') and self.typing is not None:
            _dict['typing'] = self.typing
        if hasattr(self, 'source') and self.source is not None:
            _dict['source'] = self.source
        if hasattr(self, 'title') and self.title is not None:
            _dict['title'] = self.title
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'preference') and self.preference is not None:
            _dict['preference'] = self.preference
        if hasattr(self, 'options') and self.options is not None:
            _dict['options'] = [x._to_dict() for x in self.options]
        if hasattr(self, 'message_to_human_agent'
                  ) and self.message_to_human_agent is not None:
            _dict['message_to_human_agent'] = self.message_to_human_agent
        return _dict

    def __str__(self):
        """Return a `str` version of this DialogNodeOutputGeneric object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other
        
class DialogNodeOutputOptionsElement(object):
    """
    DialogNodeOutputOptionsElement.

    :attr str label: The user-facing label for the option.
    :attr DialogNodeOutputOptionsElementValue value: An object defining the message input
    to be sent to the Watson Assistant service if the user selects the corresponding
    option.
    """

    def __init__(self, label, value):
        """
        Initialize a DialogNodeOutputOptionsElement object.

        :param str label: The user-facing label for the option.
        :param DialogNodeOutputOptionsElementValue value: An object defining the message
        input to be sent to the Watson Assistant service if the user selects the
        corresponding option.
        """
        self.label = label
        self.value = value

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DialogNodeOutputOptionsElement object from a json dictionary."""
        args = {}
        if 'label' in _dict:
            args['label'] = _dict.get('label')
        else:
            raise ValueError(
                'Required property \'label\' not present in DialogNodeOutputOptionsElement JSON'
            )
        if 'value' in _dict:
            args['value'] = DialogNodeOutputOptionsElementValue._from_dict(
                _dict.get('value'))
        else:
            raise ValueError(
                'Required property \'value\' not present in DialogNodeOutputOptionsElement JSON'
            )
        return cls(**args)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'label') and self.label is not None:
            _dict['label'] = self.label
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value._to_dict()
        return _dict

    def __str__(self):
        """Return a `str` version of this DialogNodeOutputOptionsElement object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DialogNodeOutputOptionsElementValue(object):
    """
    An object defining the message input to be sent to the Watson Assistant service if the
    user selects the corresponding option.

    :attr InputData input: (optional) An input object that includes the input text.
    """

    def __init__(self, input=None):
        """
        Initialize a DialogNodeOutputOptionsElementValue object.

        :param InputData input: (optional) An input object that includes the input text.
        """
        self.input = input

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DialogNodeOutputOptionsElementValue object from a json dictionary."""
        args = {}
        if 'input' in _dict:
            args['input'] = InputData._from_dict(_dict.get('input'))
        return cls(**args)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'input') and self.input is not None:
            _dict['input'] = self.input._to_dict()
        return _dict

    def __str__(self):
        """Return a `str` version of this DialogNodeOutputOptionsElementValue object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other
        
class InputData(object):
    """
    An input object that includes the input text.

    :attr str text: The text of the user input. This string cannot contain carriage
    return, newline, or tab characters, and it must be no longer than 2048 characters.
    """

    def __init__(self, text, **kwargs):
        """
        Initialize a InputData object.

        :param str text: The text of the user input. This string cannot contain carriage
        return, newline, or tab characters, and it must be no longer than 2048 characters.
        :param **kwargs: (optional) Any additional properties.
        """
        self.text = text
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InputData object from a json dictionary."""
        args = {}
        xtra = _dict.copy()
        if 'text' in _dict:
            args['text'] = _dict.get('text')
            del xtra['text']
        else:
            raise ValueError(
                'Required property \'text\' not present in InputData JSON')
        args.update(xtra)
        return cls(**args)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'text') and self.text is not None:
            _dict['text'] = self.text
        if hasattr(self, '_additionalProperties'):
            for _key in self._additionalProperties:
                _value = getattr(self, _key, None)
                if _value is not None:
                    _dict[_key] = _value
        return _dict

    def __setattr__(self, name, value):
        properties = {'text'}
        if not hasattr(self, '_additionalProperties'):
            super(InputData, self).__setattr__('_additionalProperties', set())
        if name not in properties:
            self._additionalProperties.add(name)
        super(InputData, self).__setattr__(name, value)

    def __str__(self):
        """Return a `str` version of this InputData object."""
        return json.dumps(self._to_dict(), indent=2)

    def __eq__(self, other):
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other        
    
    


    
    

