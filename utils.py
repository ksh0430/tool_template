import os.path
import json
import requests


def get_auth():
    home = os.path.expanduser('~')
    config_file = os.path.join(home, '.cf/config.json')
    try:
        with open(config_file, 'r') as fp:
            data = json.load(fp)
    except EnvironmentError as error:
        print("'cf login' first")
        raise error
    try:
        return data['AccessToken']
    except KeyError as error:
        raise Exception("Cannot find access token, 'cf login' first")

def get_pipeline(pipeline_id):
    url = 'https://otc-pipeline-server.ng.bluemix.net/pipeline/pipelines/{}'.format(pipeline_id)
    headers = {
        'Accept': 'application/x-yaml',
        'Authorization': get_auth(),
    }
    #try:
    #    with open('a.yml', 'r') as fp:
    #        return fp.read()
    #except:
    #    pass
    res = requests.get(url, headers=headers)
    #with open('a.yml', 'w') as fp:
    #    fp.write(res.text)
    return res.text
