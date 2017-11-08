from collections import OrderedDict


class Bitmask(object):

    def __init__(self, value, mask=None):
        self.value = value
        self.mask = mask

    def get_masked(self):
        if self.mask:
            return self.value & self.mask
        else:
            return self.value

    def __eq__(self, other):

        if isinstance(other, Bitmask):
            return self.value == other.value and self.mask == other.mask
        elif isinstance(other, (int, bytes)):
            if self.mask:
                return (self.value & self.mask) == (other & self.mask)
            else:
                return self.value == other

    def __lt__(self, other):

        if isinstance(other, Bitmask):
            return self.get_masked() < other.get_masked()
        elif isinstance(other, (int, bytes)):
            return self.get_masked() < other
        else:
            raise NotImplementedError("Not supported comparision")

    def __gt__(self, other):

        if isinstance(other, Bitmask):
            return self.get_masked() > other.get_masked()
        elif isinstance(other, (int, bytes)):
            return self.get_masked() > other
        else:
            raise NotImplementedError("Not supported comparision")

    def __hash__(self):
        return hash((self.value, self.mask))

    def __repr__(self):
        return "Bitmask({value}, {mask})".format(value=bin(self.value), mask=bin(self.mask) if self.mask else None)

    def __int__(self):
        return self.value


class BitmaskEnum(object):

    def __new__(cls, value):
        cls._attr_map = OrderedDict()

        # create a map name -> Bitmask|int
        for member in filter(lambda m: not m.startswith('_'), dir(cls)):
            attr = getattr(cls, member)
            if isinstance(attr, (Bitmask, int)):
                cls._attr_map[member] = attr

        return super(BitmaskEnum, cls).__new__(cls)

    def __init__(self, value):
        self._value = None
        self._name = None
        self._bitmask = None

        if isinstance(value, BitmaskEnum):
            value = value._value

        if isinstance(value, (Bitmask, int)):
            self._value = value

            for name, attr in self._attr_map.items():
                if attr == value:
                    self._bitmask = attr
                    self._name = name

            if not self._name:
                raise ValueError("{value} is not a valid {cls}".format(value=value, cls=self.__class__.__name__))

        elif isinstance(value, str):
            if value in self._attr_map:
                self._bitmask = self._attr_map[value]
                self._name = value
                self._value = self._bitmask.value
            else:
                raise ValueError("{value} is not a valid {cls}".format(value=value, cls=self.__class__.__name__))

        return super(BitmaskEnum, self).__init__()

    def __repr__(self):
        return "{cls}.{value}".format(cls=self.__class__.__name__, value=self._name)

    def __str__(self):
        return self._name

    def __int__(self):
        return int(self._value)

    def __float__(self):
        return float(self._value)

    def __eq__(self, other):
        if isinstance(other, BitmaskEnum):
            return self._bitmask == other._bitmask and self._name == other._name
        else:
            return self._bitmask == other
