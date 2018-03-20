import setuptools

setuptools.setup(name='er',
                 version='0.0.1',
                 author='mfmfmf',
                 author_email='twd2@163.com',
                 description='Event Registration Web Server',
                 license='AGPL-3.0',
                 keywords='event online registration web',
                 url='?',
                 packages=[
                   'er',
                   'er.handler',
                   'er.model',
                   'er.service',
                   'er.util',
                 ],
                 package_data={
                   'er': ['locale/*.csv', 'ui/templates/*', '.uibuild/*'],
                 },
                 install_requires=open('requirements.txt').readlines(),
                 test_suite='er.test')
