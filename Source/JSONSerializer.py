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

    def __init__(self):
        """
        ObjectTypeCalls is part of the process for restoring objects from JSON.  It should only be manipulated from implementations of the RegisterObjectType method of SerializableMixin.
        """
        self.ObjectTypeCalls = {}

    def SerializeDataToJSONString(self, Data, Indent=2):
        return json.dumps(Data, cls=Encoder, indent=Indent)

    def DeserializeDataFromJSONString(self, JSONString):
        return json.loads(JSONString, cls=lambda: Decoder(self.ObjectTypeCalls))


class SerializableMixin(metaclass=abc.ABCMeta):
    """
    Inherit from this class, call its __init__ method, and implement its abstract methods to allow any custom object to be serialized and deserialized.

    See the docstrings of the abstract methods for details on what they should do.
    """

    def __init__(self):
        self.RegisterObjectType()

    @abc.abstractmethod
    def RegisterObjectType(self):
        """
        This method should add a callable to the serializer's ObjectTypeCalls dictionary that returns an object of the type to be serialized.  For example:

        JSONSerializerObject.ObjectTypeCalls[self.__class__.__name__] = lambda DecodedObjectData: self.__class__(DecodedObjectData)

        This callable is used when deserializing from a JSON string, to reconstitute objects.

        Note that the data provided to the callable will be in the form of the data returned by the GetState method, so any parameters necessary for creating the object need to be included and parsed out from that data.
        """
        pass

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
