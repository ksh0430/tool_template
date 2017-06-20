import yaml


class Toolchain(object):

    def __init__(self, toolchain_id=None, filename=None):
        self.doc = {}
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

    def dump(self):
        return yaml.dump(self.doc, default_flow_style=False)


def main():
    old_tc = Toolchain(filename='toolchain1497948546.yml')
    new_tc = Toolchain()
    new_tc.doc['deploy'] = {
        'service-category': 'pipeline',
        'parameters': {
            'prod-region': '{{region}}',
            'prod-organization': '{{organization}}',
            'prod-space': '{{space}}',
        }
    }

    repo_service = None
    for k, v in old_tc.doc.iteritems():
        if k.startswith('service'):
            service_id = v['service_id']
            if service_id == 'pipeline':
                service_name = 'service_pipeline_{}'.format(v['parameters']['name'])
            elif service_id == 'githubpublic':
                service_name = 'service_github_{}'.format(v['parameters']['repo_name'])
                if not repo_service:
                    repo_service = service_name
            else:
                service_name = 'service_{}'.format(v['service_id'])
        else:
            service_name = k
        new_tc.doc[service_name] = v

    # Configure pipeline
    for k, v in new_tc.get_services('pipeline').items():
        name = v['parameters']['name']
        newparams = {
            'services': [repo_service],
            'name': name,
            'configuration': {
                'content': {
                    '$text': 'pipeline_{}.yaml'.format(name)
                },
                'env': {
                    'SERVICE_API_REPO': repo_service,
                    'PROD_REGION_ID': '{{deploy.parameters.prod-region}}',
                    'PROD_ORG_NAME': '{{deploy.parameters.prod-organization}}',
                    'PROD_SPACE_NAME': '{{deploy.parameters.prod-space}}',
                }
            }
        }
        v['parameters'] = newparams

    print new_tc.dump()

if __name__ == '__main__':
    main()
