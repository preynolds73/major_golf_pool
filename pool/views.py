from django.shortcuts import render
import csv
import os
from django.core import serializers
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseBadRequest, JsonResponse
from pool.models import Team, Golfer
from unidecode import unidecode
import re
import requests
from bs4 import BeautifulSoup
import unicodedata

@staff_member_required
def admin_init(request):
    get_pro_pool(admin_init=True)
    # get_pro_pool()
    create_teams()
    context = {
        'test': "test"
    }
    return render(request, 'pool/admin_init.html', context)

def index(request):
    context = {
        'teams': Team.objects.all()
    }
    return render(request, 'pool/home.html', context)

def home(request):
    # is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    data = []
    tier1_golfer = ""
    tier2_golfer = ""
    tier3_golfer = ""
    tier4_golfer = ""
    tier1_score = 0
    tier2_score = 0
    tier3_score = 0
    tier4_score = 0
    if request.method == 'GET':
        #get_pro_pool()
        update_teams()
        owner_list = get_owner_list("owners")
        for name in owner_list:
            team = Team.objects.get(owner__exact=name)
            golfer_names = team.golfer.values_list('name', flat=True)
            for golfer_name in golfer_names:
                temp_golfer = Golfer.objects.get(name__exact=golfer_name)
                print(temp_golfer.name)
                if temp_golfer.tier == 1:
                    tier1_golfer = temp_golfer.name
                    tier1_score = temp_golfer.ttl_score
                elif temp_golfer.tier == 2:
                    tier2_golfer = temp_golfer.name
                    tier2_score = temp_golfer.ttl_score
                elif temp_golfer.tier == 3:
                    tier3_golfer = temp_golfer.name
                    tier3_score = temp_golfer.ttl_score
                elif temp_golfer.tier == 4:
                    tier4_golfer = temp_golfer.name
                    tier4_score = temp_golfer.ttl_score
                else:
                    print("Error")
            team_data = {
                'owner': name,
                'place': team.place,
                'total_score': team.total_score,
                'tier1_golfer': tier1_golfer,
                'tier1_score': tier1_score,
                'tier2_golfer': tier2_golfer,
                'tier2_score': tier2_score,
                'tier3_golfer': tier3_golfer,
                'tier3_score': tier3_score,
                'tier4_golfer': tier4_golfer,
                'tier4_score': tier4_score,
            }
            data.append(team_data)

        # teams = list(Team.objects.all().values())
        # serial_teams = serializers.serialize('json', teams)
        # golfers = list(Golfer.objects.all().values())
        return JsonResponse({'teams': data})
    return JsonResponse({'status': 'Invalid request'}, status=400)
    
    
    # context = {
    #     'teams': Team.objects.all()
    # }
    # return render(request, 'pool/home.html', context)

#class TeamListView(ListView):
#    model = Team
#    template_name = 'pool/home.html'
#    context_object_name = 'teams'
#    ordering = ['total_score']

def leaderboard(request):
    context = {
        'leaderboard': Golfer.objects.all().order_by('place')
    }
    return render(request, 'pool/leaderboard.html', context)

def odds(request):
    context = {
        'odds': Golfer.objects.all().order_by('tier')
    }
    return render(request, 'pool/odds.html', context)

def update_teams():
    print("test")
    par = 72
    team_list = get_owner_list("owners")
    placeList = []
    for name in team_list:
        sum_total = 0
        teamQuery = Team.objects.filter(owner__exact=name)
        team = Team.objects.get(owner__exact=name)
        #placeList = Team.objects.get().all().order_by('total_score')
        placeList = Team.objects.values_list('owner', flat=True).order_by('total_score')

        if placeList[0] == name:
            teamQuery.update(place=1)
        if placeList[1] == name:
            teamQuery.update(place=2)
        if placeList[2] == name:
            teamQuery.update(place=3)

        golfer_names = team.golfer.values_list('name', flat=True)

        for golfer_name in golfer_names:
            update_golfer = Golfer.objects.get(name__exact=golfer_name)
            if update_golfer.ttl_score == 604 or update_golfer.ttl_score == 404:
                sum_total = sum_total + ((update_golfer.r1_score + update_golfer.r2_score)-(par*2))
            else:
                print(golfer_name + " " + str(update_golfer.ttl_score))
                sum_total = sum_total + update_golfer.ttl_score

        teamQuery.update(total_score=sum_total)
        print(team.total_score)

"""
TODO: Make the teams selectable. 
This is just a placeholder
"""
def create_teams():

    team_list = get_owner_list("owners")
    for team in team_list:
        temp_t1,temp_t2,temp_t3,temp_t4 = get_owner_list("get_team", team)
        if not Team.objects.filter(owner__exact=team).exists():
            t1 = Golfer.objects.get(name__exact=temp_t1)
            t2 = Golfer.objects.get(name__exact=temp_t2)
            t3 = Golfer.objects.get(name__exact=temp_t3)
            t4 = Golfer.objects.get(name__exact=temp_t4)
            #tot_score = (t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score)
            tot_score = t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score

            new_team = Team.objects.create(owner=team, 
                                           total_score=tot_score)
            new_team.golfer.add(t1,t2,t3,t4)
            new_team.save()

    Team.objects.filter(owner="deleteme").delete()

    # if not Team.objects.filter(owner__exact="Boobs").exists():
    #     t1 = Golfer.objects.get(name__exact="Xander Schauffele")
    #     t2 = Golfer.objects.get(name__exact="Tommy Fleetwood")
    #     t3 = Golfer.objects.get(name__exact="Shane Lowry")
    #     t4 = Golfer.objects.get(name__exact="Denny McCarthy")
    #     #tot_score = (t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score)
    #     tot_score = t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score

    #     new_team = Team.objects.create(owner="Boobs", 
    #                                    total_score=tot_score)
    #     new_team.golfer.add(t1,t2,t3,t4)
    #     new_team.save()

    # Team.objects.filter(owner="deleteme").delete()

    # if not Team.objects.filter(owner__exact="Jimbo").exists():
    #     t1 = Golfer.objects.get(name__exact="Xander Schauffele")
    #     t2 = Golfer.objects.get(name__exact="Tommy Fleetwood")
    #     t3 = Golfer.objects.get(name__exact="Shane Lowry")
    #     t4 = Golfer.objects.get(name__exact="Denny McCarthy")
    #     #tot_score = (t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score)
    #     tot_score = t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score

    #     new_team = Team.objects.create(owner="Jimbo", 
    #                                    total_score=tot_score)
    #     new_team.golfer.add(t1,t2,t3,t4)
    #     new_team.save()

    # Team.objects.filter(owner="deleteme").delete()

def get_pro_pool(admin_init=False):
    espn_url = 'https://www.espn.com/golf/leaderboard'
    user = User.objects.filter(username='preynold').first()
    espn_page = requests.get(espn_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    })
    espn_data = BeautifulSoup(espn_page.text, 'html.parser')

    leaderboard_hdr = []
    golfer_place = "0"
    golfer_name = ""
    golfer_list = []
    golfer_scores_ttl = "0"
    golfer_scores_tdy = "0"
    golfer_scores_r1 = "0"
    golfer_scores_r2 = "0"
    golfer_scores_r3 = "0"
    golfer_scores_r4 = "0"
    golfer_thru = ""

    data_header = espn_data.find_all('tr', attrs={'class':re.compile('Table__TR Table__even')})
    for column in data_header:
        temp_hdr = [row.get_text() for row in column.find_all('th')]
        if not temp_hdr:
            continue
        else:
            leaderboard_hdr = temp_hdr

    leaderboard = espn_data.find_all('tr', attrs={'class':re.compile('PlayerRow__Overview PlayerRow__Overview--expandable Table__TR Table__even')})
    for golfers_html in leaderboard:
        golfer_row = [row.get_text() for row in golfers_html.find_all('td')]
        length = len(golfer_row)
        """
        The ESPN leaderboard changes format pretty much every day of the
        tournament so we have to structure the if statement to take into
        account how many times the loop will iterate.
        Pre-Tournament: ['', 'PLAYER', 'TEE TIME']
        1st Round: ['', 'POS', '', 'PLAYER', 'SCORE', 'TODAY', 'THRU', 'R1', 'R2', 'R3', 'R4', 'TOT']
        Final: ['', 'POS', 'PLAYER', 'SCORE', 'R1', 'R2', 'R3', 'R4', 'TOT', 'EARNINGS', 'FEDEX PTS'
        """
        for i in range(length):
            if leaderboard_hdr[i] == "POS":
                golfer_place = golfer_row[i]
                golfer_place = golfer_place.replace('T', '')
                if golfer_place == '-':
                    golfer_place = '150'
                golfer_place = int(golfer_place)

            if leaderboard_hdr[i] == "PLAYER":
                golfer_name = unidecode(golfer_row[i])
                golfer_list.append(unidecode(golfer_row[i]))
                update_golfer = Golfer.objects.filter(name__exact=golfer_name)
                update_golfer.update(place=golfer_place)

            if leaderboard_hdr[i] == "TEE TIME":
                golfer_thru = golfer_row[i]
                update_golfer = Golfer.objects.filter(name__exact=golfer_name)
                update_golfer.update(thru=golfer_thru)

            if leaderboard_hdr[i] == "THRU":
                golfer_thru = golfer_row[i]
                update_golfer = Golfer.objects.filter(name__exact=golfer_name)
                update_golfer.update(thru=golfer_thru)

            if leaderboard_hdr[i] == "SCORE":
                golfer_scores_ttl = golfer_row[i]
                update_golfer = Golfer.objects.filter(name__exact=golfer_name)
                if golfer_scores_ttl[0] == '-':
                    golfer_scores_ttl = str_to_neg(golfer_scores_ttl)
                elif golfer_scores_ttl[0] == '+':
                    golfer_scores_ttl = golfer_scores_ttl.replace('+', '')
                elif golfer_scores_ttl == 'E':
                    golfer_scores_ttl = '0'
                elif golfer_scores_ttl == "WD":
                    golfer_scores_ttl = "404"
                elif golfer_scores_ttl == "CUT":
                    golfer_scores_ttl = find_cut_score(golfer_name)
                    # golfer_scores_ttl = 11
                    update_golfer.update(cut=True)
                golfer_scores_ttl = int(golfer_scores_ttl)
                update_golfer.update(ttl_score=golfer_scores_ttl)

            if leaderboard_hdr[i] == "TODAY":
                golfer_scores_tdy = golfer_row[i]
                if golfer_scores_tdy[0] == '-':
                    golfer_scores_tdy = str_to_neg(golfer_scores_tdy)
                elif golfer_scores_tdy[0] == '+':
                    golfer_scores_tdy = golfer_scores_tdy.replace('+', '')
                elif golfer_scores_tdy == 'E':
                    golfer_scores_tdy = '0'
                elif golfer_scores_tdy == "WD":
                    #404/504 = WD/- respectively
                    golfer_scores_tdy = "404"
                elif golfer_scores_tdy == "-":
                    golfer_scores_tdy = "504"
                elif golfer_scores_tdy == "":
                    golfer_scores_tdy = "504"
                golfer_scores_tdy = int(golfer_scores_tdy)
                update_golfer = Golfer.objects.filter(name__exact=golfer_name)
                update_golfer.update(today_score=golfer_scores_tdy)

            if leaderboard_hdr[i] == "R1":
                if golfer_row[i] != "--":
                    golfer_scores_r1 = golfer_row[i]
                    golfer_scores_r1 = int(golfer_scores_r1)
                    update_golfer = Golfer.objects.filter(name__exact=golfer_name)
                    update_golfer.update(r1_score=golfer_scores_r1)

            if leaderboard_hdr[i] == "R2":
                if golfer_row[i] != "--":
                    golfer_scores_r2 = golfer_row[i]
                    golfer_scores_r2 = int(golfer_scores_r2)
                    update_golfer = Golfer.objects.filter(name__exact=golfer_name)
                    update_golfer.update(r2_score=golfer_scores_r2)

            """
            if leaderboard_hdr[i] == "TOT":
                golfer_scores_temp = golfer_row[i]
                update_golfer = Golfer.objects.get(name__exact=golfer_name)
                tot = update_golfer.ttl_score
                if tot == 404 or tot == 604:
                    golfer_scores_ttl = int(golfer_row[i]) - (2*par)
                    update_golfer = Golfer.objects.filter(name__exact=golfer_name)
                    update_golfer.update(ttl_score=golfer_scores_ttl)
            """
    
        if not Golfer.objects.filter(name__exact=golfer_name).exists():
            new_golfer = Golfer.objects.create(name=golfer_name, place=golfer_place, ttl_score=golfer_scores_ttl, thru=golfer_thru, today_score=golfer_scores_tdy)
            new_golfer.save()
    if admin_init == True:    
        get_odds(golfer_list)
    #Not sure why Django keeps adding a blank entry, but I just delete it every time
    Golfer.objects.filter(name="deleteme").delete()

def get_odds(golfer_list):
    url = "https://sportsbook.draftkings.com/leagues/golf/fedex-st.-jude-championship"
    page = requests.get(url)
    odds_data = BeautifulSoup(page.text, 'html.parser')
    i = 0
    tier = 1
    k = 1

    dk_golfer_list = []
    odds_list = [""]

    golfer_hdr = odds_data.find_all('ul', attrs={'class':re.compile('component-18-side-rail')})
    for golfer in golfer_hdr:
        temp_list = [row.get_text() for row in golfer.find_all('li')]
        if not temp_list:
            continue
        else:
            dk_golfer_list = temp_list

    column_hdr = odds_data.find_all('p', attrs={'class':re.compile('participants')})
    col = column_hdr[0].get_text()
    length = len(dk_golfer_list)

    odds_hdr = odds_data.find_all('li', attrs={'class':re.compile('component-18__cell')})
    for i in range(length):
        odds = odds_hdr[i]
        temp_list = [row.get_text() for row in odds.find_all('span')]
        if not temp_list:
            odds_list.append("500000")
        else:
            odds_list.append(temp_list)

    for i in range(length):
        golferObj = Golfer.objects.filter(name__exact=dk_golfer_list[i])
        new_str = str(odds_list[i+1])
        new_str = new_str.replace("['", "")
        new_str = new_str.replace("+", "")
        new_str = new_str.replace("']", "")
        #Python has 4 different 'dashes'...
        #So I have to some BS string manipulation
        if unicodedata.name(new_str[0]) == "MINUS SIGN":
            new_str = new_str[1:]
            new_str = "-" + new_str
        if new_str[0] == '-':
            new_str = str_to_neg(new_str)
        if new_str:
            new_int = int(new_str)
            if (golferObj.exists()):
            #if (golferObj.exists()):
                golferObj.update(odds=new_int)
            if k < 11:
                golferObj.update(tier=1)
            elif k >= 11 and k < 21:
                golferObj.update(tier=2)
            elif k >= 21 and k < 31:
                golferObj.update(tier=3)
            else:
                golferObj.update(tier=4)
            print("dk golfer: " + dk_golfer_list[i])
            print(new_int)
            print("golfer: " + golfer_list[i])
            print(k)
        k += 1

def str_to_neg(string):
    if string != "-":
        string = string.replace('-', '')
        temp_int = int(string)
        new_int = (0 - temp_int)
    else:
        #404/504 = WD/- respectively
        new_int = 504
    return new_int

def find_cut_score(golfer_name):
    par = 72
    update_golfer = Golfer.objects.get(name__exact=golfer_name)
    sum_total = ((update_golfer.r1_score + update_golfer.r2_score)-(par*2))
    return sum_total

def get_owner_list(option, owner=""):
    path = "/home/preynold/gitProjects/major_golf_pool/pool/"
    filename = path + "GolfPoolSelections.csv"
    header = []
    rows = []
    owner_list = []
    print (os.getcwd())

    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        header = next(csvreader)

        for row in csvreader:
            rows.append(row)
    if option == "get_team":
        for row in rows:
            if row[1] == owner:
                owner_list.append(row[1])
                tier1 = row[2].split("+")[0]
                tier1 = tier1.strip()
                tier2 = row[3].split("+")[0]
                tier2 = tier2.strip()
                tier3 = row[4].split("+")[0]
                tier3 = tier3.strip()
                tier4 = row[5].split("+")[0]
                tier4 = tier4.strip()
                return tier1, tier2, tier3, tier4

        return owner_list
    elif option == "owners":
        for row in rows:
            owner_list.append(row[1])
        return owner_list
