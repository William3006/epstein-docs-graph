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

 # merge groups that share either a first-word or last-word match
    merged_groups = []
    consumed = set()
    for i, g1 in enumerate(groups):
        if i in consumed:
            continue
        combined = set(g1)
        words_1 = set()
        for n in g1:
            parts = n.split()
            if parts:
                words_1.add(parts[0])
                words_1.add(parts[-1])
        for j, g2 in enumerate(groups):
            if j <= i or j in consumed:
                continue
            words_2 = set()
            for n in g2:
                parts = n.split()
                if parts:
                    words_2.add(parts[0])
                    words_2.add(parts[-1])
            if words_1 & words_2:
                combined |= g2
                consumed.add(j)
        merged_groups.append(combined)

    alias_map = {}
    for group in merged_groups:
        canonical = max(group, key=len)
        for alias in group:
            alias_map[alias] = canonical
    return alias_map