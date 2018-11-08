#!/usr/bin/python 
import requests # get the requsts library from https://github.com/requests/requests
# overriding requests.Session.rebuild_auth to mantain headers when redirected
 
class SessionWithHeaderRedirection(requests.Session):

    AUTH_HOST = 'urs.earthdata.nasa.gov'
 
    def __init__(self, username, password):
        super().__init__()
        self.auth = (username, password)

   # Overrides from the library to keep headers when redirected to or from
 
   # the NASA auth host.
    def rebuild_auth(self, prepared_request, response):
        headers = prepared_request.headers
        url = prepared_request.url

        if 'Authorization' in headers:
            original_parsed = requests.utils.urlparse(response.request.url)
            redirect_parsed = requests.utils.urlparse(url)

            if (original_parsed.hostname != redirect_parsed.hostname) and \
                    redirect_parsed.hostname != self.AUTH_HOST and \
                    original_parsed.hostname != self.AUTH_HOST:
                del headers['Authorization']
        return
 
# create session with the user credentials that will be used to authenticate access to the data
username = "yymjzq"
password= "6912448zZ"
session = SessionWithHeaderRedirection(username, password)

file_front_name = ' NLDAS_FORA0125_H.A20150105' 
for i in range(24):
    if i < 10:
        num = '0' + str(i)
    else:
        num = str(i)
    # the url of the file we wish to retrieve 
    url = 'https://hydro1.gesdisc.eosdis.nasa.gov/data'\
            + '/NLDAS/NLDAS_FORA0125_H.002/2015/005/' \
            + 'NLDAS_FORA0125_H.A20150105.' \
            + num + '00.002.grb'
    # extract the filename from the url to be used when saving the file
    filename = url[url.rfind('/')+1:]  

    xml_url = url + '.xml'
    xml_file = xml_url[url.rfind('/')+1:]
     
    try:
        # submit the request using the session
        response = session.get(url, stream=True)
        print(response.status_code)

        # raise an exception in case of http errors
        response.raise_for_status()  

        # save the file
        with open(filename, 'wb') as fd:
            for chunk in response.iter_content(chunk_size=1024*1024):
                fd.write(chunk)

        xml_response = session.get(xml_url, stream=True)
        print(xml_response.status_code)

        xml_response.raise_for_status()  

        with open(xml_file, 'wb') as xf:
            for xml_chunk in xml_response.iter_content(chunk_size=1024*1024):
                xf.write(xml_chunk)
     
    except requests.exceptions.HTTPError as e:
        # handle any errors here
        print(e)