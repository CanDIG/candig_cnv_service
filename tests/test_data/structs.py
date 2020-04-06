class testHeader():
    def __init__(self, headers):
        self.headers = headers

    def headers(self):
        return self.headers


token = ('eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0N1RQRU5RZ'
         'ENaWVdZVjRMa21FT0RhZnZRczlKR20tLVJIajdvMUx3Tk5RIn0.eyJqdGkiOi'
         'IwZWE1NTg2Zi04Y2M2LTQzNDUtYjRhYi1lNWNjYTNlYTJhM2IiLCJleHAiOjE'
         '1ODU4NTYyMDEsIm5iZiI6MCwiaWF0IjoxNTg1ODU1OTAyLCJpc3MiOiJodHRw'
         'Oi8vZ2E0Z2hkZXYwMS5iY2dzYy5jYTo4MDgwL2F1dGgvcmVhbG1zL0NhbkRJR'
         'yIsImF1ZCI6ImdhNGdoIiwic3ViIjoiOTA4MTYyNzItZjQ4Yi00MDA3LWE1Yj'
         'ktM2E5NDMzYzRkOTE1IiwidHlwIjoiSUQiLCJhenAiOiJnYTRnaCIsImF1dGh'
         'fdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImRjZTE4YzM0LTFkNWUtNGFiZi04'
         'OTgzLTdhMjdiODAzM2I1ZSIsImFjciI6IjEiLCJzdWIiOiJkbmFpZG9vIiwic'
         'm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJjYW5kaWciLCJ1bWFfYXV0aG9yaX'
         'phdGlvbiJdLCJuYW1lIjoiRGFzaGF5bGFuIE5haWRvbyBOYWlkb28iLCJwcmV'
         'mZXJyZWRfdXNlcm5hbWUiOiJkbmFpZG9vIiwiZ2l2ZW5fbmFtZSI6IkRhc2hh'
         'eWxhbiBOYWlkb28iLCJmYW1pbHlfbmFtZSI6Ik5haWRvbyIsImVtYWlsIjoiZ'
         'G5haWRvb0BiY2dzYy5jYSJ9.aXprN1QdYG2YwfPWnUzyq9rahnTKVS2w2Z1ky'
         'nkJBzBl4Ma4ek2Fg8_iR-iQYtj23OazDPAD14FkpsXjTFnt3uDsOa6m7hovKk'
         'J8KqUDezptpifMRxdZnBQFdgbGTa28yBn8qo-KdXUyCF4klPtf3hmhah0tvv_'
         'Sj_Xle52V0RBjzU6qmM2rrMgyS2xHsl1O_MS8UXTQk8MRHD6qiE5DbMcCXIRJ'
         'QNmRXFLNJizZFAIQYUnbDMNUlk4mv0gEWY8ihmVL4fQv1JyHeMmm5003DlOTt'
         '_XsetGcG72QQeUsHpguFoZyTYI0-rOd9_UpGwr9i5L8XFuG1d_l5Rf9hfzysw')

token2 = (
    'eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICI0N1RQRU5RZENaWVdZVjRMa21FT0RhZnZRczlKR20tLVJIajdvMUx3Tk5RIn0.eyJqdGkiOiI1YWYzMzhkMy0yNTMwLTQ1YTgtODcyNS04Mzk1MzMxZjc1OWMiLCJleHAiOjE1ODU5NTQ1ODIsIm5iZiI6MCwiaWF0IjoxNTg1OTU0MjgyLCJpc3MiOiJodHRwOi8vZ2E0Z2hkZXYwMS5iY2dzYy5jYTo4MDgwL2F1dGgvcmVhbG1zL0NhbkRJRyIsImF1ZCI6ImdhNGdoIiwic3ViIjoiOTA4MTYyNzItZjQ4Yi00MDA3LWE1YjktM2E5NDMzYzRkOTE1IiwidHlwIjoiSUQiLCJhenAiOiJnYTRnaCIsImF1dGhfdGltZSI6MCwic2Vzc2lvbl9zdGF0ZSI6ImVkMDM4MDZiLWNkZDAtNDVlOS1iZjg1LTk1MjliYmIxMWIwMSIsImFjciI6IjEiLCJzdWIiOiJkbmFpZG9vIiwicm9sZXMiOlsib2ZmbGluZV9hY2Nlc3MiLCJjYW5kaWciLCJ1bWFfYXV0aG9yaXphdGlvbiJdLCJuYW1lIjoiRGFzaGF5bGFuIE5haWRvbyBOYWlkb28iLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJkbmFpZG9vIiwiZ2l2ZW5fbmFtZSI6IkRhc2hheWxhbiBOYWlkb28iLCJmYW1pbHlfbmFtZSI6Ik5haWRvbyIsImVtYWlsIjoiZG5haWRvb0BiY2dzYy5jYSJ9.FjCw9taDYd0fZM4-0AXk1H3YUgdJ76xVdXLEzTjvYZAEvDXaZEx4O98Rx3PidBPyojkYjJAwTBs2o104VazvDYL6TeLwV8KuUwCyCUMpOSZwLiQjgeoJJ-f_ES9G47TbszMq-sNUJxw8f8oefwO3NNnffBOZi-JRPzrAw9I3pA9aytdaiEoj6WPnbfMIT9i-o5qwGZx64PntPPv1OkRQQCdJGIOZK6Q9rr8nNKaEcoYa71y7tWCPjfyOlncXw0xILZNnDtVTNJsQoufu0QVVhPidMrEgfi_skpoPkYD1onW28FD8vQGDTCtnY3KrmLIYN9XdHsdXw7mpHHmX0QfB3g'
)
goodHeader = testHeader({
        "Content-Type": "application/json",
        "Host": "ga4ghdev01.bcgsc.ca:8890",
        "User-Agent": "python-requests/2.22.0",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": "Bearer " + token2,
        "Federation": "false"
    })

badHeader = testHeader({
        "Content-Type": "application/json",
        "Host": "ga4ghdev01.bcgsc.ca:8890",
        "User-Agent": "python-requests/2.22.0",
        "Accept": "application/json",
        "Accept-Encoding": "gzip, deflate",
        "Authorization": "Bearer eyJhbGciOiJSUzI1NiIsI",
        "Federation": "true"
    })
