"""
    Related to 'where.py' in Django
"""

from mongoendjin.utils import tree

#connection types
AND = 'AND'
OR = 'OR'

CONNECTION_TYPE_TO_MONGO = {
    AND: '$and',
    OR: '$or'
}


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
        connector = CONNECTION_TYPE_TO_MONGO[self.connector]
        result = []

        for child in self.children:
            result.append(child.as_mongo())

        return {
            connector: result
        }