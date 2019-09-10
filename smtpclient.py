from flask import Flask, request, json, make_response
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
#recipients = []
@app.route('/mail', methods=['POST'])
def mail():
        if request.method == 'POST':
             request.get_json(force=True)
             if 'msg' in request.json and 'mail_to' in request.json:
                  message = request.json['msg']
                  msg = MIMEMultipart('alternative')
                  msg['Subject'] = "OTP"
                  msg['From'] = "infobahnforotp@itc.in"
#                  recipients.append(request.json['mail_to'])
#                  msg['To'] = ", ".join(recipients)
                  msg['To'] = request.json['mail_to']
                  html = message
                  part1 = MIMEText(html, 'html')
                  msg.attach(part1)
                  print(msg)
                  try:
#                         Send the message via local SMTP server.
                          s = smtplib.SMTP('localhost')
                          s.set_debuglevel(1)
#                         sendmail function takes 3 arguments: sender's address, recipient's address
#                         and message to send - here it is sent as one string.
                          s.sendmail(msg['From'], msg['To'], msg.as_string())
                          return make_response('Email Sent to {0} !'.format(request.json['mail_to'])), 200
                  except Exception as e:
                      return e
                  finally:
                      s.quit()

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5000)

