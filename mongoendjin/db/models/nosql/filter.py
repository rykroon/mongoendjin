"""
    Related to 'where.py' in Django
"""

from mongoendjin.utils import tree

#connection types
AND = 'AND'
OR = 'OR'


class FilterNode(tree.Node):

    """
        A child is usually a Lookup instance.
    """
    default = AND

    def clone(self):
        clone = self.__class__._new_instance(
            children=[], connector=self.connector, negated=self.negated)
        for child in self.children:
            if hasattr(child, 'clone'):
                clone.children.append(child.clone())
            else:
                clone.children.append(child)
        return clone

    def as_mongo(self):
        result = {}
        for child in self.children:
            result.update(child.as_mongo())
        return result