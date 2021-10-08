import requests
import json
from string import Template
import uuid
from datetime import datetime
import argparse

edp_upload_reading_api_endpoint = 'https://edpzero.cliente.edp.pt/client/listeners/api/pt.edp.edponline.reading.uploadReading'

edp_google_auth_api_key = 'AIzaSyBCyKe7wskhsEcIHK7C_FVQlJLlOBJPda8'

edp_meter_date = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')

edp_payload_report_template = Template("""{
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
}""")
    
def edp_sign_in(email, password):
        request_ref = "https://www.googleapis.com/identitytoolkit/v3/relyingparty/verifyPassword?key={0}".format(edp_google_auth_api_key)
        headers = {"content-type": "application/json; charset=UTF-8"}
        data = json.dumps({"email": email, "password": password, "returnSecureToken": True})
        request_object = requests.post(request_ref, headers=headers, data=data)        
        return request_object.json()
    



def submit_meter_reading(auth_token, edp_contract_id, edp_cpe_code, edp_serial_number, reading_vazio, reading_ponta, reading_cheia):
    edp_payload_report = edp_payload_report_template.substitute(edp_correlation_id=uuid.uuid4(), edp_contract_id=edp_contract_id, edp_serial_number=edp_serial_number, edp_cpe_code=edp_cpe_code, edp_meter_date=edp_meter_date, edp_reading_vazio=reading_vazio, edp_reading_ponta=reading_ponta, edp_reading_cheia=reading_cheia)
    resp = requests.post(edp_upload_reading_api_endpoint, edp_payload_report, headers={'Authorization': auth_token})
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
    auth = edp_sign_in(args.e, args.p)
    auth_token = auth['idToken']
    print("Uploading reading report to edp ...")
    submit_meter_reading(auth_token, args.i, args.c, args.s, args.rv, args.rp, args.rc)

if __name__ == "__main__":
    main()


