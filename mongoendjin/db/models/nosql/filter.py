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

    def as_mongo(self):
        result = {}
        for child in self.children:
            result.update(child.as_mongo())
        return result