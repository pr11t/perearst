import urllib.request
import urllib.parse
import csv
from bs4 import BeautifulSoup
import argparse

def get_free_doctors(area,open_spaces=True,):
    # TODO allow docs with no open spaces
    ostring = ""
    if open_spaces:
        ostring = "&kohti=1"

    baseurl = "http://mveeb.sm.ee/ctrl/ee/Nimistud/index/?kood=&jur_isik=&teeninduspiirkond=%s&otsi=Otsi"+ostring
    # soup1 find the table
    url = baseurl % urllib.parse.quote(area)
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
    register = soup.find_all("table","register")
    # soup2 find people in table and add to list
    bs = BeautifulSoup(str(register), "html.parser")
    results = []
    for row in bs.findAll('tr'):
        try:
            aux = row.findAll('td')
            # switch firstname lastname
            name = aux[1].string.split(' - ')[1]
            name = name.split(' ')
            name = name[1]+" "+name[0]
            results.append(name)
        except:
            pass
    
    return results

def get_rating_from_tervisetrend(name,):
    name = name.replace("+"," ")
    baseurl = "http://www.tervisetrend.ee/arstid/otsing?keywords=%s"
    url = baseurl % urllib.parse.quote(name)
    soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
    # hope that only one doctor matches
    rating = soup.find_all("span", "rating")
    print(rating)
    return rating[0].string.replace(',','.')

def parsedocs(doclist):
    docrating = []
    parsed = 0
    for doc in doclist:
        print("[%i / %i]" % (parsed,len(doclist)))
        try:
            rating = get_rating_from_tervisetrend(doc)
        except IndexError:
            rating = "0"
        parsed += 1
        docrating.append({'name':doc,'rating':rating})
        #print({'name':doc,'rating':rating})

    return docrating

def tocsv(listofdocs,filename):
    keys = set()
    for d in listofdocs:
        keys.update(d.keys())

    with open(filename, 'w') as output_file:
        dict_writer = csv.DictWriter(
            output_file, fieldnames=keys, restval='-', delimiter=';')
        dict_writer.writeheader()
        dict_writer.writerows(listofdocs)

def main(args):
    print('Otsin arste kellel on vabu kohti')
    docs = get_free_doctors(args.piirkond)
    print('Otsin arstide reitinguid tervisetrendist')
    docrating = parsedocs(docs)
    if len(args.fail) > 1:
        tocsv(docrating,filename=args.fail)
    newlist = sorted(docrating, key=lambda k: k['rating']) 
    for i in newlist:
        print("%s %s" % (i['name'], i['rating']))



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-piirkond', help="Arsti teeninduspiirkond --piirkond Tartu --piirkond 'Mustamäe' --piirkond 'Viljandi Vald'", required=True)
    parser.add_argument('-fail', help="csv fail kuhu väljund salvestada, defaultis ei salvestata", default="")
    args = parser.parse_args()
    main(args=args)
