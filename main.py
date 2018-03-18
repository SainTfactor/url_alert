import sys
import http.client
import datetime
import smtplib
from entities import *

def add_task():
    name = input("Input task name: ")
    search_term = input("Input search term: ")
    target_email = input("Input target email: ")
    print("Input URLs (leave blank to terminate)")
    url_list = []
    url = "first"
    while not url == "":
        url = input(" >")
        url_list.append(url)
    urls = ";".join([i for i in url_list if not i == ""])
    create_task(name, search_term, urls, target_email)
    
def show_task(task):
    print("Id:\t\t" + str(task.id))
    print("Name:\t\t" + task.name)
    print("Search Term:\t" + task.search_term)
    print("Target Email:\t" + task.target_email)
    print("Last Found:\t" + str(task.last_triggered))
    print("URLs:\n\t" + "\n\t".join(task.urls.split(';')))
    print("\n")
    
def email_notification(task, url):
    import gmail_creds

    FROM = "no_reply@saintfactorstudios"
    TO = [task.target_email]
    SUBJECT = "We found your keyword on the web!!"
    TEXT = "Hey, that thing you were looking for?  " + task.search_term + "?  We found it!  Go to " + url + " to check it out!"
    
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    
    try:
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server_ssl.ehlo() # optional, called by login()
        server_ssl.login(gmail_creds.gmail_user, gmail_creds.gmail_pwd)  
        # ssl server doesn't support or need tls, so don't call server_ssl.starttls() 
        server_ssl.sendmail(FROM, TO, message)
        #server_ssl.quit()
        server_ssl.close()
        print("Successfully sent the mail")
    except:
        print("Failed to send mail")


def run_tasks():
    [run_task(i) for i in Task.select().where((Task.last_triggered == None) | (Task.last_triggered != datetime.date.today()))]    
 
def run_task(task):
    print("Running " + task.name + "...")
    for url in task.urls.split(';'):
        parts = url.split('/')
        locat = "/" + "/".join(parts[3:])
        conn = None
        if parts[0] == "http:":
            conn = http.client.HTTPConnection(parts[2])
        elif parts[0] == "https:":
            conn = http.client.HTTPSConnection(parts[2]) 
        else:
            print("Invalid URL")   
            return
        
        conn.request("GET", locat)
        data = conn.getresponse().read().lower()
        if str.encode(task.search_term.lower()) in data:
            Task.update({Task.last_triggered: datetime.date.today()}).where(Task.id == task.id).execute()
            email_notification(task, url)
        else:
            print("No instances of " + task.search_term + " found at " + url)
    print("")
        
def main():
    print("                            ")
    print("Welcome to the web checker! ")
    print("  Options -                 ")
    print("    1: Add task             ")
    print("    2: Remove task          ")
    print("    3: Run task             ")
    print("    4: Run all tasks        ")
    print("    5: Show task            ")
    print("    6: Show all tasks       ")
    print("    7: Exit                 ")
    print("                            ")
    
    try:
        choice = int(input("chkr> "))
    except:
        choice = 0
        
    if(choice == 1):
        add_task()
    elif(choice == 2):
        name = input("Task name: ")
        if remove_task(name):
            print("Success: Task removed")
        else:
            print("ERROR: Task not found")
    elif(choice == 3):
        name = input("Task name: ")
        run_task(get_task(name))
    elif(choice == 4):
        run_tasks()
    elif(choice == 5):
        name = input("Task name: ")
        show_task(get_task(name))
    elif(choice == 6):
        print("")
        [show_task(i) for i in Task.select()]
    elif(choice == 7):
        print("Thanks, come again!")
    else:
        print("Not a valid option!")

if len(sys.argv) > 1 and sys.argv[1] == "run":
    run_tasks()
else:
    main()