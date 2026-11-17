"""Actual loopback browser navigation probe: proves why navigated CWV/axe is a release HOLD."""
import http.server,json,socketserver,subprocess,threading,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
class Fixture(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path!='/':self.send_error(404);return
        data=subprocess.run(['php',str(ROOT/'qa/render_fixture.php')],capture_output=True,text=True,check=True).stdout.encode()
        self.send_response(200)
        self.send_header('Content-Type','text/html; charset=utf-8')
        self.send_header('Content-Length',str(len(data)))
        self.end_headers();self.wfile.write(data)
    def log_message(self,*args):pass

def run():
    result={'source':'read-only Python loopback serving exact PHP fixture',
            'browser_navigation':'UNVERIFIED','axe_core':'UNAVAILABLE',
            'lcp':'NOT MEASURED','cls':'NOT MEASURED','wordPress_staging':'NOT TESTED'}
    with socketserver.TCPServer(('127.0.0.1',0),Fixture) as server:
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        target=f'http://127.0.0.1:{server.server_address[1]}/'
        try:
            with urllib.request.urlopen(target,timeout=6) as response:
                result['python_http_status']=response.status
                result['python_markup_marker']=b'data-fv-r419-concordance' in response.read()
        except Exception as exc:result['python_http_error']=type(exc).__name__+': '+str(exc)
        try:
            with sync_playwright() as playwright:
                browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
                try:
                    page=browser.new_page()
                    response=page.goto(target,wait_until='load',timeout=8000)
                    result['browser_navigation']='SUCCEEDED_ON_FIXTURE_ONLY'
                    result['browser_http_status']=response.status if response else None
                except Exception as exc:
                    result['browser_navigation']='BLOCKED'
                    result['browser_error']=str(exc).splitlines()[0]
                finally:browser.close()
        except Exception as exc:
            result['browser_navigation']='UNAVAILABLE'
            result['browser_error']=type(exc).__name__+': '+str(exc)
        server.shutdown()
    (ROOT/'QA/navigation_probe.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(result,sort_keys=True))
if __name__=='__main__':run()
