import requests
import json
from string import Template
import uuid
from datetime import datetime
import argparse


edp_upload_reading_api_endpoint = 'https://edpzero.cliente.edp.pt/client/listeners/api/pt.edp.edponline.reading.uploadReading'
edp_get_simulation_api_endpoint = 'https://edpzero.cliente.edp.pt/client/listeners/api/pt.edp.edponline.reading.getSimulation'

edp_google_auth_api_key = 'AIzaSyBCyKe7wskhsEcIHK7C_FVQlJLlOBJPda8'

edp_meter_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

edp_correlation_id=uuid.uuid4()

edp_payload_report_template = Template("""
{
   "correlationId":"${edp_correlation_id}",
   "args":{
      "contractId":"${edp_contract_id}",
      "SupplyType":"E",
      "ReadingsList":[
         {
            "Brand":null,
            "Material":"INTELIGENTE",
            "Model":null,
            "SerialNo":"${edp_serial_number}",
            "Register":"001",
            "RegisterType":"V",
            "RegisterTypeStr":"Vazio",
            "ReadingResult":"${edp_reading_vazio}",
            "ExtUi":"${edp_cpe_code}",
            "MrReason":"09",
            "ActualCustomerMrType":"10",
            "MeterDate":"${edp_meter_date}",
            "InputDateFormat":"",
            "OutputDateFormat":""
         },
         {
            "Brand":null,
            "Material":"INTELIGENTE",
            "Model":null,
            "SerialNo":"${edp_serial_number}",
            "Register":"002",
            "RegisterType":"P",
            "RegisterTypeStr":"Ponta",
            "ReadingResult":"${edp_reading_ponta}",
            "ExtUi":"${edp_cpe_code}",
            "MrReason":"09",
            "ActualCustomerMrType":"10",
            "MeterDate":"${edp_meter_date}",
            "InputDateFormat":"",
            "OutputDateFormat":""
         },
         {
            "Brand":null,
            "Material":"INTELIGENTE",
            "Model":null,
            "SerialNo":"${edp_serial_number}",
            "Register":"003",
            "RegisterType":"C",
            "RegisterTypeStr":"Cheia",
            "ReadingResult":"${edp_reading_cheia}",
            "ExtUi":"${edp_cpe_code}",
            "MrReason":"09",
            "ActualCustomerMrType":"10",
            "MeterDate":"${edp_meter_date}",
            "InputDateFormat":"",
            "OutputDateFormat":""
         }
      ]
   },
   "replacements":[
   ]
}
""")

edp_payload_get_simulation_template = Template("""
{
   "correlationId":"${edp_correlation_id}",
   "args":{
      "contractId":"${edp_contract_id}",
      "offline":false
   },
   "replacements":[
      
   ]
}                               
""")

    
edp_payload_sso_template = Template("""
{
   "correlationId":"${correlationID}",
   "args":{
      "token":"${token}",
      "channel":"browser"
   },
   "replacements":null,
   "loading":false
}
""")

google_verifyCustomToken_payload_template = Template("""
{
     "token":"${token}",
     "returnSecureToken":true
}                                                                                                          
""")

edp_payload_usersession_login_template = Template("""
{
     "correlationId":"${correlationID}",
     "args":
         {
             "token_id":"${token}",
             "platform":0
         },
         "replacements":[]
}                                              
""")
    
def edp_sign_in(email, password):
        ## Get authentication token from google idp
        request_ref = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}'.format(edp_google_auth_api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        request_object = requests.post(request_ref, headers=headers, data=data)
        
        ## Login to edp with authentication token provided on the previous step 
        request_url = 'https://login.edp.pt/listeners/api/pt.edp.sso.auth.logIn'
        resp = requests.post(request_url, 
                             edp_payload_sso_template.substitute(token=request_object.json()['idToken'], 
                                                                 correlationID=edp_correlation_id),
                             headers={'authorization': request_object.json()['idToken']})
        firebase_token_cookie_header = resp.headers['set-cookie'].split(';')[3].split(',')[1].split('=')[1]
        
        ## Request authorization from google idp (i guess)
        request_url = 'https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyCustomToken?key={0}'.format(edp_google_auth_api_key)
        resp = requests.post(request_url, 
                             google_verifyCustomToken_payload_template.substitute(token=firebase_token_cookie_header))
        
        ## Get user session token from edp with authentication and authorization tokens
        request_url = 'https://edpzero.cliente.edp.pt/client/listeners/api/pt.edp.edponline.usersession.login'
        resp = requests.post(request_url, 
                             edp_payload_usersession_login_template.substitute(token=resp.json()['idToken'],
                                                                               correlationID=edp_correlation_id), 
                             headers={'authorization': resp.json()['idToken']})
        
        authorization_token_header = resp.headers['set-cookie'].split(';')[3].split(',')[1].split('=')[1]
        
        return firebase_token_cookie_header, authorization_token_header



def submit_meter_reading(firebase_token_cookie_header, authorization_token_header, edp_contract_id, edp_cpe_code, edp_serial_number, reading_vazio, reading_ponta, reading_cheia):
    edp_payload_report = edp_payload_report_template.substitute(edp_correlation_id=edp_correlation_id, 
                                                                edp_contract_id=edp_contract_id, 
                                                                edp_serial_number=edp_serial_number, 
                                                                edp_cpe_code=edp_cpe_code, 
                                                                edp_meter_date=edp_meter_date, 
                                                                edp_reading_vazio=reading_vazio, 
                                                                edp_reading_ponta=reading_ponta, 
                                                                edp_reading_cheia=reading_cheia)
    
    resp = requests.post(edp_upload_reading_api_endpoint, 
                         edp_payload_report, 
                         headers={'authorization': authorization_token_header, 'cookie': firebase_token_cookie_header})
    print(resp.text)
    
def get_simulation(firebase_token_cookie_header, authorization_token_header, edp_contract_id):
    edp_payload_get_simulation = edp_payload_get_simulation_template.substitute(edp_correlation_id=edp_correlation_id, 
                                                                edp_contract_id=edp_contract_id)
    
    resp = requests.post(edp_get_simulation_api_endpoint, 
                         edp_payload_get_simulation, 
                         headers={'authorization': authorization_token_header, 'cookie': firebase_token_cookie_header})
    print(resp.text)
    
def main():    
    arg_parser = argparse.ArgumentParser(prog='edp-report-meter-reading',
                                         usage='%(prog)s [args]',
                                         description='Report meter readings to edp',
                                         fromfile_prefix_chars='@')
    arg_parser.add_argument('-e',
                       help='edp user login email',
                       action='store', type=str, required=True)
    arg_parser.add_argument('-p',
                       help='edp user password',
                       action='store', type=str, required=True)
    arg_parser.add_argument('-i',
                       help='edp contract id',
                       action='store', type=str, required=True)
    arg_parser.add_argument('-c',
                       help='edp CPE code',
                       action='store', type=str, required=True)
    arg_parser.add_argument('-s',
                       help='edp serial number',
                       action='store', type=str, required=True)
    arg_parser.add_argument('-rv',
                       help='edp meter reading - vazio',
                       action='store', type=str, required=True)
    arg_parser.add_argument('-rp',
                       help='edp meter reading - ponta',
                       action='store', type=str, required=True)
    arg_parser.add_argument('-rc',
                       help='edp meter reading - cheio',
                       action='store', type=str, required=True)
    
    args = arg_parser.parse_args()

    print("Authenticating ...")
    firebase_token_cookie_header, authorization_token_header = edp_sign_in(args.e, args.p)
    print("Uploading reading report to edp ...")
    submit_meter_reading(firebase_token_cookie_header, 
                         authorization_token_header, args.i, args.c, args.s, args.rv, args.rp, args.rc)
    
    get_simulation(firebase_token_cookie_header, 
                         authorization_token_header, args.i)

if __name__ == "__main__":
    main()



