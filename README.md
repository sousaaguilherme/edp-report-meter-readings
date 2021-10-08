# EDP Report Meter Readings
  Simple python utility to report meter readings

## Usage
   
   ```
$ python edp-report-meter-reading.py -h
usage: edp-report-meter-reading [args]

Report meter readings to edp

optional arguments:
  -h, --help  show this help message and exit
  -e E        edp user login email
  -p P        edp user password
  -i I        edp contract id
  -c C        edp CPE code
  -s S        edp serial number
  -rv RV      edp meter reading - vazio
  -rp RP      edp meter reading - ponta
  -rc RC      edp meter reading - cheio

$ python edp_report_reading.py -e my_mail@gmail.com -p Passw0rd -c PTXXXXXXXXXXXXXXXXDA -i 12345678 -s 000011234567899999 -rv 1000 -rp 600 -rc 1500
```

  ### Notes:
##### This utility is **not** official. Use it at your own risk.
All trademarks, product names or brand names referred to in this document are the registered property of their respective holder.

