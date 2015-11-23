#!/usr/bin/env python
# 
# To do:
#   parse out duplicate links

from bs4 import BeautifulSoup
import sys
import argparse
from urlparse import urlparse, urlunparse
import requests
import re

address_regex = re.compile("[\w\d._%+-]+@[\w\d.-]+\.\w+")


def main():
    parser = argparse.ArgumentParser(description='Scrape the website of a given domain for email addresses')
    parser.add_argument('-u', help='The URL to start scraping from', dest="url",  required="True")
    parser.add_argument('-o', help='The output file for email addresses', dest="outfile", required="True")
    parser.add_argument('-n',help="Number of addresses to collect", dest="num_addresses", default=50)

    args = parser.parse_args()

    # Initialize all other variables
    emails = []     # array to hold all of the email addresses discovered
    URIs = []       # array to hold the URIs for all the links on the site that are discovered

    scrape(args.url,args.outfile,int(args.num_addresses),emails, URIs)
    with open(args.outfile,"a") as out:
        for email in emails:
            out.write(email)
            out.write("\n")
    

def scrape(link, output_file, num, emails, URIs):
	"""
	scrapes the given link and write out emails to the specified file
	Parameters:   link - the URL to scrape 
	              output_file - file name to write emails out to
	              num - the number of addresses to collect
	              emails - array containing list of emails
	              URIs - the list of URIs to crawl
	"""
    # create the urlparse object containing the given URL
    u = urlparse(link)

    # if scheme is not provided, set to http
    if u.scheme is '':
        p = urlunparse(u)
        u = urlparse('http://' + p)

    # Exit cases: max emails met, URI in list already, dead link
    # If we reach our email quota, return
    if len(emails) >= num:
        print "Max number of emails reached"
        return True

    if urlunparse(u) is ('http://' or 'https://'):
        print "Invalid URL"
        return True

    print "Scraping... '" + urlunparse(u) + "'"
    print "Num links: " + str(len(URIs))

    # if the URI is in the list already
    #if u.path in URIs:
    #    return True

    # pull new page
    try:
        r = requests.get(urlunparse(u))
        page = r.text
        soup = BeautifulSoup(page)
    except:
        raise
        return True
    # except KeyboardInterrupt:
    #     raise
    #     return True
    # except:
    #     pass

    # check for links by <a> (anchor) tag
    for href in soup.find_all('a'):
        if href.get('href') is not None:
            # If the URL is from the same domain, add it to the URI list
            if urlparse(href.get('href')).netloc is u.netloc or urlparse(href.get('href')).netloc is '':
                # add it to the URI list, only if it is not in the list already
                if urlparse(href.get('href')).path not in URIs:
                    if urlparse(href.get('href')).path is not (';' or ':' or '' or None):
                        # make sure link is not a mailto: address (like <a href="mailto:email@address.com">email@address.com</a>)
                        #if not address_regex.match(urlparse(href.get('href')).path) and len(urlparse(href.get('href')).path) > 0 and urlparse(href.get('href')).path not in URIs:
                        if not address_regex.match(urlparse(href.get('href')).path) and len(urlparse(href.get('href')).path) > 0:
                            #print "the new link is " + urlparse(href.get('href')).path
                            URIs.append(urlparse(href.get('href')).path)

    # Add email addresses from the page to the email array
    temp_emails = address_regex.findall(soup.prettify())

    # Take out all duplicate email addresses found
    for temp in temp_emails:
        if temp not in emails:
            emails.append(temp)

    new_link = 'ERROR' 
    # loop through all URIs in array looking for the current one being parsed
    for i in range(len(URIs)):
        # if the current URI is in the list of URIs already
        if u.path in URIs:
            #print "u.path is in URIs"
            new_index = URIs.index(u.path)+1
            if URIs[new_index][0] is not '/':
                new_link = u.netloc + '/' + URIs[new_index]
            else:
                new_link = u.netloc + URIs[new_index]
        # this would be the last link
        elif i >= len(URIs)-1:
            print "i is " + str(i) + " and len(URIs) is " + str(len(URIs))
            return True
        # else we have the first link
        else:
            # set the new_link to the first value in the URI list
            new_link = URIs[0]
            #print "new link: '" + new_link + "' and length = " + str(len(new_link))
            if new_link is not (None or '') and len(new_link) > 0:
                if new_link[0] is not '/':
                    new_link = u.netloc + '/' + new_link
                else:
                    new_link = u.netloc + new_link

    # recursively call scrape, continue adding email addresses
    # link, output_file, num, emails, URIs
    if new_link is not ('ERROR' or '' or len(new_link) > 0):
        scrape(new_link, output_file, num, emails, URIs)
    else:
        return True



if __name__ == '__main__':
    sys.exit(main())
