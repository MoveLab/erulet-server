# -*- coding: iso-8859-1 -*-
from django.shortcuts import render, render_to_response, get_object_or_404
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth import authenticate, login
import gpxpy
import gpxpy.gpx
from django.http import HttpResponseRedirect
from django.core.context_processors import csrf
from django.core.urlresolvers import reverse
from appulet.models import *
from frontulet.forms import *
import zipfile, shutil
from django.conf import settings
from PIL import Image
import shutil
from rest_framework.authtoken.models import Token
import json
from django.http import HttpResponse
from django.forms.models import modelformset_factory
from django.db.models import Count
from django import forms
from django.utils.translation import ugettext as _


def show_landing_page(request):
    context = {}
    return render(request, 'frontulet/landing_page.html', context)


def show_privacy_policy(request):
    context = {}
    return render(request, 'frontulet/privacy.html', context)


def show_home(request):
    context = {}
    return render(request, 'frontulet/home.html', context)


def show_about(request, mob=''):
    context = {}
    context['title'] = "Eth Holet"
    context['line1'] = _(u"Aquesta aplicació per dispositius mòbils ha estat desenvolupada en el marc del projecte")
    context['line2'] = _(u"Coordinació i disseny de continguts:")
    context['line3'] = _(u"LOOP<br>una unitat mixta")
    context['line4'] = _(u"Disseny tècnic:")
    context['line5'] = _(u"Organitza:")
    context['line6'] = _(u"Financia:")
    context['line7'] = _(u"Han col·laborat:")
    context['line8'] = _(u"Lluís Camarero, Agustí Escobar, John Palmer, Jordi Catalan, Frederic Bartumeus, Roser Faure, Enric Ballesteros, Guillermo de Mendoza, Claudio Aventin - Aran Culturau, Ferran Cardeñes")
    return render(request, 'frontulet/about' + mob + '.html', context)


def show_before_leaving(request, mob=''):
    context = {}
    context['gps_title'] = _(u"NAVEGACIÓ AMB GPS")
    context['gps_text'] = _(u"<p>Els sistema de guia per GPS és una ajuda a la navegació. En condicions òptimes, ens pot conduir pels itineraris amb molta precisió. Però hi ha molts factors (com ara el relleu del terreny, obstacles o núvols que distorsionin la senyal del satèl·lit, o la sensibilitat del nostre propi dispositiu) que poden afectar la precisió. Per això és important prestar també atenció a les indicacions escrites en els punts de ruta i procurar estimar en tot moment la nostra posició a partir de la interpretació del mapa, com a maneres de confirmar el posicionament GPS. L'aplicació ens mostra la nostra posició envoltada per un cercle blau que representa la precisió de la localització, que pot ser variable. Cal que tinguem en compte que la nostra posició real pot estar en qualsevol punt dintre d'aquest cercle.</p><p>Cal que tingueu activada en el vostre dispositiu l'opció de localització per GPS.</p><p>El consum de bateria pel sistema GPS és alt, cal portar la bateria carregada al 100% quan comencem l'itinerari. Per estalviar al màxim la bateria és recomanable portar el dispositiu en modus d'espera durant l'itinerari, però en un lloc on poguem sentir el senyal acústic i la vibració d'avís quan arribem a algun punt d'interés.</p>")
    context['safety_title'] = _(u"SEGURETAT")
    context['safety_text'] = _(u"<p>En els itineraris a peu, especialment aquells en zona d'alta muntanya:</p><ul><li>Abans de triar un itinerari, valorem la dificultat i les nostres capacitats i experiència.</li><li>Cal portar calçat adequat.</li><li>Encara que al sortir el temps sigui bò, és recomanable portar a la motxilla alguna peça d'abric i un impermeable en previsió d'un canvi de temps sobtat o haver d'abrigar a algú que hagi sofert un accident.</li><li>Cal beure suficient durant la caminada per mantenir una bona hidratació, i protegir-se del sòl amb barret, ulleres i crema protectora.</li><li>En els itineraris en cotxe: Alguna de les persones que no condueixen és qui ha de manipular i mirar el dispositiu mòbil, per evitar distraccions de qui condueix.</li></ul><p>En cas d'accident, cal seguir el protocol PAS - Protegir, Avisar, Socórrer</p><ul><li>PROTEGIR a qui ha patit l'accident i a nosaltres, per evitar empitjorar les consequències</li><li>AVISAR als serveis de socors: trucar al 112 (general) o al 973 640 080 (Pompièrs Val d'Aran). Tingueu en compte que en moltes zones d'alta muntanya no hi ha cobertura. Per això és convenient recordar quin és l'ultim lloc on n'hem trobat.</li><li>SOCÓRRER a les persones ferides, en la mesura dels nostres coneixements de primers auxilis i si tenim la seguretat de no agravar la situació.</li></ul>")
    context['environment_title'] = _(u"RESPECTE PEL MEDI")
    context['environment_text'] = _(u"<p>L'augment de la freqüentació del medi natural ha fet que fins i tot activitats aparentment inocues tinguin efectes negatius. Per això és molt important tenir un comportament respectuós amb el medi i extremar les precaucions per no alterar-ho. La regla general és que no deixem cap rastre del nostre pas. Els principals impactes que s'han detectat i algunes maneres d'evitar-los són:</p><p>Erosió i compactació del terreny pel trepig - Evitem caminar per fora dels senders marcats i agafar dreceres. En els corriols estrets i en pendent, com a norma de cortesia, qui baixa cedeix el pas a qui puja.</p><p>Molèsties a la fauna, en especial a les espècies protegides, tant als individus com al seu hàbitat - Evitem cridar i fer sorolls excessius. Vigilem que el nostre gos no persegueixi ni ataqui la fauna salvatge. Respectem els seus hàbitats: per exemple, no movem rocs o troncs que els hi puguin servir de refugi, no tirem pedres als rius i estanys, ni posem obstacles al flux d'aigua als rius. Recordeu que el bany i els esports aqüàtics no són permesos als estanys.</p><p>Recol·lecció d'espècies botàniques, en especial les protegides - Evitem arrencar flors i plantes. Respectem les regulacions en la recollida d'espècies comestibles, com bolets i altres. No recol·lectem fruits i baies amb mètodes agressius per les plantes.</p><p>Generació de residus - No deixem cap tipus de deixalles al medi, fins i tot les que poden servir d'aliment per a la fauna salvatge: no formen part de la seva dieta natural i els fan canviar els seus hàbits alimenticis i de comportament.</p><p>Incendis forestals - Si hem de fer foc, fem-ho només als llocs expressament acondicionats, i vigilem-lo. No llencem puntes de cigarreta, ni enceses ni apagades.</p>")

    if request.LANGUAGE_CODE == 'ca':
        return render(request, 'frontulet/before_leaving' + mob + '_ca.html', context)
    # TODO add other languages
    else:
        return render(request, 'frontulet/before_leaving' + mob + '_ca.html', context)


def show_manual(request, mob=''):
    context = {}
    context['main_page_title'] = _(u"PANTALLA PRINCIPAL:")
    context['main_page_text'] = _(u"<p>Permet accedir a informació general de l'app i a la pantalla de selecció d'itineraris.</p><p>El botó de menú secundari permet fixar les preferències (l'idioma i l'interval de temps entre posicionaments GPS consecutius) i registrar-se com a usuari (opcional).</p>")
    context['select_itineraries_title'] = _(u"SELECCIÓ D'ITINERARIS:")
    context['select_itineraries_text'] = _(u"<p>Desplega el mapa general amb tots els itineraris disponibles.</p><p>Clicant sobre cadascun dels itineraris es desplega una descripció general de l'itinerari.</p><p>Fent clic a sobre de la descripció entrem dintre de l'itinerari, amb dues opcions:</p><ul><li>VISUALITZAR la ruta (ens permet fer un recorregut virtual de la ruta)</li><li>RECÓRRER la ruta (activa el sistema de guia de la ruta, enregistra el recorregut i ens permet afegir informació pròpia a l'itinerari).</li></ul><p>El botó de menú secundari permet editar els nostres itineraris i fer la valoració dels itineraris compartits.</p>")
    context['my_itineraries_title'] = _(u"ELS MEUS ITINERARIES")
    context['my_itineraries_text'] = _(u"<ul class='no_bullet'><li class='image_bullet edit'>Obre la pantalla d'edició de l'itinerari.</li><li class='image_bullet upload'>Envia el nostre itinerari al núvol.</li><li class='image_bullet delete'>Esborra l'itinerari</li></ul>")
    context['itineraries_title'] = _(u"ITINERARIS:")
    context['itineraries_text'] = _(u"<p>Sobre els mapes dels itineraris poden aparèixer tres tipus d'icones:</p><ul class='no_bullet'><li class='image_bullet_tall waypoint'>Punt de ruta. Clicant a sobre obtenim informació de com arribar des d'aquí al següent punt de ruta.</li><li class='image_bullet_tall poi'>Punt d'interés. Clicant a sobre es desplega informació sobre algun tema d'interés relacionat amb el lloc on ens trobem.</li><li class='image_bullet_tall holet_alert'>Avís. Clicant a sobre obtenim avisos sobre temes de seguretat o afectacions al medi ambient en el lloc on ens trobem.</li></ul><p>Durant el recorregut el vibrador i un senyal acústic del dispositiu ens avisaran que estem arribant a algun d'aquests punts.</p>")
    context['buttons_title'] = _(u"BOTONS DE CONTROL:")
    context['buttons_text'] = _(u"<p>Dintre dels itineraris (virtuals o reals) tenim botons que ens permeten fer accions.</p><ul class='no_bullet'><li class='image_bullet stop'>Final del recorregut. Surt de l'itinerari i ens dóna l'opció de desar el recorregut i la informació que hem introduit.</li><li class='image_bullet add_info'>Afegir informació. Permet a l'usuari afegir informació (comentaris, fotos i vídeos) amb la seva localització geogràfica.</li><li class='image_bullet compass'>Brúixola. Obre la utilitat de brúixola, amb una fletxa que indica la direcció on es troba el següent waypoint.</li><li class='image_bullet where'>Posició actual. Mostra al mapa la nostra posició.</li></ul>")
    if request.LANGUAGE_CODE == 'ca':
        return render(request, 'frontulet/manual' + mob + '_ca.html', context)
    # TODO add other languages
    else:
        return render(request, 'frontulet/manual' + mob + '_ca.html', context)


def show_map(request):
    route_list = list()
    for route in Route.objects.all():
        these_track_steps = filter(lambda step: step.order is not None, route.track.steps.all().order_by('order'))
        these_highlight_steps = filter(lambda step: step.order is None, route.track.steps.all())
        these_highlights = map(lambda highlight: {'route_name': highlight.step.track.route.get_name(request.LANGUAGE_CODE), 'route_id': highlight.step.track.route.id, 'highlight_id': highlight.id, 'latitude': highlight.step.latitude, 'longitude': highlight.step.longitude, 'name': highlight.get_name(request.LANGUAGE_CODE), 'long_text': highlight.get_long_text(request.LANGUAGE_CODE), 'type': highlight.type}, [hl for hl in Highlight.objects.filter(step__in=these_highlight_steps).order_by('order')])
        route_list.append({'track_steps': these_track_steps, 'highlights': these_highlights, 'name': route.get_name(request.LANGUAGE_CODE), 'description': route.get_description(request.LANGUAGE_CODE), 'route_id': str(route.id)})
    context = {'routes': Route.objects.all(), 'route_list': route_list}
    return render(request, 'frontulet/map.html', context)


def show_route_list(request, whose=''):
    if request.user.is_authenticated():
        if whose == 'mine':
            routes = Route.objects.filter(created_by=request.user)
            title = _('My Routes')
        elif whose == 'others':
            routes = Route.objects.exclude(created_by=request.user)
            title = _("Other Hikers' Routes")
        elif whose == 'official':
            routes = Route.objects.filter(official=True)
            title = _("Holet's Routes")
        else:
            routes = Route.objects.all()
            title = _("All Routes")
    else:
        if whose == 'official':
            routes = Route.objects.filter(official=True)
            title = _("Holet's Routes")
        else:
            routes = Route.objects.all()
            title = _("All Routes")
    routes_localized = map(lambda route: {'name': route.get_name(request.LANGUAGE_CODE), 'short_description': route.get_short_description(request.LANGUAGE_CODE), 'id': route.id}, [r for r in routes])
    context = {'routes': routes_localized, 'title': title}
    return render(request, 'frontulet/route_list.html', context)


def show_route_detail(request, id):
    context = {'name': _('No Route'), 'short_description': '', 'description': _('There is no route with the id number you requested. Try requesting a different id.')}
    this_id = int(id)
    if Route.objects.filter(pk=this_id):
        this_route = Route.objects.get(pk=this_id)
        has_reference = this_route.reference is not None
        reference_html = ''
        if has_reference:
            reference_html_raw = this_route.reference.get_reference_html(request.LANGUAGE_CODE)
            reference_html = reference_html_raw.replace('src="', 'src="'+this_route.reference.reference_url_base+'/').replace('../general_references', '/media/holet/references/general_references')
        owner = request.user == this_route.created_by
        these_steps = this_route.track.steps.all().order_by('order')
        these_highlights_localized = map(lambda h: {'id': h.id, 'name': h.get_name(request.LANGUAGE_CODE), 'long_text': h.get_long_text(request.LANGUAGE_CODE), 'media': h.media, 'image': h.image, 'video': h.video, 'media_ext': h.media_ext, 'radius': h.radius, 'type': h.type, 'step': h.step, 'order': h.order, 'references': map(lambda r: {'id': r.id, 'name': r.get_name(request.LANGUAGE_CODE), 'html': r.get_reference_html(request.LANGUAGE_CODE).replace('src="', 'src="'+r.reference_url_base+'/').replace('../general_references', '/media/holet/references/general_references').split('</head>')[-1].split('</html>')[0]}, [ref for ref in h.references.all()]), 'interactive_images': [ii for ii in h.interactive_images.all()]}, [hl for hl in Highlight.objects.filter(step__in=these_steps).order_by('type', 'order')])
        context = {'owner': owner, 'name': this_route.get_name(request.LANGUAGE_CODE), 'short_description': this_route.get_short_description(request.LANGUAGE_CODE), 'description': this_route.get_description(request.LANGUAGE_CODE), 'has_reference': has_reference, 'reference_html': reference_html, 'steps': these_steps, 'these_highlights': these_highlights_localized, 'id': this_id}
    return render(request, 'frontulet/route_detail.html', context)


def show_profile(request):
    this_user = request.user
    these_routes = Route.objects.filter(created_by=this_user)
    n_routes = these_routes.count()
    n_pois = Highlight.objects.filter(created_by=this_user).count()
    context = {'user_name': this_user.username, 'first_name': this_user.first_name, 'last_name': this_user.last_name, 'email': this_user.email, 'n_routes': n_routes, 'n_pois': n_pois}
    return render(request, 'frontulet/user_profile.html', context)


def show_profile_mob(request, token, username):
    this_user = request.user
    these_routes = Route.objects.filter(created_by=this_user)
    n_routes = these_routes.count()
    n_pois = Highlight.objects.filter(created_by=this_user).count()
    context = {'user_name': this_user.username, 'first_name': this_user.first_name, 'last_name': this_user.last_name, 'email': this_user.email, 'n_routes': n_routes, 'n_pois': n_pois}
    return render(request, 'frontulet/user_profile.html', context)


class RegistrationView(FormView):
    template_name = 'registration/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('show_profile')

    def form_valid(self, form):
        new_user = form.save()
        request = self.request
        user = authenticate(username=request.POST['username'], password=request.POST['password1'])
        login(self.request, user)
        return HttpResponseRedirect(reverse('show_profile'))


class RegisterFromApp(FormView):
    template_name = 'registration/register_mob.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('show_profile')

    def form_valid(self, form):
        new_user = form.save()
        token = Token.objects.create(user=new_user)
        request = self.request
        user = authenticate(username=request.POST['username'], password=request.POST['password1'])
        login(self.request, user)
        return HttpResponseRedirect(reverse('show_profile_mob', kwargs={'token': token.key, 'username': new_user.username}))


def parse_gpx_track(this_route, this_track):

    if this_route.gpx_track:
        gpx_file = open(settings.MEDIA_ROOT + this_route.gpx_track.name)
        gpx = gpxpy.parse(gpx_file)

        for step in Step.objects.filter(track=this_track):
            step.delete()

        this_track.name_oc = this_route.name_oc
        this_track.name_es = this_route.name_es
        this_track.name_ca = this_route.name_ca
        this_track.name_fr = this_route.name_fr
        this_track.name_en = this_route.name_en

        if gpx.tracks:
            for track in gpx.tracks:
                if track.segments:
                    for segment in track.segments:
                        if segment.points:
                            this_order_number = 1
                            for point in segment.points:
                                new_step = Step()
                                new_step.track = this_track
                                new_step.latitude = point.latitude
                                new_step.longitude = point.longitude
                                new_step.order = this_order_number
                                new_step.save()
                                this_order_number += 1


def parse_gpx_waypoints(lang, this_user, this_route, this_track):

    if this_route.gpx_waypoints:

        gpx_file = open(settings.MEDIA_ROOT + this_route.gpx_waypoints.name)
        gpx = gpxpy.parse(gpx_file)

        if gpx.waypoints:
            this_order_number = 1
            for waypoint in gpx.waypoints:
                new_step = Step()
                new_step.latitude = waypoint.latitude
                new_step.longitude = waypoint.longitude
                new_step.altitude = waypoint.elevation
                new_step.track = this_track
                new_step.save()

                new_highlight = Highlight()
                new_highlight.created_by = this_user
                new_highlight.type = 1
                new_highlight.name_oc = waypoint.name
                new_highlight.name_es = waypoint.name
                new_highlight.name_ca = waypoint.name
                new_highlight.name_fr = waypoint.name
                new_highlight.name_en = waypoint.name
                new_highlight.step = new_step
                new_highlight.order = this_order_number
                new_highlight.save()
                this_order_number += 1


def parse_gpx_pois(lang, this_user, this_route, this_track):

    if this_route.gpx_pois:
        gpx_file = open(settings.MEDIA_ROOT + this_route.gpx_pois.name)
        gpx = gpxpy.parse(gpx_file)

        if gpx.waypoints:
            this_order_number = 1
            for waypoint in gpx.waypoints:
                new_step = Step()
                new_step.latitude = waypoint.latitude
                new_step.longitude = waypoint.longitude
                new_step.altitude = waypoint.elevation
                new_step.track = this_track
                new_step.save()

                new_highlight = Highlight()
                new_highlight.created_by = this_user
                new_highlight.type = 0
                new_highlight.name_oc = waypoint.name
                new_highlight.name_es = waypoint.name
                new_highlight.name_ca = waypoint.name
                new_highlight.name_fr = waypoint.name
                new_highlight.name_en = waypoint.name
                new_highlight.step = new_step
                new_highlight.order = this_order_number
                new_highlight.save()
                this_order_number += 1


def make_new_route(request):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))

        if request.method == 'POST':
            this_route = Route()
            this_route.created_by = request.user
            this_track = Track()
            this_track.save()
            this_route.track = this_track
            this_route.save()
            if 'scientists' in [group.name for group in request.user.groups.all()]:
                form = OfficialRouteForm(request.POST, request.FILES, instance=this_route)
            else:
                form = RouteForm(request.POST, request.FILES, instance=this_route)
            args['form'] = form
            if form.is_valid():
                form.save()
                parse_gpx_track(this_route, this_track)
                parse_gpx_waypoints(request.LANGUAGE_CODE, request.user, this_route, this_track)
                parse_gpx_pois(request.LANGUAGE_CODE, request.user, this_route, this_track)

                return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(this_route.id)}))

        else:
            if 'scientists' in [group.name for group in request.user.groups.all()]:
                args['form'] = OfficialRouteForm()
            else:
                args['form'] = RouteForm()

        return render(request, 'frontulet/create_route.html', args)

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_route(request, id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_route = Route.objects.get(pk=id)
        if this_route.created_by == request.user:
            if request.method == 'POST':
                if 'scientists' in [group.name for group in request.user.groups.all()]:
                    form = EditOfficialRouteForm(request.POST, instance=this_route)
                else:
                    form = EditRouteForm(request.POST, instance=this_route)
                    args['form'] = form
                if form.is_valid():
                    form.save()

                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(this_route.id)}))

            else:
                if 'scientists' in [group.name for group in request.user.groups.all()]:
                    args['form'] = EditOfficialRouteForm(instance=this_route)
                else:
                    args['form'] = EditRouteForm(instance=this_route)

                return render(request, 'frontulet/edit_route.html', args)

        else:
            return render(request, 'registration/no_permission_not_yours.html')

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_highlight(request, route_id, highlight_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_highlight = Highlight.objects.get(pk=highlight_id)
        if this_highlight.created_by == request.user:
            if request.method == 'POST':
                form = HighlightForm(request.POST, request.FILES, instance=this_highlight)
                args['form'] = form
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}) + "#h" + str(highlight_id))
                else:
                    args['error_message'] = _('Wrong file type: Make sure the file you have selected is either a JPG, PNG, GIF, MP4, WEBM, or OGG.')
                    return render(request, 'frontulet/upload_error.html', args)

            else:
                args['form'] = HighlightForm(instance=this_highlight)

                return render(request, 'frontulet/edit_highlight.html', args)

        else:
            return render(request, 'registration/no_permission_not_yours.html')

    else:
        return render(request, 'registration/no_permission_must_login.html')


def translate_highlights(request, lang='all', scroll_position=''):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        args['scroll_position'] = scroll_position
        if 'translators' in [group.name for group in request.user.groups.all()]:

            # first check highlights to see if already in HighlightTranslationVCS. If not, put current values there as baseline
            new_highlights = Highlight.objects.annotate(highlight_translation_vcs_entry_count=Count('highlight_translation_vcs_entries')).filter(highlight_translation_vcs_entry_count=0)
            for highlight in new_highlights:
                vcs_entry = HighlightTranslationVCS()
                vcs_entry.highlight = highlight
                vcs_entry.user = highlight.created_by
                vcs_entry.name_ca = highlight.name_ca
                vcs_entry.name_oc = highlight.name_oc
                vcs_entry.name_es = highlight.name_es
                vcs_entry.name_fr = highlight.name_fr
                vcs_entry.name_en = highlight.name_en
                vcs_entry.long_text_ca = highlight.long_text_ca
                vcs_entry.long_text_oc = highlight.long_text_oc
                vcs_entry.long_text_es = highlight.long_text_es
                vcs_entry.long_text_fr = highlight.long_text_fr
                vcs_entry.long_text_en = highlight.long_text_en
                vcs_entry.save()
            # now set up formset
            if lang == 'spain':
                fields = ('name_ca', 'name_oc', 'name_es', 'long_text_ca', 'long_text_oc', 'long_text_es')
            elif lang == 'all':
                fields = ('name_ca', 'name_oc', 'name_es', 'name_fr', 'name_en', 'long_text_ca', 'long_text_oc', 'long_text_es', 'long_text_fr', 'long_text_en')
            elif lang == 'oc':
                fields = ('name_ca', 'name_oc', 'long_text_ca', 'long_text_oc')
            elif lang == 'es':
                fields = ('name_ca', 'name_es', 'long_text_ca', 'long_text_es')
            elif lang == 'fr':
                fields = ('name_ca', 'name_fr', 'long_text_ca', 'long_text_fr')
            elif lang == 'en':
                fields = ('name_ca', 'name_en', 'long_text_ca', 'long_text_en')
            else:
                fields = ('name_ca', 'name_oc', 'name_es', 'name_fr', 'name_en', 'long_text_ca', 'long_text_oc', 'long_text_es', 'long_text_fr', 'long_text_en')

            widgets = {'name_ca': forms.TextInput(attrs={'class': 'form-control blue-back'}), 'name_oc': forms.TextInput(attrs={'class': 'form-control'}), 'name_es': forms.TextInput(attrs={'class': 'form-control'}), 'name_fr': forms.TextInput(attrs={'class': 'form-control'}), 'name_en': forms.TextInput(attrs={'class': 'form-control'}), 'long_text_ca': forms.Textarea(attrs={'rows': 3, 'class': 'form-control blue-back'}), 'long_text_oc': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 'long_text_es': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 'long_text_fr': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 'long_text_en': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})}

            TranslateHighlightFormSet = modelformset_factory(Highlight, extra=0, fields=fields, widgets=widgets)
            if request.method == 'POST':
                scroll_position = request.POST.get("scroll_position", '0')
                formset = TranslateHighlightFormSet(request.POST)
                if formset.is_valid():
                    translated_highlights = formset.save()
                    # now put everything that changed into the vcs
                    for th in translated_highlights:
                        new_vcs_entry = HighlightTranslationVCS()
                        new_vcs_entry.highlight = th
                        new_vcs_entry.user = request.user
                        new_vcs_entry.name_ca = th.name_ca
                        new_vcs_entry.name_oc = th.name_oc
                        new_vcs_entry.name_es = th.name_es
                        new_vcs_entry.name_fr = th.name_fr
                        new_vcs_entry.name_en = th.name_en
                        new_vcs_entry.long_text_ca = th.long_text_ca
                        new_vcs_entry.long_text_oc = th.long_text_oc
                        new_vcs_entry.long_text_es = th.long_text_es
                        new_vcs_entry.long_text_fr = th.long_text_fr
                        new_vcs_entry.long_text_en = th.long_text_en
                        new_vcs_entry.save()

                    return HttpResponseRedirect(reverse('translate_highlights_scroll_position', kwargs={'lang': lang, 'scroll_position': scroll_position}))
            else:
                args['formset'] = TranslateHighlightFormSet(queryset=Highlight.objects.filter(step__track__route__official=True))
                args['title'] = _('Holet Highlight Translation')
            return render(request, 'frontulet/formset_base.html', args)
        else:
            return render(request, 'registration/no_permission_must_be _translator.html')
    else:
        return render(request, 'registration/no_permission_must_login.html')


def translate_routes(request, lang='all', scroll_position=''):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        args['scroll_position'] = scroll_position
        if 'translators' in [group.name for group in request.user.groups.all()]:

            # first check highlights to see if already in HighlightTranslationVCS. If not, put current values there as baseline
            new_routes = Route.objects.annotate(route_translation_vcs_entry_count=Count('route_translation_vcs_entries')).filter(route_translation_vcs_entry_count=0)
            for route in new_routes:
                vcs_entry = RouteTranslationVCS()
                vcs_entry.route = route
                vcs_entry.user = route.created_by
                vcs_entry.name_ca = route.name_ca
                vcs_entry.name_oc = route.name_oc
                vcs_entry.name_es = route.name_es
                vcs_entry.name_fr = route.name_fr
                vcs_entry.name_en = route.name_en
                vcs_entry.description_ca = route.description_ca
                vcs_entry.description_oc = route.description_oc
                vcs_entry.description_es = route.description_es
                vcs_entry.description_fr = route.description_fr
                vcs_entry.description_en = route.description_en
                vcs_entry.short_description_ca = route.short_description_ca
                vcs_entry.short_description_oc = route.short_description_oc
                vcs_entry.short_description_es = route.short_description_es
                vcs_entry.short_description_fr = route.short_description_fr
                vcs_entry.short_description_en = route.short_description_en
                vcs_entry.save()
            # now set up formset
            if lang == 'spain':
                fields = ('name_ca', 'name_oc', 'name_es', 'short_description_ca', 'short_description_oc', 'short_description_es', 'description_ca', 'description_oc', 'description_es')
            elif lang == 'all':
                fields = ('name_ca', 'name_oc', 'name_es', 'name_fr', 'name_en', 'short_description_ca', 'short_description_oc', 'short_description_es', 'short_description_fr', 'short_description_en', 'description_ca', 'description_oc', 'description_es', 'description_fr', 'description_en')
            elif lang == 'oc':
                fields = ('name_ca', 'name_oc', 'short_description_ca', 'short_description_oc', 'description_ca', 'description_oc')
            elif lang == 'es':
                fields = ('name_ca', 'name_es', 'short_description_ca', 'short_description_es', 'description_ca', 'description_es')
            elif lang == 'fr':
                fields = ('name_ca', 'name_fr', 'short_description_ca', 'short_description_fr', 'description_ca', 'description_fr')
            elif lang == 'en':
                fields = ('name_ca', 'name_en', 'short_description_ca', 'short_description_en', 'description_ca', 'description_en')
            else:
                fields = ('name_ca', 'name_oc', 'name_es', 'name_fr', 'name_en', 'short_description_ca', 'short_description_oc', 'short_description_es', 'short_description_fr', 'short_description_en', 'description_ca', 'description_oc', 'description_es', 'description_fr', 'description_en')

            widgets = {'name_ca': forms.TextInput(attrs={'class': 'form-control blue-back'}), 'name_oc': forms.TextInput(attrs={'class': 'form-control'}), 'name_es': forms.TextInput(attrs={'class': 'form-control'}), 'name_fr': forms.TextInput(attrs={'class': 'form-control'}), 'name_en': forms.TextInput(attrs={'class': 'form-control'}), 'short_description_ca': forms.Textarea(attrs={'rows': 3, 'class': 'form-control blue-back'}), 'short_description_oc': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 'short_description_es': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 'short_description_fr': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 'short_description_en': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), 'description_ca': forms.Textarea(attrs={'rows': 5, 'class': 'form-control blue-back'}), 'description_oc': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}), 'description_es': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}), 'description_fr': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'}), 'description_en': forms.Textarea(attrs={'rows': 5, 'class': 'form-control'})}

            TranslateRouteFormSet = modelformset_factory(Route, extra=0, fields=fields, widgets=widgets)
            if request.method == 'POST':
                scroll_position = request.POST.get("scroll_position", '0')
                formset = TranslateRouteFormSet(request.POST)
                if formset.is_valid():
                    translated_routes = formset.save()
                    # now put everything that changed into the vcs
                    for tr in translated_routes:
                        new_vcs_entry = RouteTranslationVCS()
                        new_vcs_entry.route = tr
                        new_vcs_entry.user = request.user
                        new_vcs_entry.name_ca = tr.name_ca
                        new_vcs_entry.name_oc = tr.name_oc
                        new_vcs_entry.name_es = tr.name_es
                        new_vcs_entry.name_fr = tr.name_fr
                        new_vcs_entry.name_en = tr.name_en
                        new_vcs_entry.description_ca = tr.description_ca
                        new_vcs_entry.description_oc = tr.description_oc
                        new_vcs_entry.description_es = tr.description_es
                        new_vcs_entry.description_fr = tr.description_fr
                        new_vcs_entry.description_en = tr.description_en
                        new_vcs_entry.short_description_ca = tr.short_description_ca
                        new_vcs_entry.short_description_oc = tr.short_description_oc
                        new_vcs_entry.short_description_es = tr.short_description_es
                        new_vcs_entry.short_description_fr = tr.short_description_fr
                        new_vcs_entry.short_description_en = tr.short_description_en
                        new_vcs_entry.save()

                    return HttpResponseRedirect(reverse('translate_routes_scroll_position', kwargs={'lang': lang, 'scroll_position': scroll_position}))
            else:
                args['formset'] = TranslateRouteFormSet(queryset=Route.objects.filter(official=True))
                args['title'] = _('Holet Route Translation')
            return render(request, 'frontulet/formset_base.html', args)
        else:
            return render(request, 'registration/no_permission_must_be _translator.html')
    else:
        return render(request, 'registration/no_permission_must_login.html')


def add_css(this_reference):
    this_path = os.path.dirname(this_reference.html_file.path)
    new_css_file = open(os.path.join(this_path, 'erholet-ref-style.css'), 'w')
    new_css_file.write('body{width:94%}img {width:100%; margin-bottom:5px}')
    new_css_file.close()


def set_up_reference(reference):
    uploaded_file_name_split = reference.html_file.name.split('.')
    ext = uploaded_file_name_split[-1]
    this_dir = os.path.dirname(reference.html_file.path)
    if ext == 'zip':
        this_file = zipfile.ZipFile(reference.html_file.path)
        file_names = this_file.namelist()
        allowed_extensions = ['jpg', 'png', 'gif', 'mp4', 'css', 'html']
        html_file_paths = []
        for name in file_names:
            if name[:3] == '../':
                return _('At least one of the files in your ZIP archive has a path starting with "../". Please do not try to give files in the archives paths that point outside of the archived folder.')
            elif os.path.isabs(name):
                return _('At least one of the files in your ZIP archive has an absolute path. Please do not try to give files in the archives paths that point outside of the archived folder.')
            name_split = name.split('.')
            this_extension = name_split[-1]
            if this_extension == 'html':
                lang_code = name_split[0].split('-')[-1][:2]
                if lang_code not in ['to'] + map(lambda x: x[0].upper(), settings.LANGUAGES) + map(lambda x: x[0].lower(), settings.LANGUAGES):
                    reference.delete()
                    return _('At least one HTML file in your ZIP archive was missing a supported language code. Please make sure each HTML has a file name that ends in either -oc.html, -es,html, -ca.html, -fr.html, -en.html, or -to.html.')
                else:
                    html_file_paths.append((lang_code.lower(), os.path.join(this_dir, name)))
            elif this_extension.lower() not in allowed_extensions:
                reference.delete()
                return _('You tried to upload a zip file containing a file or files that are not HTML, CSS, JPG, PNG, GIF, or MP4. Please make sure the ZIP archive contains only those file type.')
        if len(html_file_paths) > 5:
            reference.delete()
            return _('There are more than five HTML files in this ZIP archive. Please include no more than one HTML file for each of the five supported languages (Aranese, Spanish, Catalan, French, and English).')
        elif len(html_file_paths) == 0:
            reference.delete()
            return _('There is no HTML file in this ZIP archive. Please include at least one HTML file.')
        else:
            this_file.extractall(path=this_dir)
            # if it is a general reference, then extract also to general references folder
            if reference.general:
                general_reference_path = os.path.join(os.path.dirname(this_dir), 'general_references')
                this_file.extractall(path=general_reference_path)
            for html_path in html_file_paths:
                with codecs.open(html_path[1], 'r', 'iso-8859-1') as f:
                    this_html_original = f.read()
                    this_html_final = this_html_original.replace('href="IT', 'href="../general_references/IT')
                    if html_path[0] == 'to':
                        for lc in map(lambda x: x[0].lower(), settings.LANGUAGES):
                            new_file = codecs.open(os.path.join(this_dir, 'reference_' + lc + '.html'), 'w+', 'iso-8859-1')
                            new_file.write(this_html_final)
                            new_file.close()
                    else:
                        new_file = codecs.open(os.path.join(this_dir, 'reference_' + html_path[0] + '.html'), 'w+', 'iso-8859-1')
                        new_file.write(this_html_final)
                        new_file.close()
                    f.close()
                    # delete original file
                    os.remove(html_path[1])
            these_extensions = [name.split('.')[-1] for name in file_names]
            if 'css' not in these_extensions:
                add_css(reference)
            return 'OK'
    elif ext == 'html':
        add_css(reference)
        lang_code = uploaded_file_name_split[0].split('_')[-1]
        shutil.copyfile(reference.html_file.path, os.path.join(this_dir, 'reference_' + lang_code + '.html'))
        return 'OK'
    else:
        reference.delete()
        return _('You tried to upload something other than a ZIP or HTML file. Please check the file and try again.')


def make_new_route_reference(request, route_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))

        if request.method == 'POST':
            this_reference = Reference()
            this_reference.save()
            this_route = Route.objects.get(pk=route_id)
            this_route.reference = this_reference
            this_route.save()
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
        else:
            args['form'] = ReferenceForm()

        return render(request, 'frontulet/create_reference.html', args)

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_route_reference(request, route_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_route = Route.objects.get(pk=route_id)
        this_reference = Reference.objects.get(pk=this_route.reference.id)
        if request.method == 'POST':
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
        else:
            args['form'] = ReferenceForm(instance=this_reference)
        return render(request, 'frontulet/edit_reference.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def make_new_highlight_reference(request, route_id, highlight_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))

        if request.method == 'POST':
            this_highlight = Highlight.objects.get(pk=highlight_id)
            this_reference = Reference()
            this_reference.highlight = this_highlight
            this_reference.save()
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}) + "#h" + str(highlight_id))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
            else:
                this_reference.delete()
        else:
            args['form'] = ReferenceForm()

        return render(request, 'frontulet/create_reference.html', args)

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_highlight_reference(request, route_id, reference_id):
    if request.user.is_authenticated():
        this_reference = Reference.objects.get(pk=reference_id)
        this_highlight = this_reference.highlight
        args = {}
        args.update(csrf(request))
        args['route_id'] = route_id
        args['highlight_id'] = this_highlight.id
        this_reference = Reference.objects.get(pk=reference_id)
        if request.method == 'POST':
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}) + "#h" + str(this_highlight.id))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
        else:
            args['form'] = ReferenceForm(instance=this_reference)
        return render(request, 'frontulet/edit_reference.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def delete_highlight_reference(request, route_id, reference_id):
    this_reference = Reference.objects.get(pk=reference_id)
    this_highlight = this_reference.highlight
    trees_to_delete = []
    if request.user.is_authenticated():
        if this_reference.highlight.created_by == request.user:
            if this_reference.html_file:
                trees_to_delete.append(os.path.dirname(this_reference.html_file.path))
            this_reference.delete()
            for this_tree in trees_to_delete:
                shutil.rmtree(this_tree)
    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}) + '#h' + str(this_highlight.id))


def delete_route_reference(request, route_id):
    this_route = Route.objects.get(id=route_id)
    this_reference = this_route.reference
    trees_to_delete = []
    if request.user.is_authenticated():
        if this_reference.route.created_by == request.user:
            if this_reference.html_file:
                trees_to_delete.append(os.path.dirname(this_reference.html_file.path))
            this_reference.delete()
            for this_tree in trees_to_delete:
                shutil.rmtree(this_tree)
    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': str(route_id)}))


def delete_route(request, route_id):
    this_route = Route.objects.get(id=route_id)
    this_track = this_route.track
    trees_to_delete = []
    files_to_delete = []
    if request.user.is_authenticated():
        if this_route.created_by == request.user:
            # remove all route reference files
            if this_route.reference:
                if this_route.reference.html_file:
                    trees_to_delete.append(os.path.dirname(this_route.reference.html_file.path))
            # remove all gpx files
            if this_route.gpx_track:
                files_to_delete.append(this_route.gpx_track.path)
            if this_route.gpx_waypoints:
                files_to_delete.append(this_route.gpx_waypoints.path)
            if this_route.gpx_pois:
                files_to_delete.append(this_route.gpx_pois.path)
            for step in Step.objects.filter(track=this_track):
                for highlight in step.highlights.all():
                    if highlight.media:
                        files_to_delete.append(highlight.media.path)
                    for reference in highlight.references.all():
                        # remove all highlight reference files
                        if reference.html_file:
                            trees_to_delete.append(os.path.dirname(reference.html_file.path))
                    for interactive_image in highlight.interactive_images.all():
                        # remove interactive image files
                        if interactive_image.image_file:
                            files_to_delete.append(interactive_image.image_file.path)
            # first delete the route from the database
            this_route.delete()
            # now delete all associated files
            for this_file in files_to_delete:
                os.remove(this_file)
            for this_tree in trees_to_delete:
                shutil.rmtree(this_tree)
    return HttpResponseRedirect(reverse('show_home'))


def edit_profile(request):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_user = request.user
        if request.method == 'POST':
            form = ProfileForm(request.POST, instance=this_user)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('show_profile'))

        else:
            args['form'] = ProfileForm(instance=this_user)

        return render(request, 'frontulet/edit_profile.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def create_ii(request, highlight_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_ii = InteractiveImage()
        this_highlight = Highlight.objects.get(id=highlight_id)
        this_ii.highlight = this_highlight
        if request.method == 'POST':
            this_ii.save()
            form = InteractiveImageForm(request.POST, request.FILES, instance=this_ii)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('create_ii_box', kwargs={'ii_id': this_ii.id}))
            else:
                args['form'] = InteractiveImageForm()
                this_ii.delete()
                return render(request, 'frontulet/wrong_file_type_ii.html', args)

        else:
            args['form'] = InteractiveImageForm(instance=this_ii)

        return render(request, 'frontulet/create_ii.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_ii(request, ii_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_ii = InteractiveImage.objects.get(id=ii_id)
        if request.method == 'POST':
            form = InteractiveImageForm(request.POST, instance=this_ii)
            if form.is_valid():
                form.save()
                # clear all boxes from old ii
                for box in this_ii.boxes.all():
                    box.delete()
                return HttpResponseRedirect(reverse('create_ii_box', kwargs={'ii_id': this_ii.id}))

        else:
            args['form'] = InteractiveImageForm(instance=this_ii)

        return render(request, 'frontulet/create_ii.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def create_ii_box(request, ii_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_ii = InteractiveImage.objects.get(id=ii_id)
        args['image_url'] = this_ii.image_file.url
        args['display_width'] = 600.00
        args['scaling_factor'] = args['display_width'] / this_ii.original_width
        args['display_height'] = this_ii.original_height * args['scaling_factor']
        args['original_height'] = this_ii.original_height
        args['original_width'] = this_ii.original_width
        args['route_id'] = this_ii.highlight.step.track.route.id
        args['highlight_id'] = this_ii.highlight.id
        args['editing'] = False
        args['ii_id'] = ii_id
        this_box = Box()
        this_box.interactive_image = this_ii
        if this_ii.boxes.count() > 0:
            args['boxes'] = map(lambda b: {'box': b, 'message': b.get_message(request.LANGUAGE_CODE).replace('"', "'"), 'all_messages': b.get_all_messages_html().replace('"', "'")}, [box for box in this_ii.boxes.all()])
        if request.method == 'POST':
            form = BoxForm(request.POST, instance=this_box)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('create_ii_box', kwargs={'ii_id': this_ii.id}))

        else:
            args['form'] = BoxForm(instance=this_box)

        return render(request, 'frontulet/create_ii_box.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_ii_box(request, ii_id, box_id):
    if request.user.is_authenticated():
        args = {}
        args.update(csrf(request))
        this_ii = InteractiveImage.objects.get(id=ii_id)
        args['image_url'] = this_ii.image_file.url
        args['display_width'] = 600.00
        args['scaling_factor'] = args['display_width'] / this_ii.original_width
        args['display_height'] = this_ii.original_height * args['scaling_factor']
        args['original_height'] = this_ii.original_height
        args['original_width'] = this_ii.original_width
        args['route_id'] = this_ii.highlight.step.track.route.id
        args['highlight_id'] = this_ii.highlight.id
        this_box = Box.objects.get(id=box_id)
        args['this_box'] = this_box
        args['editing'] = True
        args['ii_id'] = ii_id
        other_boxes = filter(lambda b: b != this_box, [box for box in this_ii.boxes.all()])
        if len(other_boxes) > 0:
            args['boxes'] = map(lambda b: {'box': b, 'message': b.get_message(request.LANGUAGE_CODE).replace('"', "'"), 'all_messages': b.get_all_messages_html().replace('"', "'")}, other_boxes)
        if request.method == 'POST':
            form = BoxForm(request.POST, instance=this_box)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('create_ii_box', kwargs={'ii_id': this_ii.id}))

        else:
            args['form'] = BoxForm(instance=this_box)

        return render(request, 'frontulet/create_ii_box.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def view_ii(request, ii_id):
    args = {}
    args.update(csrf(request))
    this_ii = InteractiveImage.objects.get(id=ii_id)
    if request.user == this_ii.highlight.created_by:
        args['owner'] = True
    else:
        args['owner'] = False
    args['ii_id'] = ii_id
    args['image_url'] = this_ii.image_file.url
    args['display_width'] = 600.00
    args['scaling_factor'] = args['display_width'] / this_ii.original_width
    args['display_height'] = this_ii.original_height * args['scaling_factor']
    args['original_height'] = this_ii.original_height
    args['original_width'] = this_ii.original_width
    args['route_id'] = this_ii.highlight.step.track.route.id
    args['highlight_id'] = this_ii.highlight.id
    if this_ii.boxes.count() > 0:
        args['boxes'] = map(lambda b: {'box': b, 'message': b.get_message(request.LANGUAGE_CODE).replace('"', "'")}, [box for box in this_ii.boxes.all()])
    return render(request, 'frontulet/view_ii.html', args)


def delete_ii(request, ii_id):
    args = {}
    args.update(csrf(request))
    this_ii = InteractiveImage.objects.get(id=ii_id)
    this_highlight_id = this_ii.highlight.id
    this_route_id = this_ii.highlight.step.track.route.id
    this_ii.delete()
    return HttpResponseRedirect(reverse('show_route_detail', kwargs={'id': this_route_id}) +"#h" + str(this_highlight_id) )


def show_general_references(request):
    scientist = 'scientists' in [group.name for group in request.user.groups.all()]
    these_references = map(lambda r: {'id': r.id, 'name': r.get_name(request.LANGUAGE_CODE), 'html': r.get_reference_html(request.LANGUAGE_CODE).replace('src="', 'src="'+r.reference_url_base+'/').split('</head>')[-1].split('</html>')[0]}, [ref for ref in Reference.objects.filter(general=True)])
    context = {'references': these_references, 'scientist': scientist}
    return render(request, 'frontulet/general_references.html', context)


def make_new_general_reference(request):
    if request.user.is_authenticated() and 'scientists' in [group.name for group in request.user.groups.all()]:
        args = {}
        args.update(csrf(request))
        if request.method == 'POST':
            this_reference = Reference()
            this_reference.general = True
            this_reference.save()
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_general_references'))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
        else:
            args['form'] = ReferenceForm()

        return render(request, 'frontulet/create_reference.html', args)

    else:
        return render(request, 'registration/no_permission_must_login.html')


def edit_general_reference(request, reference_id):
    if request.user.is_authenticated() and'scientists' in [group.name for group in request.user.groups.all()]:
        args = {}
        args.update(csrf(request))
        this_reference = Reference.objects.get(id=reference_id)
        if request.method == 'POST':
            form = ReferenceForm(request.POST, request.FILES, instance=this_reference)
            args['form'] = form
            if form.is_valid():
                form.save()
                setup_response = set_up_reference(this_reference)
                if setup_response == 'OK':
                    return HttpResponseRedirect(reverse('show_general_references'))
                else:
                    args['form'] = ReferenceForm()
                    args['error_message'] = setup_response
                    return render(request, 'frontulet/upload_error.html', args)
        else:
            args['form'] = ReferenceForm(instance=this_reference)
        return render(request, 'frontulet/edit_reference.html', args)
    else:
        return render(request, 'registration/no_permission_must_login.html')


def delete_general_reference(request, reference_id):
    this_reference = Reference.objects.get(id=reference_id)
    trees_to_delete = []
    if request.user.is_authenticated() and 'scientists' in [group.name for group in request.user.groups.all()]:
        if this_reference.html_file:
            trees_to_delete.append(os.path.dirname(this_reference.html_file.path))
        this_reference.delete()
        for this_tree in trees_to_delete:
            shutil.rmtree(this_tree, True)
        return HttpResponseRedirect(reverse('show_general_references'))
    else:
        return render(request, 'registration/no_permission_must_login.html')


def show_survey(request, mob, survey_name, route_id=None):
    args = {}
    args.update(csrf(request))
    lang = request.LANGUAGE_CODE
    this_scheme = get_object_or_404(SurveyScheme, unique_name=survey_name)
    this_route = None
    if route_id and Route.objects.filter(id=route_id).count() == 1:
        this_route = Route.objects.get(id=route_id)
    widgets = {'response': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})}
    extra = this_scheme.questions.all().count()
    survey_formset = modelformset_factory(SurveyResponse, fields=('response',), extra=extra, labels={'response': ''}, widgets=widgets)
    if request.method == 'POST':
        formset = survey_formset(request.POST)
        if formset.is_valid():
            this_instance = SurveyInstance(survey_scheme=this_scheme, route=this_route, language=lang)
            this_instance.save()
            for i in range(len(formset)):
                form = formset[i]
                form.instance.survey_instance = this_instance
                form.instance.question = this_scheme.questions.all()[i]
            formset.save()
            return HttpResponseRedirect(reverse('show_survey_submitted', kwargs={'response_code': "ok", 'mob': mob}))
        else:
            return HttpResponseRedirect(reverse('show_survey_submitted', kwargs={'response_code': "error", 'mob': mob}))

    else:
        initial = []
        for question in this_scheme.questions.all():
            initial.append({'question': question})
        formset = survey_formset(queryset=SurveyResponse.objects.none(), initial=initial)
        args['formset'] = formset
        args['lang'] = lang
    return render_to_response('frontulet/survey' + mob + '.html', args)


def show_survey_submitted(request, response_code, mob):
    if response_code == 'ok':
        message = _('Thank you!')
    else:
        message = _('Error')
    return render(request, 'frontulet/simple_message' + mob + '.html', {'message': message})