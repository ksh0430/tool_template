import os.path
import yaml

import utils


class Toolchain(object):

    def __init__(self, toolchain_id=None, filename=None):
        self.doc = {}
        self.repos = {}
        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        with open(filename, 'r') as fp:
            self.doc = yaml.load(fp)
        self.init_doc()

    def init_doc(self):
        self.doc['version'] = '0.1'

    def get_services(self, service_id=None, startswith=None):
        if service_id:
            return {k: v for k, v in self.doc.items() if k.startswith('service') and v['service_id'] == service_id}

    def save_pipeline(self, k, filename):
        params = self.doc[k]['parameters']
        try:
            pipeline_id = params['api_url'].split('/')[-1]
            del params['api_url']
        except:
            raise Exception('Cannot find api_url for pipeline, use otc save-template')
        text = utils.get_pipeline(pipeline_id)
        data = yaml.load(text)
        for stage in data['stages']:
            for sinput in stage['inputs']:
                if sinput['type'] == 'git':
                    url = sinput['url']
                    if url in self.repos:
                        service_name = self.repos[url]
                        sinput['service'] = service_name
                        del sinput['url']
                        if 'services' in params:
                            if not service_name in params['services']:
                                params['services'].append(service_name)
                        else:
                            params['services'] = [service_name]
        fullpath = os.path.join('.bluemix/', filename)
        with open(fullpath, 'w') as fp:
            fp.write(yaml.dump(data, default_flow_style=False))
            print 'Pipeline saved to {}'.format(fullpath)
        params['configuration'] = {
            'content': {
                '$text': filename
            },
            'env': {
                #'SERVICE_API_REPO': repo_service,
                #'PROD_REGION_ID': '{{deploy.parameters.prod-region}}',
                #'PROD_ORG_NAME': '{{deploy.parameters.prod-organization}}',
                #'PROD_SPACE_NAME': '{{deploy.parameters.prod-space}}',
            },
        }

    def dump(self):
        return yaml.dump(self.doc, default_flow_style=False)

    def save(self, filename='.bluemix/toolchain.yml'):
        with open(filename, 'w') as fp:
            fp.write(self.dump())


def main():
    old_tc = Toolchain(filename='toolchain1497968997.yml')
    new_tc = Toolchain()
    new_tc.doc['deploy'] = {
        'service-category': 'pipeline',
        'parameters': {
            'prod-region': '{{region}}',
            'prod-organization': '{{organization}}',
            'prod-space': '{{space}}',
        }
    }

    for k, v in old_tc.doc.iteritems():
        if k.startswith('service'):
            service_id = v['service_id']
            if service_id == 'pipeline':
                service_name = 'service_pipeline_{}'.format(v['parameters']['name'])
            elif service_id == 'githubpublic':
                service_name = 'service_github_{}'.format(v['parameters']['repo_name'])
                new_tc.repos[v['parameters']['repo_url']] = service_name
            else:
                service_name = 'service_{}'.format(v['service_id'])
                # Clean-up parameters
                v['parameters'] = {}
        else:
            service_name = k
        try:
            del v['toolchain_binding']
        except TypeError:
            pass
        new_tc.doc[service_name] = v

    # Configure pipeline
    for k, v in new_tc.get_services('pipeline').items():
        name = v['parameters']['name']
        filename = 'pipeline_{}.yml'.format(name)
        new_tc.save_pipeline(k, filename)

    new_tc.save()

if __name__ == '__main__':
    main()
