import abc
import json


class JSONSerializer:
    """
    This class is designed to serialize and deserialize arbitrary object data in JSON format.

    The serialized data must either adhere to the normal JSON structures or be an object inheriting from SerializableMixin (and implementing its methods properly).

    Likewise, data returned by the GetState method of SerializableMixin inheritors must adhere to these restrictions.

    To serialize data, just call the SerializeDataToJSONString method, which returns the JSON string.

    To deserialize data from a JSON string, call the DeserializeDataFromJSONString method, which returns the reconstituted data structure.
    """

    def __init__(self, ObjectClasses=()):
        """
        ObjectClasses should be a tuple of classes to be serialized; a dictionary is created from them that allows the Decoder to reconstitute the objects from states.
        """
        self.ObjectClasses = ObjectClasses
        self.ObjectTypeCalls = {}
        for ObjectClass in ObjectClasses:
            self.ObjectTypeCalls[ObjectClass.__name__] = lambda State, ObjectClass=ObjectClass: ObjectClass.CreateFromState(State)

    def SerializeDataToJSONString(self, Data, Indent=2):
        return json.dumps(Data, cls=Encoder, indent=Indent)

    def DeserializeDataFromJSONString(self, JSONString):
        return json.loads(JSONString, cls=lambda: Decoder(self.ObjectTypeCalls))


class SerializableMixin(metaclass=abc.ABCMeta):
    """
    Inherit from this class, call its __init__ method, and implement its abstract methods to allow any custom object to be serialized and deserialized.

    See the docstrings of the abstract methods for details on what they should do.
    """

    @abc.abstractmethod
    def SetState(self, NewState):
        """
        This method should set the state of the object, parsing whatever GetState returns.

        For example, if GetState returns a string attribute of the object, SetState should assign that string.
        """
        pass

    @abc.abstractmethod
    def GetState(self):
        """
        This method should capture the state of the object and return it.

        For example, a GUI object like a single-line text edit widget should return its contents as a string.
        """
        pass

    @classmethod
    @abc.abstractmethod
    def CreateFromState(cls, State):
        """
        This method should create a new instance of the class, set its state, and return the instance.
        """
        pass


class Encoder(json.JSONEncoder):
    def default(self, EncodedObject):
        if isinstance(EncodedObject, SerializableMixin):
            Data = {}
            Data["ObjectData"] = EncodedObject.GetState()
            Data["ObjectType"] = EncodedObject.__class__.__name__
            return Data
        return super().default(EncodedObject)


class Decoder(json.JSONDecoder):
    def __init__(self, ObjectTypeCalls):
        self.ObjectTypeCalls = ObjectTypeCalls
        super().__init__(object_hook=self.ObjectHook)

    def ObjectHook(self, DecodedObject):
        if "ObjectType" not in DecodedObject or "ObjectData" not in DecodedObject:
            return DecodedObject
        ObjectType = DecodedObject["ObjectType"]
        return self.ObjectTypeCalls[ObjectType](DecodedObject["ObjectData"])
