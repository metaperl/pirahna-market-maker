def pretty_dump(label, o):
    import pprint
    return """
<{}>
{}
</{}>
""".format(label, pprint.pformat(o, indent=4), label)
