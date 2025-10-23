def parse(input: str, comment_marker: str):
    result = []
    lines = input.splitlines()
    i = 0

    # skip empty lines at start
    while i < len(lines) and len(lines[i].lstrip()) == 0:
        i += 1

    while i < len(lines):
        code, comments = [], []

        # skip empty lines
        while i < len(lines) and len(lines[i].lstrip()) == 0:
            i += 1

        if not lines[i].lstrip().startswith(comment_marker):
            # if starting with code we only parse code
            while i < len(lines) and not lines[i].lstrip().startswith(comment_marker):
                code.append(lines[i])
                i += 1
        else:
            # first parse leading comment
            while i < len(lines) and lines[i].lstrip().startswith(comment_marker):
                comments.append(lines[i].strip()[len(comment_marker):].lstrip())
                i += 1

            # parse following code (everything that's not a comment or empty line)
            while i < len(lines) and not (lines[i].lstrip().startswith(comment_marker)
                                 or len(lines[i].lstrip()) == 0):
                code.append(lines[i])
                i += 1

        result.append((' '.join(comments), code))
    
    return result
