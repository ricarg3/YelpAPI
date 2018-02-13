from __future__ import print_function

import argparse
import requests
import sys

import xlsxwriter
import csv
import xlrd


from urllib.error import HTTPError
from urllib.parse import quote

API_KEY =  "lrIx8ciMCrJjoW5eIKFPpd2HK9XCaohg3_AWfDkB1KDt_2rwkAkJH1e5HpSJUolQuUIRL-Gzw7MxcET8-QWM89MDLOb56ePhV5AdjweCKGsW_PojTZCH2yENjVZ2WnYx"

API_HOST = "https://api.yelp.com"
SEARCH_PATH = "/v3/businesses/search"
BUSINESS_PATH = "/v3/businesses/"

DEFAULT_TERM = 'Salon'
DEFAULT_LOCATION = 'Irvine, CA'
SEARCH_LIMIT = "50"

def request(host, path, api_key,url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key
    }


    response = requests.request('GET', url, headers= headers, params= url_params)

    return response.json()


def search(api_key, term, location):
    url_params = {
        'term': term.replace(' ','+'),
        'location': location.replace(' ','+'),
        'limit': SEARCH_LIMIT
    }

    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business(api_key, business_id):
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)


def query_api(term, location):
    workbook = xlsxwriter.Workbook('YelpData.xlsx')
    worksheet = workbook.add_worksheet()

    col = 0
    worksheet.write(0, col,'providerID#')
    worksheet.write(0, col + 1, 'address')
    worksheet.write(0, col + 2, 'city')
    worksheet.write(0, col + 3, 'email')
    worksheet.write(0, col + 4, 'facebook')
    worksheet.write(0, col + 5, 'instagram')
    worksheet.write(0, col + 6, 'name')
    worksheet.write(0, col + 7, 'numberOfCustomers')
    worksheet.write(0, col + 8, 'password')
    worksheet.write(0, col + 9, 'phonenumber')
    worksheet.write(0, col + 10, 'price')
    worksheet.write(0, col + 11, 'profession')
    worksheet.write(0, col + 12, 'serviceType')
    worksheet.write(0, col + 13, 'skillLevel')
    worksheet.write(0, col + 14, 'state')
    worksheet.write(0, col + 15, 'student')
    worksheet.write(0, col + 16, 'zip')


    response = search(API_KEY, term, location)
    businesses = response.get('businesses')

    if not businesses:

        return

    for i in range(int(SEARCH_LIMIT)):
        business_id = businesses[i]['id']

        response = get_business(API_KEY, business_id)

         # providerId
        worksheet.write(i+1,col,i)

        # address
        if (response['location']['address2'] != None and response['location']['address3'] != None):
            worksheet.write(i+1,col+1,response['location']['address1'] + " " + response['location']['address2'] + " " + response['location']['address3'])

        elif(response['location']['address2'] != None):
            worksheet.write(i+1, col + 1, response['location']['address1'] + " " + response['location']['address2'])

        else:
            worksheet.write(i+1, col + 1, response['location']['address1'])

        # city
        worksheet.write(i+1, col + 2, response['location']['city'])

        # email

        # facebook
        # insta

        # name
        worksheet.write(i+1, col + 6, response['name'])

        # numberOfCustomers

        worksheet.write(i+1, col + 7, response['review_count'])

        # password

        # phonenumber
        worksheet.write(i+1, col + 9, response['phone'])

        # price (range for Salons)
        if(response['price'] == '$'):
            worksheet.write(i+1, col + 10, '$0-$10')

        elif(response['price'] == '$$'):
            worksheet.write(i+1, col + 10, '$11-$30')

        elif(response['price'] == '$$$'):
            worksheet.write(i+1, col + 10, '$31-$60')
        else:
            worksheet.write(i+1, col + 10, '$60-')

        #profession
        # serviceType (Salon for salons)
        worksheet.write(i+1, col + 12, 'Salon')

        # skillLevel (10 for salons or Not required for Salons)
        worksheet.write(i+1, col + 13, '10')

        # state
        worksheet.write(i+1, col + 14,response['location']['state'])
        # student
        worksheet.write(i+1, col + 15, 'no')
        # zip
        worksheet.write(i+1, col + 16,response['location']['zip_code'])

           ###
           ####
        i += 1

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q','--term',dest='term',default=DEFAULT_TERM,type=str, help='Search term (default: %(default)s)')

    parser.add_argument('-l','--location',dest='location', default=DEFAULT_LOCATION,type=str,help='Search location (default: %(default)s)')

    input_values = parser.parse_args()

    try:
        query_api(input_values.term, input_values.location)
    except HTTPError as error:
        sys.exit('Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
            error.code,
            error.url,
            error.read(),

        ))

    wb = xlrd.open_workbook('YelpData.xlsx')
    sh = wb.sheet_by_name('Sheet1')
    file = open('YelpData.csv','w')
    wr = csv.writer(file, quoting=csv.QUOTE_ALL)

    for rownum in range(sh.nrows):
        wr.writerow(sh.row_values(rownum))

    file.close()

if __name__ == '__main__':
    main()

