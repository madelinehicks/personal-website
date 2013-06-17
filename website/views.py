from __future__ import division
from django.http import HttpResponse
from django.template import loader, Context
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
import settings
import models
import logging
import os
import urllib, re, bs4
import common
import datetime


def content(request):
    posts = models.Post.objects.order_by('-created_on')
    tags = models.Tag.objects.all()
    t = loader.get_template(os.path.join(os.getcwd(), 'templates', 'content.html'))
    return HttpResponse(t.render(Context({ 'posts': posts, 'tags': tags, 'settings': settings })))

@csrf_exempt        
def fb_log(request):
    logging.debug(str(request))
    print request
    return HttpResponse()

def etsy(request):
    send_mail('Pageview at /etsy/', str(request), 'mad@madelinehicks.com', ['mad@madelinehicks.com'], fail_silently=False)
    print request
    return HttpResponse(loader.get_template('etsy.html').render(Context()))

def trade(request):
    return HttpResponse(loader.get_template('trade-beta.html').render(Context()))

REGIONS = {
'The Citadel': 10000033, #
'Lonetrek': 10000016, # 
'The Forge': 10000002, #
'Heimatar': 10000030, #
'Molden Heath': 10000028,
'Metropolis': 10000042, #
'Sinq Laison': 10000032, #
}

CACHE = { }

def route_lookup(request):
    # there is NO WAY IN HELL i will be able to read this code in 6 months. damnit.
    
    # first collect all profitable trade routes
    try:
        origin = request.GET['start'] and [ common.EMPIRE_SPACE[request.GET['start'].title()] ] or REGIONS.values()
        destination = request.GET['end'] and [ common.EMPIRE_SPACE[request.GET['end'].title()] ] or REGIONS.values()
    except KeyError:
        return HttpResponse('Origin or destination system/region not found.')
    capital = (int(re.sub('[^0-9.]', '', request.GET['capital'])) * 1000000) or 100000000
    cargo = int(re.sub('[^0-9.]', '', request.GET['cargo'])) or 10000
    if len(origin) > 1 or origin[0] < 30000000: # regions or region to system, not yet supported
        if len(destination) > 1 or destination[0] < 30000000:
            lookup_type = 'Regions'
        else:
            return HttpResponse('Region to System lookup not yet supported.')
    else: # system to region or system to system
        if len(destination) > 1 or destination[0] < 30000000:
            lookup_type = 'SystemToRegion'
        else:
            lookup_type = 'Systems'

    routes = list()
    by_item = dict()
    for region in origin:
        for end in destination:
            url = ('http://eve-central.com/home/tradefind_display.html?set=1&'
                'qtype={qtype}&age=24&minprofit=2000000&size={cargo}&limit=50'
                '&sort=sprofit&prefer_sec=1&fromt={origin}&to={destination}'.format(
                cargo=cargo, origin=region, destination=end, qtype=lookup_type))
            #print url
            jh = urllib.urlopen(url).read()
            soup = bs4.BeautifulSoup(jh)
            td = soup.find(id="bodyText").findAll('td')
            
            for i in range(0, len(td), 13):
                e = [t.text for t in td[i:i+13]]
                r = dict()
                r['composite'] = False
                r['from'] = e[0][6:]
                r['to'] = e[1][4:]
                r['jumps'] = int(re.sub('[^0-9.]', '', e[2]))
                r['item'] = e[3][6:]
                item_nums = re.sub('[^0-9 ]', '', e[7]).split(' ')
                r['item_num'] = int(item_nums[2])
                r['sell_avail'] = int(item_nums[3])
                r['buy_avail'] = int(item_nums[5])
                r['ask'] = float(re.sub('[^0-9.]', '', e[4]))
                r['bid'] = float(re.sub('[^0-9.]', '', e[5]))
                r['profit'] = float(re.sub('[^0-9.]', '', e[10]))
                r['capital'] = r['ask'] * r['item_num']
                r['ratio'] = round(r['capital'] / r['profit'], 2)
                try:
                    item = common.ITEMS[r['item']]
                    r['vol'] = item[0]
                    r['id'] = item[1]
                    r['cargo'] = (r['item_num'] * r['vol']) / cargo
                except Exception:
                    print 'error getting volume info for', r['item']
                    r['cargo'] = '?'
                    r['id'] = 'notfound'
                    r['vol'] = 0.01
                try:
                    r['to_region'] = common.SYSTEM_TO_REGION[' '.join(r['to'].split('-')[0].strip().split(' ')[:-1])]
                except Exception:
                    print 'error looking up region for system', r['to']
                    r['to_region'] = '?'
                if r['ask'] <= capital:
                    by_item.setdefault(r['id'], []).append(r)
    condensed = list()
    # now combine routes by item and origin and destination stations
    for k, v in by_item.iteritems():
        temp = dict()
        for r in v:
            temp.setdefault((r['from'], r['to']), []).append(r)
        cargo_max = int(cargo / r['vol']) # what's the max # of items that will fit in our cargo hold?
        if not cargo_max:
            continue # if none, skip this route
        for od, e in temp.iteritems():
            # find minimum of all bids / asks at those stations, capital to risk, and cargo space
            l = len(e)
            r = e[0].copy()
            if l > 1:
                #cargo_max = int(cargo / r['vol']) # what's the max # of items we can buy?
                # what's our market depth?
                sell_orders = sorted(set([(m['sell_avail'], m['ask']) for m in e]), key=lambda p: p[1])
                buy_orders = sorted(set([(m['buy_avail'], m['bid']) for m in e]), key=lambda p: p[1], reverse=True)
                buy_vol = sum([m[0] for m in buy_orders])
                bought = 0
                spent = 0.0
                while True:
                    if not sell_orders:
                        break
                    # 3 exit conditions - capital allowance, cargo bay limit, buy orders exhausted
                    exit = min(int((capital - spent) / sell_orders[0][1]), (cargo_max - bought), buy_vol, sell_orders[0][0])
                    if exit < sell_orders[0][0]:
                        bought += exit
                        spent += sell_orders[0][1] * exit
                        break
                    else:
                        bought += sell_orders[0][0]
                        spent += sell_orders[0][0] * sell_orders[0][1]
                        buy_vol -= sell_orders[0][0]
                        sell_orders.pop(0)
                sold = 0
                made = 0.0
                #for order in buy_orders:
                while sold < bought:
                    if buy_orders: # we could run out of buy orders if the code above breaks. shrug, better safe than sorry
                        highest_buy = buy_orders.pop(0)
                        if bought - sold < highest_buy[0]: # amount to buy is less than amount for sale in highest buy order
                            made += ((bought - sold) * highest_buy[1])
                            sold = bought
                        else: # buy up the entire order
                            made += (highest_buy[0] * highest_buy[1])
                            sold += highest_buy[0]
                    
                r['composite'] = True
                r['item_num'] = bought
                r['ask'] = spent / bought
                r['bid'] = made / sold
                r['capital'] = spent
                r['cargo'] = (bought * r['vol']) / cargo
                r['profit'] = (made * (1 - float(request.GET['tax']) / 100)) - spent
                r['ratio'] = round(r['capital'] / r['profit'], 2)
            if r['item_num'] > cargo_max:
                r['item_num'] = cargo_max
                r['capital'] = r['item_num'] * r['ask']
                r['cargo'] = (r['item_num'] * r['vol']) / cargo
                r['profit'] = (r['bid'] - r['ask']) * r['item_num']
                r['ratio'] = round(r['capital'] / r['profit'], 2)
            if r['profit'] > 1000000 and r['capital'] <= capital:
                routes.append(r)
    
    return HttpResponse(loader.get_template('results.html').render(Context({'routes': routes})))       
