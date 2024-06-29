from helpers import add_outcomes

dict1 = {'a': {'odds': 3.5, 'count': 2}, 'b': {'odds': 5.5, 'count': 2}}

dict2 = {'a': {'odds': 1.5, 'count': 1}, 'b': {'odds': 2.5, 'count': 1}}
print(dict1)
add_outcomes(dict1,dict2)
print(dict1)