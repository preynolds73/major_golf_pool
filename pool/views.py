from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from pool.models import Team, Golfer
from unidecode import unidecode
import re
import requests
from bs4 import BeautifulSoup
import unicodedata


@staff_member_required
def admin_init(request):
    get_pro_pool()
    create_teams()
    context = {
        'test': "test"
    }
    return render(request, 'pool/admin_init.html', context)

def home(request):
    print("Home refresh")
    update_teams()
    context = {
        'teams': Team.objects.all().order_by('total_score')
    }
    return render(request, 'pool/home.html', context)

def leaderboard(request):
    context = {
        'leaderboard': Golfer.objects.all().order_by('place')
    }
    return render(request, 'pool/leaderboard.html', context)

def update_teams():
    par = 70
    team_list = ["Parker", "Parke"]
    for name in team_list:
        sum_total = 0
        teamQuery = Team.objects.filter(owner__exact=name)
        print(teamQuery)
        team = Team.objects.get(owner__exact=name)
        golfer_names = team.golfer.values_list('name', flat=True)
        print(golfer_names)

        for golfer_name in golfer_names:
            update_golfer = Golfer.objects.get(name__exact=golfer_name)
            if update_golfer.ttl_score == 604 or update_golfer.ttl_score == 404:
                sum_total = sum_total + ((update_golfer.r1_score + update_golfer.r2_score)-(par*2))
            else:
                sum_total = sum_total + update_golfer.ttl_score
            print(sum_total)

        teamQuery.update(total_score=sum_total)

"""
TODO: Make the teams selectable. 
This is just a placeholder
"""
def create_teams():

    if not Team.objects.filter(owner__exact="Parker").exists():
        t1 = Golfer.objects.get(name__exact="Beau Hossler")
        t2 = Golfer.objects.get(name__exact="Chad Ramey")
        t3 = Golfer.objects.get(name__exact="Victor Perez")
        t4 = Golfer.objects.get(name__exact="Daniel Berger")
        #tot_score = (t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score)
        tot_score = t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score

        new_team = Team.objects.create(owner="Parker", 
                                       total_score=tot_score)
        print(t1.ttl_score)
        print(t2.ttl_score)
        print(t3.ttl_score)
        print(t4.ttl_score)
        new_team.golfer.add(t1,t2,t3,t4)
        new_team.save()

    if not Team.objects.filter(owner__exact="Parke").exists():
        t1 = Golfer.objects.get(name__exact="Beau Hossler")
        t2 = Golfer.objects.get(name__exact="Chad Ramey")
        t3 = Golfer.objects.get(name__exact="Victor Perez")
        t4 = Golfer.objects.get(name__exact="Doug Ghim")
        #tot_score = (t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score)
        tot_score = t1.ttl_score + t2.ttl_score + t3.ttl_score + t4.ttl_score

        new_team = Team.objects.create(owner="Parke", 
                                       total_score=tot_score)
        print(t1.ttl_score)
        print(t2.ttl_score)
        print(t3.ttl_score)
        print(t4.ttl_score)
        new_team.golfer.add(t1,t2,t3,t4)
        new_team.save()


    
    Team.objects.filter(owner="deleteme").delete()

def get_pro_pool():
    espn_url = 'https://www.espn.com/golf/leaderboard'
    user = User.objects.filter(username='preynold').first()
    espn_page = requests.get(espn_url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
    })
    espn_data = BeautifulSoup(espn_page.text, 'html.parser')

    leaderboard_hdr = []
    golfer_place = ""
    golfer_name = ""
    golfer_list = []
    golfer_scores_ttl = ""
    golfer_scores_tdy = "504"
    golfer_scores_r1 = ""
    golfer_scores_r2 = ""
    golfer_scores_r3 = ""
    golfer_scores_r4 = ""
    golfer_thru = ""
    new_golfer = Golfer.objects.create()

    data_header = espn_data.find_all('tr', attrs={'class':re.compile('Table__TR Table__even')})
    for column in data_header:
        temp_hdr = [row.get_text() for row in column.find_all('th')]
        if not temp_hdr:
            continue
        else:
            leaderboard_hdr = temp_hdr

    leaderboard = espn_data.find_all('tr', attrs={'class':re.compile('PlayerRow__Overview PlayerRow__Overview--expandable Table__TR Table__even')})
    print(leaderboard_hdr)
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
            print(golfer_row)
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
                    golfer_scores_ttl = "604"
                    #golfer_scores_ttl = find_cut_score(golfer_row[i])
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
        
    get_odds(golfer_list)
    #Not sure why Django keeps adding a blank entry, but I just delete it every time
    Golfer.objects.filter(name="deleteme").delete()

def get_odds(golfer_list):
    url = "https://sportsbook.draftkings.com/leagues/golf/texas-children's-houston-open"
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
            if (golferObj.exists()) and (golfer_list[i] in dk_golfer_list):
                golferObj.update(odds=new_int)
            if k < 11:
                golferObj.update(tier=1)
            elif k >= 11 and k < 21:
                golferObj.update(tier=2)
            elif k >= 21 and k < 31:
                golferObj.update(tier=3)
            else:
                golferObj.update(tier=4)
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
