try:
    import urequests as requests
except:
    import requests
import os
import sys
from time import sleep, time
from parse import urlencode


class Updater:

    @staticmethod
    def _make_request(method:str, url:str, **kw):
        # This will work with HTTPS, but won't verify the certificate due to
        # https://github.com/micropython/micropython/issues/2781
        # urequests.request doesn't support params argument
        if 'params' in kw.keys():
            url = url.rstrip('?') + '?' + urlencode(kw.pop('params'), doseq=True)
        response = requests.request(method, url, **kw)
        if 200 <= response.status_code < 300:
            return response
        raise RuntimeError(f"Error fetching request:\n{response.text}")

    @classmethod
    def _make_api_request(cls, method:str, domain:str, path:str, **kw):
        headers = {
            'User-Agent': sys.platform.upper(),
            'Accept': 'Accept: application/vnd.github.v3+json'
        }
        url = f'https://{domain}{path}'
        response = cls._make_request(method, url, headers=headers, **kw)
        data = response.json()
        return data

    @classmethod
    def get_latest_commit(cls, repo:str, domain:str='api.github.com', branch:str=None):
        path = f'/repos/{repo}/commits'
        if branch:
            commits = cls._make_api_request('GET', domain, path, params={'sha': branch})
        else:
            commits = cls._make_api_request('GET', domain, path)
        return commits[0]

    @classmethod
    def get_latest_release(cls, repo:str, domain:str='api.github.com', prereleases:bool=False):
        path = f'/repos/{repo}/releases'
        releases = cls._make_api_request('GET', domain, path)
        if len(releases) == 0:
            return
        if prereleases:
            return releases[0]
        for release in releases:
            if not release['prerelease']:
                return release        

    @classmethod
    def download_update(cls, repo:str, commit:str, root_dir:str='/', domain:str='api.github.com'):
        if not root_dir:
            root_dir = '/'
        while root_dir[0] == '/':
            root_dir = root_dir[1:]
        params = {
            'ref': commit,
        }

        def find_all_files(directory):
            files = {}
            path = f'/repos/{repo}/contents/{directory}'
            contents = cls._make_api_request('GET', domain, path, params=params)

            for item in contents:
                if item['type'] == 'file':
                    files[item['path'].replace(root_dir, '')] = item['download_url']
                elif item['type'] == 'dir':
                    files += find_all_files(item['path'])
                else:
                    raise ValueError(f'Unsupported content type: {item["type"]}')
            
        for filepath, download_url in find_all_files(root_dir).items():
            if '/' in filepath:
                directory = '/'.join(filepath.split('/')[:-1])
                if not os.path.exists(directory):
                    os.makedirs(directory)
            with open(filepath, 'wb') as f:
                f.write(cls._make_request('GET', download_url).content)

    @classmethod
    def main(cls, config):
        domain = config.get('update_domain')
        repo = config.get('update_repo')
        
        # Check if a newer update is available
        if config.get('releases_only'):
            latest = cls.get_latest_release(repo, 'api.'+domain, config.get('prereleases'))
            if not latest:
                raise ValueError('At least one (valid) release must be published!')
            if latest['tag_name'].split('.') <= config.get('current_version').split('.'):
                return False
            commit = cls.get_latest_commit(repo, 'api.'+domain, latest['tag_name'])
        else:
            commit = cls.get_latest_commit(repo, 'api.'+domain, config.get('channel'))
            if commit['sha'] == config.get('current_version'):
                return False
        
        # Perform the update
        cls.download_update(repo, commit, config.get('update_path'), 'api.'+domain)

        # Set update values after successful update
        config.set('last_updated', time())
        version = commit['tag_name'] if config.get('releases_only') else commit['sha']
        print(f"Updated from version {config.get('current_version')} to version {version}.")
        config.set('current_version', version)
        return True
