def json2dict(file) -> dict:
    import json
    with open(file, 'r') as f:
        return json.load(f)


def dict2json(dict, file) -> None:
    import json
    with open(file, 'w') as f:
        json.dump(dict, f, indent=4)


if __name__ == '__main__':
    config = json2dict('template.json')

    config['master']['username'] = ''
    config['master']['password'] = ''

    config['term']['termId'] = '20212'

    config['params']['cids'].append('08305012')
    config['params']['tnos'].append('1002')

    config['servant']['username'] = ''
    config['servant']['password'] = ''

    dict2json(config, 'config.json')
