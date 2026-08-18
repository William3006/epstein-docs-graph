from rapidfuzz import fuzz

def resolve_entities(nodes_dict):
    names = [n.strip() for n in nodes_dict.keys() if n.strip()]
    groups = []
    used = set()

    for name in names:
        if name in used:
            continue
        group = {name}
        for other in names:
            if other == name or other in used:
                continue
            # only merge entities of the same type
            if nodes_dict.get(name) != nodes_dict.get(other):
                continue
            if name in other or other in name:
                group.add(other)
            elif fuzz.ratio(name, other) > 85:
                group.add(other)
        groups.append(group)
        used.update(group)

    merged_groups = []
    consumed = set()
    for i, g1 in enumerate(groups):
        if i in consumed:
            continue
        combined = set(g1)
        last_words_1 = {n.split()[-1] for n in g1 if n.split()}
        for j, g2 in enumerate(groups):
            if j <= i or j in consumed:
                continue
            # also require same type here
            if nodes_dict.get(next(iter(g1))) != nodes_dict.get(next(iter(g2))):
                continue
            last_words_2 = {n.split()[-1] for n in g2 if n.split()}
            if last_words_1 & last_words_2:
                combined |= g2
                consumed.add(j)
        merged_groups.append(combined)

    alias_map = {}
    for group in merged_groups:
        canonical = max(group, key=len)
        for alias in group:
            alias_map[alias] = canonical
    return alias_map