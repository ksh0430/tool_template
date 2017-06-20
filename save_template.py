import yaml

filename = 'toolchain1497948546.yml'

with open(filename, 'r') as fp:
    doc = yaml.load(fp)

def main():
    newdoc = {
        'deploy': {
            'service-category': 'pipeline',
            'parameters': {
                'prod-region': '{{region}}',
                'prod-organization': '{{organization}}',
                'prod-space': '{{space}}',
            }
        }
    }

    newdoc['version'] = '0.1'
    repo_service = 'service_github_spring-petclinic-microservices'
    for k, v in doc.iteritems():
        if k.startswith('service'):
            service_id = v['service_id']
            if service_id == 'pipeline':
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
                            'PROD_REGION_ID': "{{deploy.parameters.prod-region}}",
                            'PROD_ORG_NAME': "{{deploy.parameters.prod-organization}}",
                            'PROD_SPACE_NAME': "{{deploy.parameters.prod-space}}",
                        }
                    }
                }
                v['parameters'] = newparams
                service_name = 'service_pipeline_{}'.format(v['parameters']['name'])
            elif service_id == 'githubpublic':
                service_name = 'service_github_{}'.format(v['parameters']['repo_name'])
                if not repo_service:
                    repo_service = service_name
            else:
                service_name = 'service_{}'.format(v['service_id'])
        else:
            service_name = k
        newdoc[service_name] = v

    print yaml.dump(newdoc, default_flow_style=False)

if __name__ == '__main__':
    main()
