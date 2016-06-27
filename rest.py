import pycurl
import cStringIO
import simplejson
import os
import time

TIMEOUT = 300

class Rest:

    def __init__(self, url, useXBasicAuth = True):
        """
        Initializes the Rest object with that will interact with a given URL.
        parameter: useXBasicAuth whether to use X-Basic or Basic authentication.
        """
        self.__url = url.replace(' ', "%20") # Avoid problems with URLs containing spaces
        self.__useXBasicAuth = useXBasicAuth
        self.request_count = 0.0
        self.accum_request_time = 0.0

    def set_url(self, new_url):
        self.__url = new_url

    def __perform(self, c):
        buf = cStringIO.StringIO()
        if self.__useXBasicAuth:
          c.setopt(c.HTTPHEADER, ['Authorization: X-Basic YWRtaW46YWRtaW4='])
        else:
          c.setopt(c.HTTPHEADER, ['Authorization: Basic YWRtaW46YWRtaW4='])
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.setopt(c.CONNECTTIMEOUT, TIMEOUT)
        c.setopt(c.TIMEOUT, TIMEOUT)
        c.setopt(c.NOSIGNAL, 1) 
        #c.setopt(c.FAILONERROR, True) Don't throw exception. HTTP errors are handled by the upper layer via the returned code

        t0 = time.clock()
        try:
            self.request_count = self.request_count + 1.0
            c.perform()
        except pycurl.error, error:
            errno, errstr = error
            print 'Error in perform. Error code: %s, message: %s, url: %s' % (errno, errstr, self.__url)
            self.accum_request_time = self.accum_request_time + (time.clock() - t0)
            raise

        self.accum_request_time = self.accum_request_time + (time.clock() - t0)

        try:
            res = simplejson.loads(buf.getvalue())
        except simplejson.decoder.JSONDecodeError:
            res = None
        buf.close()

        cd = c.getinfo(c.HTTP_CODE)
        c.close()

        return cd, res

    def __curl(self):
        c = pycurl.Curl()
        c.setopt(c.URL, self.__url)
        return c

    def get(self):
        """
        Performs a GET on the URL
        returns: A pair containing the return code and an object containing the response.
        Such object is accessible as a JSON object
        """
        return self.__perform(self.__curl())

    def post(self, data):
        """
        Performs a POST on the URL, with the given data as parameters
        parameter: data - An object that must be convertible to string
        returns: A pair containing the return code and an object containing the response.
        Such object is accessible as a JSON object.
        """
        c = self.__curl()
        c.setopt(c.POSTFIELDS, str(data))
        ret = self.__perform(c)
        return ret

    def delete(self):
        """
        Performs a DELETE on the URL
        returns: A pair containing the return code and an object containing the response.
        """
        c = self.__curl()
        c.setopt(c.CUSTOMREQUEST, 'DELETE')
        ret = self.__perform(c)
        return ret
    
    def put(self, data):
        """
        Performs a PUT on the URL
        returns: A pair containing the return code and an object containing the response.
        """
        c = self.__curl()
        c.setopt(c.POSTFIELDS, str(data))
        c.setopt(c.CUSTOMREQUEST, 'PUT')

        ret = self.__perform(c)
        return ret
    def putJsonFile(self, localfile):
        """
        Performs a PUT on the URL
        returns: A pair containing the return code and an object containing the response.
        """
        c = self.__curl()
        #c.setopt(pycurl.POST,   True)
        c.setopt(c.HTTPPOST, [('file', (pycurl.FORM_FILE, localfile))] )
        #c.setopt(c.CUSTOMREQUEST, 'POST')
        c.setopt(c.CUSTOMREQUEST, 'PUT')

        ret = self.__perform(c)
        return ret

    def put_file(self, local_file):
        c = self.__curl()
        c.setopt(pycurl.UPLOAD,   True)
        filesize = os.path.getsize(local_file) 
        c.setopt(pycurl.INFILESIZE, filesize) 
        c.setopt(pycurl.INFILE, open(local_file, 'rb')) 
        return c.perform()#_do_request()

    def pyCurlWrap(self, data):
        buf = cStringIO.StringIO()
        c=pycurl.Curl()
        c.setopt(c.URL, self.__url);
        c.setopt(c.WRITEFUNCTION, buf.write)
        c.setopt(c.CONNECTTIMEOUT, 5)
        c.setopt(c.TIMEOUT, 8)
        if not data == "null":
            c.setopt(c.POSTFIELDS, data)
        c.setopt(c.FOLLOWLOCATION, True)
        c.setopt(c.MAXREDIRS, 10)
        c.setopt(c.CUSTOMREQUEST, 'PUT')
        c.setopt(c.HTTPHEADER, ['Content-type: application/json'])
        c.perform()
        result = buf.getvalue()
        buf.close()
        return result;

    def get_mean_request_time(self):
        """
        Returns the mean request time of all request performed so far in seconds as 
        a floating point number.
        """
        ret = 0.0
        if (self.request_count != 0.0):
            ret = self.accum_request_time / self.request_count

        return ret


