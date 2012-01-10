'''
'''
#import logging
import smtplib

# FIXME: Add logging for daily / Weekly digests
#Nice little implemention of logging output
#logger = logging.getLogger('cfwatchdog')
#hdlr = logging.FileHandler("C:\\cfwatchdog\\src\\watchdog.log")
#formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
#hdlr.setFormatter(formatter)
#logger.addHandler(hdlr)
#logger.setLevel(logging.INFO)

def send_email(from_addr, to_addr_list, cc_addr_list,
              subject, message,
              smtpserver='lava.studylink.com'):
    """Create doc string here"""
    try:
        header  = 'From: %s\n' % from_addr
        header += 'To: %s\n' % ','.join(to_addr_list)
        header += 'Cc: %s\n' % ','.join(cc_addr_list)
        header += 'Subject: %s\n\n' % subject
        message = header + message

        server = smtplib.SMTP(smtpserver)
        problems = server.sendmail(from_addr, to_addr_list, message)
        server.quit()
        #FIXME: logger.critical(problems)
    except Exception, e:
        print "Exception: ", e


def email_results(server,instance,results):
    """Email the results of each check to the Dev-Team"""
    # FIXME: This should be a digest of all issues.
    try:
        send_email(from_addr    = 'nick.minter@studylink.com',
              to_addr_list = ['nick.minter@studylink.com'],
              cc_addr_list = [''],
              subject      = 'Weekly server subversion report',
              message      = server+'\n'+instance+'\n'+results)
    except Exception, e:
        print "Exception: ", e