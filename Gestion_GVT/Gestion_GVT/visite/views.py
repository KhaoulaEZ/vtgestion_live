from django.db.models.aggregates import Count
from django.db.models.expressions import F
from users.models import Users
from facture.models import Facture
from proprietaire.models import Proprietaire
from vehicule.models import Vehicule
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from visite.models import Visite
from django.http import HttpResponse
from django.contrib.auth.models import User
import xlwt
from django.db.models import Sum
from io import BytesIO
from django.template.loader import render_to_string

import tempfile
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.generic import ListView
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.contrib.staticfiles import finders
# Create your views here.
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import VisiteSerializer
from .models import Visite

@login_required(login_url='/users/login')
def add_test_v(request):
    if request.method == 'GET':
        return render(request, 'visite/addV.html')

    if request.method == 'POST':
        print(request.POST)
        context = {
            'values': request.POST,
        }
        # partie proprietaire
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        nom = nom.capitalize()
        prenom = prenom.capitalize()
        Cin = request.POST['CIN']
        ville = request.POST['VILLE']
        quartier = request.POST['QUARTIER']
        tele = request.POST['Tele']
        nom_c = nom + ' ' + prenom
        nom_c = nom_c.lower()
        proprietaire = Proprietaire(nom_c=nom_c,
                                    nom=nom, prenom=prenom, Cin=Cin, ville=ville, quartier=quartier, Tele=tele)
        proprietaire.save()
        # partie vehicule
        matricule = request.POST['Matricule']
        marque = request.POST['Marque']
        type_vh = request.POST['type_vh']
        puissance = int(request.POST['puissance'])
        vehicule = Vehicule(proprietaire=proprietaire, matricule=matricule,
                            marque=marque, type=type_vh, puissance_fiscale=puissance)
        vehicule.save()
        # partie Facture
        Narsa = int(request.POST['Narsa'])
        taxe_fiscale = int(request.POST['taxe_fiscale'])
        taxe_communale = int(request.POST['taxe_communale'])
        paiment = request.POST['paiment']
        montant_net = int(request.POST['montant_net'])
        resultat = request.POST['resultat']
        # Narsa = 0
        # taxe_communale = 0
        # if resultat == 'favorable':
        #     Narsa = 30
        #     taxe_communale = 50
        numero = request.POST['numero']
        montant_total = Narsa + taxe_fiscale + taxe_communale + (6 / 5) * montant_net
        taxe_paiment = 0
        if paiment == 'Espèce':
            taxe_paiment = montant_total / 400
        montant_total += taxe_paiment
        montant_total = round(float(montant_total), 2)
        facture = Facture(Narsa=Narsa, taxe_fiscale=taxe_fiscale, taxe_paiment=taxe_paiment, numero=numero,
                          taxe_communale=taxe_communale, paiment=paiment, montant_net=montant_net,
                          montant_total=montant_total)
        facture.save()
        # visite
        date_visite = request.POST['date_visite']
        date_expiration = request.POST['date_expiration']
        type_visite = request.POST['type_visite']
        resultat = request.POST['resultat']
        observation = request.POST['observation']
        utilisateur = Users(Utilisateur_nom=nom, Utilisateur_prenom=prenom)
        utilisateur.save()
        visite = Visite(vehicule=vehicule, Users=utilisateur, facture=facture,
                        observation=observation, date_visite=date_visite, date_expiration=date_expiration,
                        prix=montant_total, paiment=paiment, type=type_visite, resultat=resultat)
        visite.save()
        messages.success(request, 'Visite est enregistrée')
        return redirect('visite')

@api_view(['Get'])
def all_visite(request):
    visites=Visite.objects.all()
    serialization =VisiteSerializer(visites,many=True)
    return Response(serialization.data)


@api_view(['Get'])
def get_one_visite(request,id):
    visite=Visite.objects.all(id=id)
    serialization =VisiteSerializer(visite)
    return Response(serialization.data)

@api_view(['POST'])
def add_visite(request,id):
    serializer=VisiteSerializer(data=data.request.data,many=True)
    if serializer.is_valid():
        serializer.save()
    return Response(serializer.data)

def search(matricule, client, cin, datev, datee):
    L = client.split()
    s = ' '.join(L)
    s = s.lower()
    proprietaires = Proprietaire.objects.filter(
        nom_c__startswith=s, Cin__startswith=cin)
    # | Proprietaire.objects.filter(nom_c__startswith=nom_cc, Cin__startswith=cin)
    vehicules = Vehicule.objects.filter(
        proprietaire__in=proprietaires, matricule__startswith=matricule)
    visite = Visite.objects.filter(
        vehicule__in=vehicules, date_visite__startswith=datev, date_expiration__startswith=datee)
    return visite


def search_visite(request):
    if request.method == 'POST':
        matricule = request.POST['search_Matricule']
        client = request.POST['search_Client']
        cin = request.POST['search_Cin']
        datev = request.POST['search_DateV']
        datee = request.POST['search_DateE']
        visite = search(matricule, client, cin, datev, datee)
        paginator = Paginator(visite, 20)
        page_number = request.GET.get('page')
        page_obj = Paginator.get_page(paginator, page_number)
        context = {
            'search_Matricule': matricule,
            'search_Client': client,
            'search_Cin': cin,
            'search_DateV': datev,
            'search_DateE': datee,
            'page_obj': page_obj,
        }
        return render(request, 'visite/hm.html', context)


def export_users_xls(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=visites'+str(datetime.datetime.now()) + \
        '.xls'

    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Visites')
    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['N°', 'Date Visite ', 'Date Expiration', 'Prix', 'Mode.R',
               'Type VT', 'Matricule', 'Type VH', 'Client', 'CIN', 'Ville', 'N° tél', ]

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    visites = Visite.objects.all().values_list('date_visite', 'date_expiration', 'prix', 'paiment',
                                               'type', 'vehicule_id')
    rows = visites
    for row in rows:
        vehicule = Vehicule.objects.get(pk=row[5])
        proprietaire = Proprietaire.objects.get(pk=vehicule.proprietaire_id)
        row = row[:5]+(vehicule.matricule, vehicule.type, proprietaire.nom+" " +
                       proprietaire.prenom, proprietaire.Cin, proprietaire.ville, proprietaire.Tele)
        row_num += 1
        ws.write(row_num, 0, str(row_num), font_style)
        for col_num in range(len(row)):
            ws.write(row_num, col_num+1, row[col_num], font_style)

    wb.save(response)
    return response


def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those
    resources
    """
    result = finders.find(uri)
    if result:
        if not isinstance(result, (list, tuple)):
            result = [result]
        result = list(os.path.realpath(path) for path in result)
        path = result[0]
    else:
        sUrl = settings.STATIC_URL        # Typically /static/
        sRoot = settings.STATIC_ROOT      # Typically /home/userX/project_static/
        mUrl = settings.MEDIA_URL         # Typically /media/
        mRoot = settings.MEDIA_ROOT       # Typically /home/userX/project_static/media/

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

    # make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path


def render_pdf_view(request, id):
    date = str(datetime.date.today())
    print(date)
    template_path = 'visite/pdf.html'
    visite = Visite.objects.get(pk=id)
    facture = Facture.objects.get(pk=visite.facture_id)
    vehicule = Vehicule.objects.get(pk=visite.vehicule_id)
    client = Proprietaire.objects.get(pk=vehicule.proprietaire_id)
    Tva = "{:.2f}".format(facture.montant_net/5)
    ttc = "{:.2f}".format(facture.montant_net*6/5)
    narsa1 = "{:.2f}".format(facture.Narsa*2/3)
    narsa2 = "{:.2f}".format(facture.Narsa/3)
    context = {'facture': facture, 'visite': visite, 'narsa1': narsa1, 'narsa2': narsa2,
               'vehicule': vehicule, 'client': client, 'date': date, 'TVA': Tva, 'TTC': ttc}
    # Create a Django response object, and specify content_type as pdf
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Facture.pdf"'
    # find the template and render it.
    template = get_template(template_path)
    html = template.render(context)
    # create a pdf
    pisa_status = pisa.CreatePDF(
        html, dest=response)
    # , link_callback=link_callback)
    # if error then show some funy view
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    # return render(request, 'visite/pdf.html', context)
    return response


def zero(string):
    if string is None:
        return 0
    else:
        return round(float(string), 2)


@login_required(login_url='/users/login')
def redevances(request):
    if request.method == 'GET':
        jour = str(datetime.date.today())
        annee = jour[:4]
        context = {
            'yearm': annee,
            'year': annee
        }
        return render(request, 'stats/redevances.html', context)
    if request.method == 'POST':
        yearm = request.POST['yearm']
        # year = request.POST['year']
        year = yearm
        narsay = Visite.objects.filter(date_visite__startswith=year)
        narsam = []
        fiscalem = []
        communalem = []
        for i in range(12):
            if i < 9:
                dat = yearm+"-0"+str(i+1)
            else:
                dat = yearm+"-"+str(i+1)
            narsa = Visite.objects.filter(date_visite__startswith=dat)
            fiscalem.append(zero(narsa.aggregate(Sum('facture__taxe_fiscale'))[
                'facture__taxe_fiscale__sum']))
            communalem.append(zero(narsa.aggregate(Sum('facture__taxe_communale'))[
                'facture__taxe_communale__sum']))
            narsam.append(zero(narsa.aggregate(Sum('facture__Narsa'))
                               ['facture__Narsa__sum']))
        fiscalem.append(sum(fiscalem))
        communalem.append(sum(communalem))
        narsam.append(sum(narsam))
        fiscaley = zero(narsay.aggregate(Sum('facture__taxe_fiscale'))[
                        'facture__taxe_fiscale__sum'])
        communaley = zero(narsay.aggregate(Sum('facture__taxe_communale'))[
                          'facture__taxe_communale__sum'])
        narsay = zero(narsay.aggregate(Sum('facture__Narsa'))
                      ['facture__Narsa__sum'])
        s11 = year+'-01-01'
        s12 = year+'-03-31'
        s21 = year+'-04-01'
        s22 = year+'-06-30'
        s31 = year+'-07-01'
        s32 = year+'-09-30'
        s41 = year+'-10-01'
        s42 = year+'-12-31'
        narsa1 = Visite.objects.filter(date_visite__range=[s11, s12])
        narsa2 = Visite.objects.filter(date_visite__range=[s21, s22])
        narsa3 = Visite.objects.filter(date_visite__range=[s31, s32])
        narsa4 = Visite.objects.filter(date_visite__range=[s41, s42])
        fiscale1 = zero(narsa1.aggregate(Sum('facture__taxe_fiscale'))[
                        'facture__taxe_fiscale__sum'])
        communale1 = zero(narsa1.aggregate(Sum('facture__taxe_communale'))[
                          'facture__taxe_communale__sum'])
        narsa1 = zero(narsa1.aggregate(Sum('facture__Narsa'))
                      ['facture__Narsa__sum'])
        fiscale2 = zero(narsa2.aggregate(Sum('facture__taxe_fiscale'))[
                        'facture__taxe_fiscale__sum'])
        communale2 = zero(narsa2.aggregate(Sum('facture__taxe_communale'))[
                          'facture__taxe_communale__sum'])
        narsa2 = zero(narsa2.aggregate(Sum('facture__Narsa'))
                      ['facture__Narsa__sum'])
        fiscale3 = zero(narsa3.aggregate(Sum('facture__taxe_fiscale'))[
                        'facture__taxe_fiscale__sum'])
        communale3 = zero(narsa3.aggregate(Sum('facture__taxe_communale'))[
                          'facture__taxe_communale__sum'])
        narsa3 = zero(narsa3.aggregate(Sum('facture__Narsa'))
                      ['facture__Narsa__sum'])
        fiscale4 = zero(narsa4.aggregate(Sum('facture__taxe_fiscale'))[
                        'facture__taxe_fiscale__sum'])
        communale4 = zero(narsa4.aggregate(Sum('facture__taxe_communale'))[
                          'facture__taxe_communale__sum'])
        narsa4 = zero(narsa4.aggregate(Sum('facture__Narsa'))
                      ['facture__Narsa__sum'])
        mois = {'narsa': narsam, 'fiscale': fiscalem, 'communale': communalem}
        taxey = {'narsa': narsay, 'fiscale': fiscaley, 'communale': communaley}
        taxes1 = {'narsa': narsa1, 'fiscale': fiscale1,
                  'communale': communale1}
        taxes2 = {'narsa': narsa2, 'fiscale': fiscale2,
                  'communale': communale2}
        taxes3 = {'narsa': narsa3, 'fiscale': fiscale3,
                  'communale': communale3}
        taxes4 = {'narsa': narsa4, 'fiscale': fiscale4,
                  'communale': communale4}
        values = {'mois': mois, 'year': taxey, 't1': taxes1,
                  't2': taxes2, 't3': taxes3, 't4': taxes4}
        context = {
            'yearm': yearm,
            'year': year,
            'values': values
        }
        return render(request, 'stats/redevances.html', context)


def CA(request):
    if request.method == 'GET':
        jour = str(datetime.date.today())
        mois = jour[:7]
        annee = jour[:4]
        context = {
            'jour': jour,
            'month': mois,
            'year': annee
        }
        return render(request, 'stats/CA.html', context)

    if request.method == 'POST':
        jour = request.POST['jour']
        month = request.POST['month']
        year = request.POST['year']
        vj = Visite.objects.filter(date_visite__startswith=jour)
        vm = Visite.objects.filter(date_visite__startswith=month)
        vy = Visite.objects.filter(date_visite__startswith=year)
        year_1 = int(year)-1
        year_s = str(year_1)
        vy_s = Visite.objects.filter(date_visite__startswith=year_s)
        vjh = zero(vj.aggregate(Sum('facture__montant_net'))[
            'facture__montant_net__sum'])
        vmh = zero(vm.aggregate(Sum('facture__montant_net'))[
            'facture__montant_net__sum'])
        vyh = zero(vy.aggregate(Sum('facture__montant_net'))[
            'facture__montant_net__sum'])
        vjc = zero(vj.aggregate(Sum('facture__montant_total'))[
            'facture__montant_total__sum'])
        vmc = zero(vm.aggregate(Sum('facture__montant_total'))[
            'facture__montant_total__sum'])
        vyc = zero(vy.aggregate(Sum('facture__montant_total'))[
            'facture__montant_total__sum'])
        dyttc = vyc-zero(vy_s.aggregate(Sum('facture__montant_total'))[
            'facture__montant_total__sum'])
        dy = vyh-zero(vy_s.aggregate(Sum('facture__montant_net'))[
            'facture__montant_net__sum'])
        b = 0+(dy >= 0)
        print(b)
        s_jour = {'ht': vjh, 'ttc': vjc}
        s_month = {'ht': vmh, 'ttc': vmc, }
        s_year = {'ht': vyh, 'ttc': vyc, 'diffht': dy, 'diffttc': dyttc}
        values = {'jour': s_jour, 'month': s_month, 'year': s_year}
        context = {
            'jour': jour,
            'month': month,
            'year': year,
            'year_1': year_1,
            'bool': b,
            'values': values
        }
        return render(request, 'stats/CA.html', context)


def VT(request):
    if request.method == 'GET':
        jour = str(datetime.date.today())
        mois = jour[:7]
        annee = jour[:4]
        context = {
            'jour': jour,
            'month': mois,
            'year': annee
        }
        return render(request, 'stats/VT.html', context)

    if request.method == 'POST':
        jour = request.POST['jour']
        month = request.POST['month']
        year = request.POST['year']
        vtpj = Visite.objects.filter(
            type='VTP', date_visite__startswith=jour).count()
        mutj = Visite.objects.filter(
            type='MUT', date_visite__startswith=jour).count()
        volj = Visite.objects.filter(
            type='VOL', date_visite__startswith=jour).count()
        vcj = Visite.objects.filter(
            type='VC', date_visite__startswith=jour).count()
        vtpm = Visite.objects.filter(
            type='VTP', date_visite__startswith=month).count()
        mutm = Visite.objects.filter(
            type='MUT', date_visite__startswith=month).count()
        volm = Visite.objects.filter(
            type='VOL', date_visite__startswith=month).count()
        vcm = Visite.objects.filter(
            type='VC', date_visite__startswith=month).count()
        vtpy = Visite.objects.filter(
            type='VTP', date_visite__startswith=year).count()
        muty = Visite.objects.filter(
            type='MUT', date_visite__startswith=year).count()
        voly = Visite.objects.filter(
            type='VOL', date_visite__startswith=year).count()
        vcy = Visite.objects.filter(
            type='VC', date_visite__startswith=year).count()
        s_jour = {'vtp': vtpj, 'mut': mutj, 'vol': volj, 'vc': vcj}
        s_month = {'vtp': vtpm, 'mut': mutm, 'vol': volm, 'vc': vcm}
        s_year = {'vtp': vtpy, 'mut': muty, 'vol': voly, 'vc': vcy}
        values = {'jour': s_jour, 'month': s_month, 'year': s_year}
        context = {
            'jour': jour,
            'month': month,
            'year': year,
            'values': values
        }
        return render(request, 'stats/VT.html', context)


def VH(request):
    if request.method == 'GET':
        jour = str(datetime.date.today())
        mois = jour[:7]
        annee = jour[:4]
        context = {
            'jour': jour,
            'month': mois,
            'year': annee
        }
        return render(request, 'stats/VH.html', context)

    if request.method == 'POST':
        print(request.POST)
        jour = request.POST['jour']
        month = request.POST['month']
        year = request.POST['year']
        vehicules = Vehicule.objects.filter(type='VL')
        vlj = Visite.objects.filter(
            vehicule__in=vehicules, date_visite__startswith=jour,).count()
        vlm = Visite.objects.filter(
            vehicule__in=vehicules, date_visite__startswith=month,).count()
        vly = Visite.objects.filter(
            vehicule__in=vehicules, date_visite__startswith=year,).count()
        vehicules = Vehicule.objects.filter(type='PL+15T')
        plj = Visite.objects.filter(
            vehicule__in=vehicules, date_visite__startswith=jour,).count()
        plm = Visite.objects.filter(
            vehicule__in=vehicules, date_visite__startswith=month,).count()
        ply = Visite.objects.filter(
            vehicule__in=vehicules, date_visite__startswith=year,).count()
        pj = Visite.objects.filter(
            date_visite__startswith=jour,).count()-plj-vlj
        pm = Visite.objects.filter(
            date_visite__startswith=month,).count()-plm-vlm
        py = Visite.objects.filter(
            date_visite__startswith=year,).count()-ply-vly
        s_jour = {'vl': vlj, 'pl': plj, 'p': pj}
        s_month = {'vl': vlm, 'pl': plm, 'p': pm}
        s_year = {'vl': vly, 'pl': ply, 'p': py}
        values = {'jour': s_jour, 'month': s_month, 'year': s_year}
        context = {
            'jour': jour,
            'month': month,
            'year': year,
            'values': values
        }
        return render(request, 'stats/VH.html', context)


@login_required(login_url='/users/login')
def index(request):
    visite = Visite.objects.all()
    if request.method == 'POST':
        search_str = json.loads(request.body).get('searchText')
        print(search_str)
        visite = Visite.objects.filter(date_visite=search_str)

    paginator = Paginator(visite, 20)
    page_number = request.GET.get('page')
    page_obj = Paginator.get_page(paginator, page_number)
    context = {
        'page_obj': page_obj,
        'visite': visite,
    }
    return render(request, 'visite/hm.html', context)
    #return render(request, 'visite/home.html', context)


@login_required(login_url='/users/login')
def add(request):
    if request.method == 'GET':
        return render(request, 'visite/add_visite.html')

    if request.method == 'POST':
        print(request.POST)
        context = {
            'values': request.POST,
        }
        # partie proprietaire
        nom = request.POST['nom']
        prenom = request.POST['prenom']
        nom = nom.capitalize()
        prenom = prenom.capitalize()
        Cin = request.POST['CIN']
        ville = request.POST['VILLE']
        quartier = request.POST['QUARTIER']
        tele = request.POST['Tele']
        nom_c = nom+' '+prenom
        nom_c = nom_c.lower()
        proprietaire = Proprietaire(nom_c=nom_c,
                                    nom=nom, prenom=prenom, Cin=Cin, ville=ville, quartier=quartier, Tele=tele)
        proprietaire.save()
        # partie vehicule
        matricule = request.POST['Matricule']
        marque = request.POST['Marque']
        type_vh = request.POST['type_vh']
        puissance = int(request.POST['puissance'])
        vehicule = Vehicule(proprietaire=proprietaire, matricule=matricule,
                            marque=marque, type=type_vh, puissance_fiscale=puissance)
        vehicule.save()
        # partie Facture
        Narsa = int(request.POST['Narsa'])
        taxe_fiscale = int(request.POST['taxe_fiscale'])
        taxe_communale = int(request.POST['taxe_communale'])
        paiment = request.POST['paiment']
        montant_net = int(request.POST['montant_net'])
        resultat = request.POST['resultat']
        # Narsa = 0
        # taxe_communale = 0
        # if resultat == 'favorable':
        #     Narsa = 30
        #     taxe_communale = 50
        numero = request.POST['numero']
        montant_total = Narsa+taxe_fiscale+taxe_communale+(6/5)*montant_net
        taxe_paiment = 0
        if paiment == 'Espèce':
            taxe_paiment = montant_total/400
        montant_total += taxe_paiment
        montant_total = round(float(montant_total), 2)
        facture = Facture(Narsa=Narsa, taxe_fiscale=taxe_fiscale, taxe_paiment=taxe_paiment, numero=numero,
                          taxe_communale=taxe_communale, paiment=paiment, montant_net=montant_net, montant_total=montant_total)
        facture.save()
        # visite
        date_visite = request.POST['date_visite']
        date_expiration = request.POST['date_expiration']
        type_visite = request.POST['type_visite']
        resultat = request.POST['resultat']
        observation = request.POST['observation']
        utilisateur = Users(Utilisateur_nom=nom, Utilisateur_prenom=prenom)
        utilisateur.save()
        visite = Visite(vehicule=vehicule, Users=utilisateur, facture=facture,
                        observation=observation, date_visite=date_visite, date_expiration=date_expiration, prix=montant_total, paiment=paiment, type=type_visite, resultat=resultat)
        visite.save()
        messages.success(request, 'Visite est enregistrée')
        return redirect('visite')


@login_required(login_url='/users/login')
def modifier(request, id):
    visite = Visite.objects.get(pk=id)
    context = {
        'values': visite,
    }
    if request.method == 'GET':
        return render(request, 'visite/modifier.html', context)
    if request.method == 'POST':
        proprietaire = visite.vehicule.proprietaire
        nom = request.POST['nom']
        proprietaire.nom = nom.capitalize()
        prenom = request.POST['prenom']
        proprietaire.prenom = prenom.capitalize()
        nom_c = nom+' '+prenom
        proprietaire.nom_c = nom_c.lower()
        Cin = request.POST['CIN']
        proprietaire.Cin = Cin
        ville = request.POST['VILLE']
        proprietaire.ville = ville
        proprietaire.quartier = request.POST['QUARTIER']
        proprietaire.Tele = request.POST['Tele']
        proprietaire.save()
        # partie vehicule
        vehicule = visite.vehicule
        matricule = request.POST['Matricule']
        vehicule.matricule = matricule
        marque = request.POST['Marque']
        vehicule.marque = marque
        type_vh = request.POST['type_vh']
        vehicule.type = type_vh
        puissance = int(request.POST['puissance'])
        vehicule.puissance_fiscale = puissance
        vehicule.save()
        # Facture
        facture = visite.facture
        # Narsa = request.POST['Narsa']
        facture.Narsa = int(request.POST['Narsa'])
        facture.taxe_fiscale = int(request.POST['taxe_fiscale'])
        facture.taxe_communale = int(request.POST['taxe_communale'])
        paiment = request.POST['paiment']
        numero = request.POST['numero']
        facture.paiment = paiment
        montant_net = request.POST['montant_net']
        montant_net = int(montant_net)
        facture.montant_net = montant_net
        facture.numero = numero
        montant_total = facture.Narsa+facture.taxe_fiscale + \
            facture.taxe_communale+(6/5)*montant_net
        facture.taxe_paiment = 0
        if paiment == 'Espèce':
            facture.taxe_paiment = montant_total/400
        montant_total = facture.Narsa+facture.taxe_paiment + \
            facture.taxe_fiscale+facture.taxe_communale+(6/5)*montant_net
        facture.montant_total = round(float(montant_total), 2)
        facture.save()
        # visite
        date_visite = request.POST['date_visite']
        visite.date_visite = date_visite
        date_expiration = request.POST['date_expiration']
        visite.date_expiration = date_expiration
        type_visite = request.POST['type_visite']
        visite.type = type_visite
        resultat = request.POST['resultat']
        visite.resultat = resultat
        print(resultat)
        visite.observation = request.POST['observation']
        utilisateur = Users(
            Utilisateur_nom=nom, Utilisateur_prenom=prenom)

        utilisateur.save()
        visite.prix = facture.montant_total
        visite.paiment = facture.paiment
        visite.save()
        messages.success(request, 'Visite est modifiée')
        return redirect('visite')


@login_required(login_url='/users/login')
def supprimer(request, id):
    visite = Visite.objects.get(pk=id)
    visite.delete()
    messages.success(request, 'Visite est supprimée')
    return redirect('visite')


# defVisvisite_category_summary(request):
#     todays_date = datetime.date.today()
#     six_months_ago = todays_date-datetime.timedelta(days=30*6)
#    visites =Visite.objects.filter(owner=request.user,
#                                       date__gte=six_months_ago, date__lte=todays_date)
#     finalrep = {}

#     def get_category(proVisvisite):
#         returnVisvisite.category
#     category_list = list(set(map(get_category,visites)))

#     def get_proVisvisite_category_amount(category):
#         amount = 0
#         filtered_by_category =visites.filter(category=category)

#         for item in filtered_by_category:
#             amount += item.amount
#         return amount

#     for x invisites:
#         for y in category_list:
#             finalrep[y] = get_proVisvisite_category_amount(y)

#     return JsonResponse({'proVisvisite_category_data': finalrep}, safe=False)
