# ruff: noqa
# fmt: off

"""Recovered legacy ontology source retained for migration provenance.

The canonical ontology is maintained in ``macroareas.json``, ``areas.json``,
and ``subareas.json``. Do not use this module as a runtime data source.
"""

import json
import uuid
from collections import defaultdict, deque

# ============================================================
# STRUTTURA GERARCHICA - LOTTO PILOTA
# ============================================================

# Formato: {id: {"label": ..., "type": ..., "parent": ..., "description": ...}}
nodes = {}
edges = []

def add_node(node_id, label, node_type, parent_id, description):
    if node_id in nodes:
        raise ValueError(f"ID duplicato: {node_id}")
    nodes[node_id] = {
        "id": node_id,
        "label": label,
        "type": node_type,
        "parent_id": parent_id,
        "description": description,
        "language": "it"
    }
    if parent_id is not None:
        edges.append({"source": parent_id, "target": node_id, "relation": "CONTAINS"})

def add_related(source, target):
    edges.append({"source": source, "target": target, "relation": "RELATED_TO"})

# ============================================================
# MACROAREE (43)
# ============================================================

macroaree = [
    ("lingua_italiana", "Lingua italiana", "Storia, normativa, uso e varietà della lingua italiana"),
    ("grammatica_linguistica", "Grammatica e linguistica", "Studio scientifico del linguaggio e delle sue strutture"),
    ("letteratura", "Letteratura", "Produzione letteraria italiana e mondiale"),
    ("storia", "Storia", "Studio del passato umano attraverso fonti e interpretazioni"),
    ("geografia", "Geografia", "Studio della Terra, dei suoi abitanti e dei fenomeni spaziali"),
    ("matematica", "Matematica", "Studio dei numeri, delle strutture, degli spazi e dei cambiamenti"),
    ("logica", "Logica", "Studio del ragionamento valido e delle inferenze"),
    ("statistica_probabilita", "Statistica e probabilità", "Raccolta, analisi dei dati e studio degli eventi casuali"),
    ("fisica", "Fisica", "Studio della materia, dell'energia e delle loro interazioni"),
    ("chimica", "Chimica", "Studio della composizione, struttura e trasformazione della materia"),
    ("biologia", "Biologia", "Studio degli organismi viventi e dei processi vitali"),
    ("medicina_salute", "Medicina e salute", "Scienza della cura, prevenzione e benessere dell'organismo umano"),
    ("astronomia", "Astronomia", "Studio degli oggetti celesti e dell'universo"),
    ("scienze_terra", "Scienze della Terra", "Studio della litosfera, idrosfera, atmosfera e loro dinamiche"),
    ("ambiente_ecologia", "Ambiente ed ecologia", "Rapporti tra organismi e ambiente, sostenibilità e conservazione"),
    ("informatica", "Informatica", "Studio teorico e pratico dell'elaborazione automatica dell'informazione"),
    ("intelligenza_artificiale", "Intelligenza artificiale", "Sistemi computazionali in grado di simulare l'intelligenza umana"),
    ("ingegneria", "Ingegneria", "Applicazione delle scienze esatte alla progettazione e costruzione"),
    ("tecnologia", "Tecnologia", "Strumenti, tecniche e processi per risolvere problemi pratici"),
    ("economia", "Economia", "Studio della produzione, distribuzione e consumo di beni e servizi"),
    ("finanza", "Finanza", "Gestione del capitale, degli investimenti e dei mercati monetari"),
    ("diritto", "Diritto", "Sistema di norme che regolano la convivenza umana"),
    ("politica_istituzioni", "Politica e istituzioni", "Organizzazione del potere, governo e amministrazione pubblica"),
    ("filosofia", "Filosofia", "Indagine critica sui fondamenti del sapere, dell'essere e dell'agire"),
    ("etica", "Etica", "Studio dei principi morali e della condotta umana"),
    ("psicologia", "Psicologia", "Studio scientifico del comportamento e dei processi mentali"),
    ("sociologia", "Sociologia", "Studio delle strutture sociali e delle dinamiche collettive"),
    ("antropologia", "Antropologia", "Studio dell'uomo in tutte le sue dimensioni biologiche e culturali"),
    ("religioni", "Religioni", "Sistemi di credenze, pratiche rituali e fenomeni religiosi"),
    ("arte", "Arte", "Espressione creativa attraverso forme visive e concettuali"),
    ("musica", "Musica", "Arte dell'organizzazione dei suoni nel tempo"),
    ("cinema_spettacolo", "Cinema e spettacolo", "Arti sceniche, cinematografiche e dello spettacolo dal vivo"),
    ("architettura", "Architettura", "Arte e tecnica di progettare e costruire spazi abitati"),
    ("comunicazione", "Comunicazione", "Processi di trasmissione e scambio di informazioni"),
    ("educazione", "Educazione", "Processi di formazione, istruzione e sviluppo delle persone"),
    ("lavoro_professioni", "Lavoro e professioni", "Attività lavorative, mercato del lavoro e figure professionali"),
    ("industria_manifattura", "Industria e manifattura", "Trasformazione industriale delle materie prime in prodotti"),
    ("agricoltura", "Agricoltura", "Coltivazione del suolo, allevamento e produzione agroalimentare"),
    ("energia", "Energia", "Fonti, produzione, distribuzione e consumo di energia"),
    ("trasporti", "Trasporti", "Sistemi e infrastrutture per il movimento di persone e merci"),
    ("cucina_alimentazione", "Cucina e alimentazione", "Preparazione dei cibi, dietetica e cultura gastronomica"),
    ("sport", "Sport", "Attività fisiche agonistiche e ricreative regolate"),
    ("vita_quotidiana", "Vita quotidiana", "Routine, pratiche e aspetti ordinari dell'esistenza"),
    ("competenze_pratiche", "Competenze pratiche", "Abilità manuali e know-how per la gestione autonoma della vita"),
    ("cultura_digitale", "Cultura digitale", "Competenze, pratiche e fenomeni della società digitale"),
    ("sicurezza", "Sicurezza", "Protezione da rischi, minacce e pericoli per persone e beni"),
    ("cittadinanza", "Cittadinanza", "Diritti, doveri e partecipazione alla vita collettiva"),
    ("attualita_societa", "Attualità e società", "Fenomeni, dibattiti e dinamiche del contemporaneo"),
]

for m_id, m_label, m_desc in macroaree:
    add_node(m_id, m_label, "macroarea", None, m_desc)

print(f"Macroaree inserite: {len(macroaree)}")

# ============================================================
# AREE (max 10 per macroarea)
# ============================================================

aree_data = [
    # Lingua italiana
    ("lingua_italiana", [
        ("li_storia", "Storia della lingua", "Evoluzione storica dell'italiano dal latino ai giorni nostri"),
        ("li_normativa", "Normativa linguistica", "Regole, accademie e istituzioni che normano la lingua"),
        ("li_lessico", "Lessicologia e lessicografia", "Studio del vocabolario, dei neologismi e dei dizionari"),
        ("li_varieta", "Varietà linguistiche", "Dialetti, registri, italiano regionale e socioletti"),
        ("li_ortografia", "Ortografia e pronuncia", "Norme di scrittura, accento e fonetica italiana"),
        ("li_uso", "Uso della lingua", "Pratiche comunicative, lingua dei media e dei giovani"),
        ("li_italiano_l2", "Italiano come L2", "Insegnamento e apprendimento dell'italiano per stranieri"),
        ("li_tecniche_scrittura", "Tecniche di scrittura", "Stili, generi testuali e strategie di composizione"),
    ]),
    # Grammatica e linguistica
    ("grammatica_linguistica", [
        ("gl_fonologia", "Fonologia e fonetica", "Studio dei suoni del linguaggio"),
        ("gl_morfologia", "Morfologia", "Formazione delle parole, flessione e derivazione"),
        ("gl_sintassi", "Sintassi", "Struttura delle frasi e relazioni tra costituenti"),
        ("gl_semantica", "Semantica e pragmatica", "Significato delle espressioni e uso contestuale"),
        ("gl_tipologia", "Tipologia linguistica", "Classificazione delle lingue del mondo"),
        ("gl_sociolinguistica", "Sociolinguistica", "Rapporto tra lingua e società"),
        ("gl_psicolinguistica", "Psicolinguistica", "Processi mentali sottostanti al linguaggio"),
        ("gl_neurolinguistica", "Neurolinguistica", "Basi neurali del linguaggio e patologie"),
        ("gl_linguistica_computazionale", "Linguistica computazionale", "Elaborazione del linguaggio naturale con metodi informatici"),
        ("gl_stilistica", "Stilistica e retorica", "Analisi dello stile e delle figure retoriche"),
    ]),
    # Letteratura
    ("letteratura", [
        ("let_italiana", "Letteratura italiana", "Opere, autori e movimenti della letteratura in Italia"),
        ("let_europea", "Letteratura europea", "Tradizioni letterarie dei principali paesi europei"),
        ("let_mondiale", "Letteratura mondiale", "Letterature extraeuropee e letteratura comparata"),
        ("let_poesia", "Poesia", "Generi poetici, metrica e movimenti lirici"),
        ("let_narrativa", "Narrativa", "Romanzo, racconto, novella e tecniche narrative"),
        ("let_teatro", "Teatro letterario", "Drammaturgia e storia del teatro come forma letteraria"),
        ("let_saggistica", "Saggistica e critica", "Opere di critica letteraria, teoria e saggistica"),
        ("let_generi", "Generi letterari", "Classificazione e caratteristiche dei generi"),
        ("let_orale", "Tradizione orale", "Fiabe, leggende e narrazione popolare"),
        ("let_contemporanea", "Letteratura contemporanea", "Produzione letteraria dagli anni Ottanta a oggi"),
    ]),
    # Storia
    ("storia", [
        ("st_antica", "Storia antica", "Civiltà del Mediterraneo e del Vicino Oriente fino al V secolo"),
        ("st_medioevo", "Storia medievale", "Europa e Mediterraneo dal V al XV secolo"),
        ("st_moderna", "Storia moderna", "Età moderna dal XV al XVIII secolo"),
        ("st_contemporanea", "Storia contemporanea", "Dalla Rivoluzione francese al presente"),
        ("st_italia", "Storia d'Italia", "Eventi politici, sociali e culturali della penisola italiana"),
        ("st_metodologia", "Storiografia e metodologia", "Teoria della storia, fonti e metodi critici"),
        ("st_economica", "Storia economica", "Evoluzione dei sistemi economici e del lavoro"),
        ("st_sociale", "Storia sociale", "Vita quotidiana, classi e stratificazione nel tempo"),
        ("st_culturale", "Storia culturale", "Mentalità, rappresentazioni e pratiche simboliche"),
        ("st_militare", "Storia militare", "Guerre, strategie e tecnologie belliche"),
    ]),
    # Geografia
    ("geografia", [
        ("geo_fisica", "Geografia fisica", "Rilievi, climi, idrografia e ecosistemi terrestri"),
        ("geo_umana", "Geografia umana", "Popolazione, insediamenti e attività antropiche"),
        ("geo_politica", "Geografia politica", "Confini, Stati e organizzazione territoriale"),
        ("geo_economica", "Geografia economica", "Distribuzione delle risorse e dei settori produttivi"),
        ("geo_regionale", "Geografia regionale", "Studio delle aree geografiche del mondo"),
        ("geo_italia", "Geografia dell'Italia", "Territorio, regioni e caratteristiche della penisola"),
        ("geo_europa", "Geografia dell'Europa", "Caratteristiche fisiche e umane del continente europeo"),
        ("geo_cartografia", "Cartografia e GIS", "Tecniche di rappresentazione e sistemi informativi geografici"),
        ("geo_ambientale", "Geografia ambientale", "Rapporto tra ambiente e sviluppo sostenibile"),
        ("geo_urbana", "Geografia urbana", "Città, metropolitanizzazione e pianificazione"),
    ]),
    # Matematica
    ("matematica", [
        ("mat_aritmetica", "Aritmetica", "Numeri, operazioni e proprietà fondamentali"),
        ("mat_algebra", "Algebra", "Strutture algebriche, equazioni e polinomi"),
        ("mat_geometria", "Geometria", "Studio delle forme, spazi e trasformazioni"),
        ("mat_analisi", "Analisi matematica", "Calcolo differenziale, integrale e successioni"),
        ("mat_probabilita", "Calcolo delle probabilità", "Teoria assiomatica e distribuzioni"),
        ("mat_statistica_matematica", "Statistica matematica", "Inferenza, stima e test d'ipotesi"),
        ("mat_logica_matematica", "Logica matematica", "Sistemi formali, dimostrazioni e teoria dei modelli"),
        ("mat_storia", "Storia della matematica", "Evoluzione del pensiero matematico nelle civiltà"),
        ("mat_matematica_applicata", "Matematica applicata", "Modelli matematici per scienze e ingegneria"),
        ("mat_teoria_numeri", "Teoria dei numeri", "Proprietà degli interi e strutture aritmetiche"),
    ]),
    # Logica
    ("logica", [
        ("log_formale", "Logica formale", "Sistemi deduttivi, sintassi e semantica"),
        ("log_proposizionale", "Logica proposizionale", "Calcolo dei connettivi e delle tautologie"),
        ("log_predicativa", "Logica predicativa", "Quantificatori, predicati e strutture del primo ordine"),
        ("log_modale", "Logica modale", "Necessità, possibilità e mondi possibili"),
        ("log_filosofica", "Logica filosofica", "Fondamenti, paradossi e teorie del ragionamento"),
        ("log_informatica", "Logica per l'informatica", "Programmazione logica, verifica e dimostrazione automatica"),
        ("log_argomentazione", "Teoria dell'argomentazione", "Schemi inferenziali e fallacie"),
        ("log_decisione", "Teoria della decisione", "Scelta razionale sotto incertezza"),
    ]),
    # Statistica e probabilità
    ("statistica_probabilita", [
        ("sp_descrittiva", "Statistica descrittiva", "Rappresentazione e sintesi dei dati"),
        ("sp_inferenziale", "Statistica inferenziale", "Stima, intervalli di confidenza e test"),
        ("sp_probabilita", "Teoria della probabilità", "Assiomi, variabili casuali e teoremi limite"),
        ("sp_modelli", "Modelli statistici", "Regressione, ANOVA e modelli lineari"),
        ("sp_campionamento", "Tecniche di campionamento", "Metodi per selezionare sottoinsiemi rappresentativi"),
        ("sp_dati", "Analisi dei dati", "Esplorazione, pulizia e preparazione dei dataset"),
        ("sp_bayesiana", "Statistica bayesiana", "Approccio basato sul teorema di Bayes"),
        ("sp_sperimentali", "Progetti sperimentali", "Design degli esperimenti e controllo delle variabili"),
        ("sp_applicazioni", "Applicazioni pratiche", "Sondaggi, demografia e ricerca di mercato"),
    ]),
    # Fisica
    ("fisica", [
        ("fis_meccanica", "Meccanica classica", "Cinematica, dinamica, statica e fluidi"),
        ("fis_termodinamica", "Termodinamica", "Calore, lavoro, entropia e macchine termiche"),
        ("fis_elettromagnetismo", "Elettromagnetismo", "Elettricità, magnetismo e onde elettromagnetiche"),
        ("fis_ottica", "Ottica", "Luce, lenti, interferenza e diffrazione"),
        ("fis_relativita", "Relatività", "Teorie ristretta e generale di Einstein"),
        ("fis_quantistica", "Meccanica quantistica", "Dualismo onda-particella, principio di indeterminazione"),
        ("fis_nucleare", "Fisica nucleare", "Nucleo atomico, radioattività e reazioni nucleari"),
        ("fis_particelle", "Fisica delle particelle", "Quark, leptoni, bosoni e interazioni fondamentali"),
        ("fis_astrofisica", "Astrofisica", "Fisica applicata agli oggetti celesti"),
        ("fis_storia", "Storia della fisica", "Evoluzione delle teorie fisiche e dei grandi esperimenti"),
    ]),
    # Chimica
    ("chimica", [
        ("chim_generale", "Chimica generale", "Struttura atomica, legami e stechiometria"),
        ("chim_organica", "Chimica organica", "Composti del carbonio, reazioni e sintesi"),
        ("chim_inorganica", "Chimica inorganica", "Composti minerali, metalli e non metalli"),
        ("chim_analitica", "Chimica analitica", "Metodi di identificazione e quantificazione"),
        ("chim_fisica", "Chimica fisica", "Termodinamica, cinetica e spettroscopia"),
        ("chim_biochimica", "Biochimica", "Processi chimici nei sistemi viventi"),
        ("chim_ambientale", "Chimica ambientale", "Inquinanti, cicli biogeochimici e sostenibilità"),
        ("chim_materiali", "Scienza dei materiali", "Proprietà e applicazioni dei materiali"),
        ("chim_industriale", "Chimica industriale", "Processi produttivi e ingegneria chimica"),
        ("chim_storia", "Storia della chimica", "Dall'alchimia alla chimica moderna"),
    ]),
]

for parent, aree in aree_data:
    for a_id, a_label, a_desc in aree:
        add_node(a_id, a_label, "area", parent, a_desc)

print(f"Aree inserite: {sum(len(v) for _, v in aree_data)}")

# Continuazione AREE

aree_data_2 = [
    # Biologia
    ("biologia", [
        ("bio_botanica", "Botanica", "Studio delle piante e dei loro processi vitali"),
        ("bio_zoologia", "Zoologia", "Studio degli animali, tassonomia e comportamento"),
        ("bio_genetica", "Genetica", "Ereditarietà, DNA, genomi e ingegneria genetica"),
        ("bio_microbiologia", "Microbiologia", "Batteri, virus, funghi e microrganismi"),
        ("bio_ecologia", "Ecologia biologica", "Interazioni tra organismi e ambiente"),
        ("bio_evolution", "Evoluzione", "Teoria darwiniana, speciazione e filogenesi"),
        ("bio_cellulare", "Biologia cellulare", "Struttura e funzione della cellula"),
        ("bio_molecolare", "Biologia molecolare", "Processi molecolari della replicazione e espressione genica"),
        ("bio_fisiologia", "Fisiologia", "Funzioni degli organismi e dei loro apparati"),
        ("bio_antropologia", "Antropologia biologica", "Evoluzione umana e biodiversità"),
    ]),
    # Medicina e salute
    ("medicina_salute", [
        ("med_anatomia", "Anatomia", "Struttura del corpo umano"),
        ("med_fisiologia", "Fisiologia umana", "Funzioni degli apparati e degli organi"),
        ("med_patologia", "Patologia", "Studio delle malattie e delle loro cause"),
        ("med_farmacologia", "Farmacologia", "Farmaci, meccanismi d'azione e terapie"),
        ("med_chirurgia", "Chirurgia", "Tecniche operatorie e specialità chirurgiche"),
        ("med_psichiatria", "Psichiatria e salute mentale", "Disturbi psichici e trattamenti"),
        ("med_pediatria", "Pediatria", "Medicina dell'infanzia e dell'adolescenza"),
        ("med_prevenzione", "Medicina preventiva", "Igiene, vaccini e promozione della salute"),
        ("med_nutrizione", "Nutrizione clinica", "Dieta, metabolismo e patologie nutrizionali"),
        ("med_emergenza", "Medicina d'emergenza", "Pronto soccorso, rianimazione e trauma"),
    ]),
    # Astronomia
    ("astronomia", [
        ("astro_sistema_solare", "Sistema solare", "Pianeti, satelliti, asteroidi e comete"),
        ("astro_stelle", "Stelle ed evoluzione stellare", "Nascita, vita e morte delle stelle"),
        ("astro_galassie", "Galassie e cosmologia", "Struttura dell'universo e modelli cosmologici"),
        ("astro_osservazione", "Osservazione astronomica", "Strumenti, tecniche e cataloghi celesti"),
        ("astro_esopianeti", "Esopianeti", "Pianeti extrasolari e ricerca di vita"),
        ("astro_radio", "Radioastronomia", "Studio delle onde radio cosmiche"),
        ("astro_storia", "Storia dell'astronomia", "Dall'antichità all'astronomia moderna"),
        ("astro_astronautica", "Astronautica", "Tecnologie per l'esplorazione spaziale"),
    ]),
    # Scienze della Terra
    ("scienze_terra", [
        ("st_geologia", "Geologia", "Studio della litosfera, rocce e minerali"),
        ("st_vulcanologia", "Vulcanologia", "Vulcani, magma ed eruzioni"),
        ("st_sismologia", "Sismologia", "Terremoti, onde sismiche e rischio sismico"),
        ("st_paleontologia", "Paleontologia", "Fossili ed evoluzione della vita sulla Terra"),
        ("st_idrogeologia", "Idrogeologia", "Acque sotterranee e loro dinamica"),
        ("st_oceanografia", "Oceanografia", "Studio degli oceani e dei loro fenomeni"),
        ("st_climatologia", "Climatologia", "Climi del passato e del presente"),
        ("st_geochimica", "Geochimica", "Composizione chimica della Terra"),
        ("st_geofisica", "Geofisica", "Fisica della Terra e dei suoi campi"),
        ("st_cartografia_geologica", "Cartografia geologica", "Rappresentazione del sottosuolo"),
    ]),
    # Ambiente ed ecologia
    ("ambiente_ecologia", [
        ("amb_ecosistemi", "Ecosistemi", "Comunità biotiche e abiotiche e loro dinamiche"),
        ("amb_biodiversita", "Biodiversità", "Variabilità della vita a tutti i livelli"),
        ("amb_cambiamento_climatico", "Cambiamento climatico", "Riscaldamento globale e sue conseguenze"),
        ("amb_inquinamento", "Inquinamento", "Contaminazione dell'aria, acqua e suolo"),
        ("amb_sostenibilita", "Sviluppo sostenibile", "Modelli di sviluppo a basso impatto ambientale"),
        ("amb_energie_rinnovabili", "Energie rinnovabili", "Fonti energetiche alternative e pulite"),
        ("amb_gestione_risorse", "Gestione delle risorse naturali", "Acqua, suolo, foreste e pesca"),
        ("amb_urbanistica_verde", "Urbanistica verde", "Città sostenibili e infrastrutture verdi"),
        ("amb_educazione_ambientale", "Educazione ambientale", "Sensibilizzazione e comportamenti eco-sostenibili"),
        ("amb_politiche", "Politiche ambientali", "Normative, accordi internazionali e governance"),
    ]),
    # Informatica
    ("informatica", [
        ("info_algoritmi", "Algoritmi e strutture dati", "Progettazione e analisi di algoritmi"),
        ("info_programmazione", "Programmazione", "Linguaggi, paradigmi e tecniche di codifica"),
        ("info_software", "Ingegneria del software", "Progettazione, sviluppo e manutenzione di sistemi"),
        ("info_architetture", "Architetture dei calcolatori", "Hardware, processori e memorie"),
        ("info_sistemi_operativi", "Sistemi operativi", "Gestione delle risorse di un computer"),
        ("info_reti", "Reti di calcolatori", "Protocolli, Internet e comunicazione dati"),
        ("info_sicurezza_informatica", "Sicurezza informatica", "Crittografia, minacce e difesa dei sistemi"),
        ("info_basi_dati", "Basi di dati", "Progettazione e gestione dei database"),
        ("info_grafica", "Grafica computazionale", "Visualizzazione, rendering e realtà virtuale"),
        ("info_storia", "Storia dell'informatica", "Evoluzione dei computer e del software"),
    ]),
    # Intelligenza artificiale
    ("intelligenza_artificiale", [
        ("ia_apprendimento", "Apprendimento automatico", "Algoritmi che apprendono dai dati"),
        ("ia_deep_learning", "Deep learning", "Reti neurali profonde e rappresentazioni gerarchiche"),
        ("ia_nlp", "Elaborazione del linguaggio naturale", "Comprensione e generazione del linguaggio"),
        ("ia_visione", "Visione artificiale", "Riconoscimento e interpretazione di immagini e video"),
        ("ia_ragionamento", "Ragionamento automatico", "Sistemi esperti, pianificazione e logica"),
        ("ia_robotica", "Robotica intelligente", "Agenti autonomi, sensori e attuatori"),
        ("ia_etica_ia", "Etica dell'IA", "Bias, responsabilità e impatto sociale"),
        ("ia_generativa", "IA generativa", "Modelli per la creazione di contenuti"),
        ("ia_multimodale", "Intelligenza multimodale", "Fusione di testo, immagine, audio e video"),
        ("ia_storia", "Storia dell'IA", "Dalle origini simboliche ai modelli fondazionali"),
    ]),
    # Ingegneria
    ("ingegneria", [
        ("ing_civile", "Ingegneria civile", "Progettazione di infrastrutture e costruzioni"),
        ("ing_meccanica", "Ingegneria meccanica", "Macchine, meccanismi e sistemi energetici"),
        ("ing_elettrica", "Ingegneria elettrica", "Produzione, trasmissione e utilizzo dell'energia elettrica"),
        ("ing_elettronica", "Ingegneria elettronica", "Circuiti, semiconduttori e sistemi embedded"),
        ("ing_informatica", "Ingegneria informatica", "Sistemi hardware-software integrati"),
        ("ing_chimica", "Ingegneria chimica", "Processi industriali e reattori"),
        ("ing_aerospaziale", "Ingegneria aerospaziale", "Aeromobili, veicoli spaziali e propulsione"),
        ("ing_biomedica", "Ingegneria biomedica", "Dispositivi medici e sistemi per la salute"),
        ("ing_ambientale", "Ingegneria ambientale", "Tecnologie per la protezione ambientale"),
        ("ing_gestionale", "Ingegneria gestionale", "Organizzazione, logistica e ottimizzazione"),
    ]),
    # Tecnologia
    ("tecnologia", [
        ("tec_telecomunicazioni", "Telecomunicazioni", "Tecnologie per la trasmissione a distanza"),
        ("tec_nanotecnologie", "Nanotecnologie", "Manipolazione della materia a scala nanometrica"),
        ("tec_biotecnologie", "Biotecnologie", "Applicazione tecnologica ai sistemi biologici"),
        ("tec_materiali_avanzati", "Materiali avanzati", "Grafene, metamateriali e leghe innovative"),
        ("tec_stampa_3d", "Stampa 3D", "Tecniche di manifattura additiva"),
        ("tec_quantistica", "Tecnologie quantistiche", "Computer, sensori e comunicazione quantistica"),
        ("tec_industria_4", "Industria 4.0", "Automazione, IoT e fabbriche intelligenti"),
        ("tec_wearable", "Dispositivi indossabili", "Smartwatch, sensori biometrici e realtà aumentata"),
        ("tec_droni", "Droni e veicoli autonomi", "Robotica aerea e guida autonoma"),
        ("tec_blocchi", "Tecnologia blockchain", "Registri distribuiti e smart contract"),
    ]),
    # Economia
    ("economia", [
        ("eco_micro", "Microeconomia", "Comportamento di consumatori, imprese e mercati"),
        ("eco_macro", "Macroeconomia", "Aggregati economici, PIL, inflazione e disoccupazione"),
        ("eco_storia", "Storia economica", "Evoluzione dei sistemi economici nel tempo"),
        ("eco_sviluppo", "Economia dello sviluppo", "Crescita, povertà e disuguaglianze"),
        ("eco_internazionale", "Economia internazionale", "Commercio, cambi e integrazione globale"),
        ("eco_lavoro", "Economia del lavoro", "Mercato del lavoro, salari e politiche occupazionali"),
        ("eco_pubblica", "Economia pubblica", "Spesa, tassazione e beni pubblici"),
        ("eco_ambientale", "Economia ambientale", "Esternalità, valutazione e politiche verdi"),
        ("eco_comportamentale", "Economia comportamentale", "Psicologia applicata alle scelte economiche"),
        ("eco_monetaria", "Economia monetaria", "Banche centrali, politiche monetarie e liquidità"),
    ]),
]

for parent, aree in aree_data_2:
    for a_id, a_label, a_desc in aree:
        add_node(a_id, a_label, "area", parent, a_desc)

print(f"Aree totali inserite finora: {len([n for n in nodes.values() if n['type']=='area'])}")

# Continuazione AREE - parte 3

aree_data_3 = [
    # Finanza
    ("finanza", [
        ("fin_mercati", "Mercati finanziari", "Azioni, obbligazioni e strumenti di investimento"),
        ("fin_banche", "Sistema bancario", "Intermediazione creditizia e regolamentazione"),
        ("fin_investimenti", "Gestione degli investimenti", "Portafogli, fondi e analisi dei titoli"),
        ("fin_corporate", "Finanza aziendale", "Struttura del capitale, valutazione e M&A"),
        ("fin_assicurazioni", "Assicurazioni", "Gestione del rischio e prodotti assicurativi"),
        ("fin_fintech", "Fintech", "Tecnologia applicata ai servizi finanziari"),
        ("fin_contabilita", "Contabilità e bilancio", "Principi contabili, revisione e reporting"),
        ("fin_tassazione", "Tassazione", "Imposte dirette, indirette e pianificazione fiscale"),
        ("fin_cripto", "Criptovalute", "Bitcoin, Ethereum e asset digitali"),
        ("fin_macro", "Finanza macroeconomica", "Debito pubblico, spread e politiche di bilancio"),
    ]),
    # Diritto
    ("diritto", [
        ("dir_costituzionale", "Diritto costituzionale", "Struttura dello Stato e diritti fondamentali"),
        ("dir_privato", "Diritto privato", "Persone, famiglia, proprietà e contratti"),
        ("dir_penale", "Diritto penale", "Reati, sanzioni e procedura penale"),
        ("dir_amministrativo", "Diritto amministrativo", "Attività della pubblica amministrazione"),
        ("dir_lavoro", "Diritto del lavoro", "Rapporto di lavoro e tutela dei lavoratori"),
        ("dir_commerciale", "Diritto commerciale", "Imprese, fallimenti e mercati"),
        ("dir_internazionale", "Diritto internazionale", "Rapporti tra Stati e organizzazioni sovranazionali"),
        ("dir_ue", "Diritto dell'Unione Europea", "Normativa, istituzioni e giurisprudenza UE"),
        ("dir_ambientale", "Diritto ambientale", "Norme di tutela dell'ambiente e sostenibilità"),
        ("dir_tributario", "Diritto tributario", "Obblighi fiscali e contenzioso"),
    ]),
    # Politica e istituzioni
    ("politica_istituzioni", [
        ("pol_teoria", "Teoria politica", "Ideologie, modelli di governo e pensiero politico"),
        ("pol_istituzioni_it", "Istituzioni italiane", "Parlamento, governo, presidente e magistratura"),
        ("pol_istituzioni_ue", "Istituzioni europee", "Parlamento europeo, Commissione e Consiglio"),
        ("pol_partiti", "Partiti e movimenti", "Organizzazione politica e sistemi di partito"),
        ("pol_elezioni", "Sistemi elettorali", "Leggi elettorali, voto e rappresentanza"),
        ("pol_amministrazione", "Amministrazione pubblica", "Organizzazione e funzionamento della PA"),
        ("pol_relazioni_internazionali", "Relazioni internazionali", "Diplomazia, conflitti e cooperazione globale"),
        ("pol_glocal", "Governance locale", "Regioni, province, comuni e autonomie"),
        ("pol_comunicazione_pol", "Comunicazione politica", "Media, propaganda e opinion pubblica"),
        ("pol_storia_politica", "Storia politica", "Evoluzione dei sistemi politici nel tempo"),
    ]),
    # Filosofia
    ("filosofia", [
        ("fil_antica", "Filosofia antica", "Pensiero greco, romano e orientale antico"),
        ("fil_medievale", "Filosofia medievale", "Scolastica, patristica e pensiero islamico"),
        ("fil_moderna", "Filosofia moderna", "Razionalismo, empirismo e illuminismo"),
        ("fil_contemporanea", "Filosofia contemporanea", "Idealismo, esistenzialismo e filosofia analitica"),
        ("fil_epistemologia", "Epistemologia", "Teoria della conoscenza e della scienza"),
        ("fil_metafisica", "Metafisica", "Studio dell'essere, della realtà e del tempo"),
        ("fil_estetica", "Estetica", "Natura dell'arte, della bellezza e del gusto"),
        ("fil_politica", "Filosofia politica", "Giustizia, Stato e libertà"),
        ("fil_scienza", "Filosofia della scienza", "Fondamenti, metodi e paradigmi scientifici"),
        ("fil_mente", "Filosofia della mente", "Coscienza, identità personale e intelligenza"),
    ]),
    # Etica
    ("etica", [
        ("et_normativa", "Etica normativa", "Teorie del dovere, della virtù e della consequenzialità"),
        ("et_applicata", "Etica applicata", "Bioetica, etica ambientale ed etica professionale"),
        ("et_bioetica", "Bioetica", "Dilemmi morali in medicina e biotecnologie"),
        ("et_digitale", "Etica digitale", "Privacy, sorveglianza e diritti nell'era digitale"),
        ("et_ia", "Etica dell'intelligenza artificiale", "Autonomia, responsabilità e bias algoritmici"),
        ("et_ambientale", "Etica ambientale", "Doveri verso la natura e le generazioni future"),
        ("et_professionale", "Deontologia professionale", "Codici etici e responsabilità dei mestieri"),
        ("et_interculturale", "Etica interculturale", "Valori universali e relativismo morale"),
        ("et_animale", "Etica animale", "Diritti degli animali e specismo"),
    ]),
    # Psicologia
    ("psicologia", [
        ("psi_generale", "Psicologia generale", "Percezione, attenzione, memoria e apprendimento"),
        ("psi_sviluppo", "Psicologia dello sviluppo", "Cambiamenti cognitivi ed emotivi nel ciclo di vita"),
        ("psi_sociale", "Psicologia sociale", "Relazioni, atteggiamenti e influenza sociale"),
        ("psi_clinica", "Psicologia clinica", "Diagnosi e trattamento dei disturbi psicologici"),
        ("psi_personalita", "Psicologia della personalità", "Tratti, temperamento e modelli della personalità"),
        ("psi_lavoro", "Psicologia del lavoro", "Selezione, benessere organizzativo e ergonomia"),
        ("psi_educativa", "Psicologia educativa", "Apprendimento scolastico e difficoltà"),
        ("psi_neuro", "Neuropsicologia", "Relazione tra cervello e comportamento"),
        ("psi_sport", "Psicologia dello sport", "Prestazione, motivazione e gestione dello stress"),
        ("psi_forense", "Psicologia forense", "Valutazione psicologica nel contesto giudiziario"),
    ]),
    # Sociologia
    ("sociologia", [
        ("soc_teoria", "Teoria sociologica", "Classici e paradigmi della sociologia"),
        ("soc_stratificazione", "Stratificazione sociale", "Classi, ceti, mobilità e disuguaglianza"),
        ("soc_famiglia", "Sociologia della famiglia", "Forme familiari, genitorialità e relazioni"),
        ("soc_educazione", "Sociologia dell'educazione", "Scuola, istruzione e riproduzione sociale"),
        ("soc_lavoro", "Sociologia del lavoro", "Mercato, professioni e organizzazioni"),
        ("soc_urbana", "Sociologia urbana", "Città, spazi pubblici e metropoli"),
        ("soc_digitale", "Sociologia digitale", "Internet, social media e comunità virtuali"),
        ("soc_devianza", "Devianza e controllo sociale", "Crimine, norme e istituzioni di controllo"),
        ("soc_generale", "Sociologia generale", "Concetti fondamentali e metodi della disciplina"),
        ("soc_cultura", "Sociologia della cultura", "Valori, simboli e pratiche collettive"),
    ]),
    # Antropologia
    ("antropologia", [
        ("ant_culturale", "Antropologia culturale", "Culture, simboli e pratiche sociali"),
        ("ant_fisica", "Antropologia fisica", "Evoluzione umana, genetica e biodiversità"),
        ("ant_linguistica", "Antropologia linguistica", "Linguaggio nelle diverse culture"),
        ("ant_archeologica", "Archeologia", "Studio dei resti materiali delle civiltà passate"),
        ("ant_etnografia", "Etnografia", "Metodi di ricerca sul campo e descrizione culturale"),
        ("ant_religione", "Antropologia della religione", "Credenze, rituali e sacro nelle società"),
        ("ant_medicina", "Antropologia medica", "Malattia, cura e sistemi sanitari culturali"),
        ("ant_visuale", "Antropologia visuale", "Immagini, media e rappresentazioni culturali"),
        ("ant_storia", "Storia dell'antropologia", "Evoluzione della disciplina e dei suoi paradigmi"),
    ]),
    # Religioni
    ("religioni", [
        ("rel_cristianesimo", "Cristianesimo", "Dottrine, storia e confessioni cristiane"),
        ("rel_islam", "Islam", "Corano, sunna, scuole giuridiche e cultura islamica"),
        ("rel_ebraismo", "Ebraismo", "Torah, Talmud, storia e tradizioni ebraiche"),
        ("rel_induismo", "Induismo", "Vedanta, dharma, caste e pratiche devozionali"),
        ("rel_buddismo", "Buddismo", "Quattro nobili verità, nirvana e scuole buddiste"),
        ("rel_storia_religioni", "Storia delle religioni", "Evoluzione del fenomeno religioso"),
        ("rel_fenomenologia", "Fenomenologia religiosa", "Studio comparato delle esperienze religiose"),
        ("rel_secolarizzazione", "Secolarizzazione", "Declino del ruolo pubblico della religione"),
        ("rel_interreligioso", "Dialogo interreligioso", "Incontro e confronto tra tradizioni"),
        ("rel_nuovi_movimenti", "Nuovi movimenti religiosi", "Sette, culti e spiritualità contemporanee"),
    ]),
    # Arte
    ("arte", [
        ("art_pittura", "Pittura", "Tecniche, generi e storia della pittura"),
        ("art_sculptura", "Scultura", "Materiali, tecniche e evoluzione tridimensionale"),
        ("art_storia_arte", "Storia dell'arte", "Periodi, movimenti e critica artistica"),
        ("art_contemporanea", "Arte contemporanea", "Pratiche artistiche dal dopoguerra a oggi"),
        ("art_fotografia", "Fotografia", "Tecniche fotografiche e storia del mezzo"),
        ("art_grafica", "Arti grafiche", "Stampa, incisione e design editoriale"),
        ("art_performance", "Performance art", "Azione, corpo e arte relazionale"),
        ("art_restauro", "Restauro e conservazione", "Tecniche di preservazione del patrimonio"),
        ("art_mercato", "Mercato dell'arte", "Collezionismo, gallerie e valorizzazione"),
        ("art_digitale", "Arte digitale", "Arte generativa, NFT e nuovi media"),
    ]),
]

for parent, aree in aree_data_3:
    for a_id, a_label, a_desc in aree:
        add_node(a_id, a_label, "area", parent, a_desc)

print(f"Aree totali inserite finora: {len([n for n in nodes.values() if n['type']=='area'])}")

# Continuazione AREE - parte 4

aree_data_4 = [
    # Musica
    ("musica", [
        ("mus_teorica", "Teoria musicale", "Armonia, contrappunto, analisi e forme"),
        ("mus_storia", "Storia della musica", "Periodi, scuole e compositori"),
        ("mus_classica", "Musica classica", "Repertorio colto, sinfonico e da camera"),
        ("mus_jazz", "Jazz", "Stili, improvvisazione e grandi interpreti"),
        ("mus_pop_rock", "Musica pop e rock", "Generi commerciali, storia e cultura giovanile"),
        ("mus_folk", "Musica tradizionale e folk", "Etnomusicologia e repertori locali"),
        ("mus_tecnologia", "Tecnologia musicale", "Registrazione, produzione e sintesi sonora"),
        ("mus_educazione", "Educazione musicale", "Didattica, solfeggio e pratica strumentale"),
        ("mus_neuro", "Neuroscienze della musica", "Percezione, emozione e cervello musicale"),
        ("mus_mercato", "Industria musicale", "Editoria, diritti e distribuzione"),
    ]),
    # Cinema e spettacolo
    ("cinema_spettacolo", [
        ("cin_storia", "Storia del cinema", "Dalle origini al cinema contemporaneo"),
        ("cin_teorica", "Teoria e critica cinematografica", "Analisi filmica, generi e autori"),
        ("cin_produzione", "Produzione cinematografica", "Sceneggiatura, regia, fotografia e montaggio"),
        ("cin_teatro", "Teatro", "Drammaturgia, regia, recitazione e scenografia"),
        ("cin_danza", "Danza", "Balletto, danza contemporanea e tradizioni corporee"),
        ("cin_circo", "Circo e arti circensi", "Acrobazia, giocoleria e spettacolo circense"),
        ("cin_televisione", "Televisione", "Generi, palinsesti e industria televisiva"),
        ("cin_streaming", "Piattaforme digitali", "Streaming, web series e nuovi formati"),
        ("cin_festival", "Festival e premi", "Mostre, rassegne e riconoscimenti"),
        ("cin_musical", "Musical e teatro musicale", "Spettacolo che integra canto, danza e recitazione"),
    ]),
    # Architettura
    ("architettura", [
        ("arch_storia", "Storia dell'architettura", "Stili, periodi e monumenti"),
        ("arch_tecnica", "Tecnica progettuale", "Disegno, modellazione e strutture"),
        ("arch_sostenibile", "Architettura sostenibile", "Bioedilizia, efficienza energetica e materiali verdi"),
        ("arch_urbana", "Urbanistica", "Pianificazione territoriale e progettazione urbana"),
        ("arch_paesaggio", "Architettura del paesaggio", "Giardini, parchi e spazi verdi"),
        ("arch_restauro", "Restauro architettonico", "Recupero e conservazione del patrimonio edilizio"),
        ("arch_contemporanea", "Architettura contemporanea", "Tendenze, archistar e nuovi materiali"),
        ("arch_interni", "Design degli interni", "Spazi abitativi, arredamento e lighting design"),
        ("arch_infrastrutture", "Infrastrutture e ingegneria civile", "Ponti, viadotti e grandi opere"),
        ("arch_normativa", "Normativa edilizia", "Leggi urbanistiche, sicurezza e abitabilità"),
    ]),
    # Comunicazione
    ("comunicazione", [
        ("com_teoria", "Teoria della comunicazione", "Modelli, processi e funzioni della comunicazione"),
        ("com_giornalismo", "Giornalismo", "Informazione, inchiesta e generi giornalistici"),
        ("com_pubblicita", "Pubblicità", "Strategie, creatività e media planning"),
        ("com_relazioni", "Relazioni pubbliche", "Reputation management e comunicazione istituzionale"),
        ("com_social", "Social media", "Piattaforme, community management e viralità"),
        ("com_visiva", "Comunicazione visiva", "Grafica, semiotica e design della comunicazione"),
        ("com_interculturale", "Comunicazione interculturale", "Scambi tra culture e mediazione linguistica"),
        ("com_crisi", "Comunicazione di crisi", "Gestione dell'emergenza informativa"),
        ("com_politica", "Comunicazione politica", "Campagne elettorali, spin e framing"),
        ("com_digitale", "Comunicazione digitale", "SEO, content marketing e newsletter"),
    ]),
    # Educazione
    ("educazione", [
        ("edu_pedagogia", "Pedagogia generale", "Teorie dell'educazione e dello sviluppo"),
        ("edu_didattica", "Didattica", "Metodi, strategie e progettazione delle lezioni"),
        ("edu_inclusiva", "Educazione inclusiva", "BES, DSA e barriere all'apprendimento"),
        ("edu_digitale", "Didattica digitale", "LIM, e-learning e ambienti virtuali"),
        ("edu_valutazione", "Valutazione e certificazione", "Prove, griglie e competenze"),
        ("edu_orientamento", "Orientamento scolastico e professionale", "Scelta del percorso e transizioni"),
        ("edu_formazione", "Formazione professionale", "Aggiornamento, lifelong learning e competenze"),
        ("edu_infanzia", "Educazione infantile", "Scuola dell'infanzia e sviluppo precoce"),
        ("edu_superiore", "Università e ricerca", "Sistema universitario, dottorato e accademia"),
        ("edu_storia", "Storia dell'educazione", "Evoluzione delle istituzioni scolastiche"),
    ]),
    # Lavoro e professioni
    ("lavoro_professioni", [
        ("lav_mercato", "Mercato del lavoro", "Occupazione, disoccupazione e dinamiche"),
        ("lav_contratti", "Contratti e normativa", "Tipologie contrattuali e diritti"),
        ("lav_professioni", "Professioni e mestieri", "Figure lavorative e percorsi professionali"),
        ("lav_imprenditorialita", "Imprenditorialità", "Startup, innovazione e business model"),
        ("lav_risorse_umane", "Risorse umane", "Selezione, formazione e welfare aziendale"),
        ("lav_sicurezza", "Sicurezza sul lavoro", "Prevenzione, rischi e normativa"),
        ("lav_remote", "Lavoro remoto e smart working", "Organizzazione flessibile e digitalizzazione"),
        ("lav_giovani", "Inserimento dei giovani", "Tirocini, stage e primo impiego"),
        ("lav_sindacati", "Sindacati e relazioni industriali", "Contrattazione e rappresentanza"),
        ("lav_futuro", "Futuro del lavoro", "Automazione, competenze e nuovi mestieri"),
    ]),
    # Industria e manifattura
    ("industria_manifattura", [
        ("ind_processi", "Processi produttivi", "Metodi di fabbricazione e ottimizzazione"),
        ("ind_automazione", "Automazione industriale", "Robot, PLC e linee automatiche"),
        ("ind_qualita", "Controllo qualità", "Standard, certificazioni e ispezioni"),
        ("ind_supply", "Supply chain", "Logistica, magazzino e gestione fornitori"),
        ("ind_manutenzione", "Manutenzione industriale", "Predittiva, preventiva e correttiva"),
        ("ind_sicurezza", "Sicurezza industriale", "Prevenzione incidenti e gestione rischi"),
        ("ind_sostenibilita", "Industria sostenibile", "Economia circolare e impronta ambientale"),
        ("ind_tessile", "Industria tessile e moda", "Filiera tessile, design e produzione"),
        ("ind_alimentare", "Industria alimentare", "Trasformazione, conservazione e packaging"),
        ("ind_meccanica", "Meccanica e meccatronica", "Componenti, assemblaggio e sistemi integrati"),
    ]),
    # Agricoltura
    ("agricoltura", [
        ("agr_colture", "Coltivazioni", "Cereali, ortaggi, frutta e colture industriali"),
        ("agr_zootecnia", "Zootecnia", "Allevamento di bovini, suini, ovini e avicoli"),
        ("agr_agronomia", "Agronomia", "Gestione del suolo, rotazioni e fertilità"),
        ("agr_fitosanitari", "Fitosanitari e difesa", "Pesticidi, biologico e lotta integrata"),
        ("agr_meccanizzazione", "Meccanizzazione agricola", "Trattori, macchine e precision farming"),
        ("agr_sostenibile", "Agricoltura sostenibile", "Biologico, rigenerativa e permacultura"),
        ("agr_idraulica", "Idraulica agraria", "Irrigazione, drenaggio e gestione idrica"),
        ("agr_forestale", "Selvicoltura", "Gestione dei boschi e prodotti forestali"),
        ("agr_pesca", "Pesca e acquacoltura", "Pesca marittima, fluviale e allevamenti ittici"),
        ("agr_economia", "Economia agraria", "Mercati, PAC e politiche di settore"),
    ]),
    # Energia
    ("energia", [
        ("en_fossili", "Fonti fossili", "Carbone, petrolio, gas naturale e impatto"),
        ("en_nucleare", "Energia nucleare", "Fissione, fusione e gestione scorie"),
        ("en_rinnovabili", "Fonti rinnovabili", "Solare, eolico, idroelettrico e geotermia"),
        ("en_rete", "Reti elettriche", "Trasmissione, distribuzione e smart grid"),
        ("en_storage", "Accumulo energetico", "Batterie, idrogeno e sistemi di stoccaggio"),
        ("en_efficienza", "Efficienza energetica", "Risparmio, isolamento e certificazione"),
        ("en_mercato", "Mercato dell'energia", "Liberalizzazione, prezzi e operatori"),
        ("en_transizione", "Transizione energetica", "Decarbonizzazione e politiche climatiche"),
        ("en_idrogeno", "Idrogeno verde", "Produzione, trasporto e applicazioni"),
        ("en_storia", "Storia energetica", "Dalla rivoluzione industriale alle rinnovabili"),
    ]),
    # Trasporti
    ("trasporti", [
        ("tr_stradale", "Trasporto stradale", "Autoveicoli, infrastrutture viarie e sicurezza"),
        ("tr_ferroviario", "Trasporto ferroviario", "Treni, alta velocità e metropolitane"),
        ("tr_aereo", "Trasporto aereo", "Aviazione civile, aeroporti e compagnie"),
        ("tr_marittimo", "Trasporto marittimo", "Navi, porti e navigazione"),
        ("tr_sostenibile", "Mobilità sostenibile", "Bike sharing, e-mobility e pedonalità"),
        ("tr_logistica", "Logistica e freight", "Trasporto merci, intermodalità e hub"),
        ("tr_normativa", "Normativa sui trasporti", "Codice della strada, regolamenti internazionali"),
        ("tr_infrastrutture", "Infrastrutture di trasporto", "Ponti, gallerie, aeroporti e porti"),
        ("tr_autonomo", "Veicoli autonomi", "Guida automatica e nuove tecnologie"),
        ("tr_storia", "Storia dei trasporti", "Evoluzione delle modalità di spostamento"),
    ]),
]

for parent, aree in aree_data_4:
    for a_id, a_label, a_desc in aree:
        add_node(a_id, a_label, "area", parent, a_desc)

print(f"Aree totali inserite finora: {len([n for n in nodes.values() if n['type']=='area'])}")

# Continuazione AREE - parte 5 (ultime 8 macroaree)

aree_data_5 = [
    # Cucina e alimentazione
    ("cucina_alimentazione", [
        ("cuc_tecniche", "Tecniche di cucina", "Cotture, tagli, impiattamento e preparazioni di base"),
        ("cuc_regionale", "Cucina regionale italiana", "Tradizioni gastronomiche delle regioni"),
        ("cuc_internazionale", "Cucine del mondo", "Tradizioni gastronomiche extra-italiane"),
        ("cuc_pasticceria", "Pasticceria", "Dolci, lievitati e tecniche di pasticceria"),
        ("cuc_nutrizione", "Nutrizione e dietetica", "Principi nutritivi, diete e benessere alimentare"),
        ("cuc_sicurezza", "Sicurezza alimentare", "HACCP, conservazione e igiene"),
        ("cuc_enogastronomia", "Enogastronomia", "Vini, abbinamenti e cultura del bere"),
        ("cuc_sostenibile", "Alimentazione sostenibile", "Km zero, stagionalità e riduzione dello spreco"),
        ("cuc_storia", "Storia dell'alimentazione", "Evoluzione delle diete e dei costumi alimentari"),
        ("cuc_industria", "Industria alimentare", "Trasformazione, packaging e distribuzione"),
    ]),
    # Sport
    ("sport", [
        ("sp_atletica", "Atletica leggera", "Corse, salti, lanci e prove multiple"),
        ("sp_calcio", "Calcio", "Regole, tattiche, storia e competizioni"),
        ("sp_pallacanestro", "Pallacanestro", "Regole, tecniche e campionati"),
        ("sp_pallavolo", "Pallavolo", "Regole, ruoli e competizioni internazionali"),
        ("sp_nuoto", "Nuoto", "Stili, tecnica e competizioni acquatiche"),
        ("sp_ciclismo", "Ciclismo", "Strada, pista, mountain bike e ciclocross"),
        ("sp_sci", "Sport invernali", "Sci alpino, fondo, snowboard e pattinaggio"),
        ("sp_arti_marziali", "Arti marziali", "Judo, karate, boxe e discipline da combattimento"),
        ("sp_olimpici", "Giochi olimpici", "Storia, cerimonie e discipline olimpiche"),
        ("sp_salute", "Sport e salute", "Attività fisica, prevenzione e riabilitazione"),
    ]),
    # Vita quotidiana
    ("vita_quotidiana", [
        ("vq_casa", "Gestione della casa", "Pulizia, organizzazione e manutenzione domestica"),
        ("vq_spese", "Spese e budget familiare", "Gestione delle finanze personali e domestiche"),
        ("vq_tempo", "Gestione del tempo", "Pianificazione, routine e produttività personale"),
        ("vq_relazioni", "Relazioni sociali", "Amicizie, vicinato e dinamiche interpersonali"),
        ("vq_benessere", "Benessere quotidiano", "Sonno, relax e piccole abitudini salutari"),
        ("vq_trasporti", "Spostamenti quotidiani", "Mobilità urbana, pendolarismo e viaggi brevi"),
        ("vq_shopping", "Acquisti e consumo", "Spesa, e-commerce e scelte di consumo"),
        ("vq_famiglia", "Dinamiche familiari", "Convivenza, genitorialità e cura dei familiari"),
        ("vq_tempo_libero", "Tempo libero", "Hobby, svago e attività ricreative"),
        ("vq_stagioni", "Ritmi stagionali", "Adattamenti alla stagione, vacanze e festività"),
    ]),
    # Competenze pratiche
    ("competenze_pratiche", [
        ("cp_fai_da_te", "Fai da te", "Riparazioni, bricolage e progetti manuali"),
        ("cp_cucito", "Cucito e sartoria", "Tecniche di confezione, riparazione e modifica"),
        ("cp_giardinaggio", "Giardinaggio", "Coltivazione ornamentale, potatura e composizioni"),
        ("cp_riparazioni", "Riparazioni domestiche", "Idraulica, elettricità e manutenzione base"),
        ("cp_sopravvivenza", "Sopravvivenza", "Orientamento, primo soccorso e tecniche di emergenza"),
        ("cp_guida", "Guida veicoli", "Patente, codice della strada e guida sicura"),
        ("cp_organizzazione", "Organizzazione personale", "Archiviazione, pianificazione e gestione documenti"),
        ("cp_cura_animali", "Cura degli animali domestici", "Alimentazione, igiene e benessere di cani e gatti"),
        ("cp_riciclo", "Riciclo e riuso", "Upcycling, compostaggio e riduzione rifiuti"),
        ("cp_finanze", "Gestione pratica delle finanze", "Bollette, risparmio e contratti"),
    ]),
    # Cultura digitale
    ("cultura_digitale", [
        ("cd_literacy", "Alfabetizzazione digitale", "Uso base di computer, smartphone e Internet"),
        ("cd_sicurezza", "Sicurezza digitale personale", "Password, phishing e protezione dati"),
        ("cd_privacy", "Privacy online", "Dati personali, GDPR e tracce digitali"),
        ("cd_social", "Uso consapevole dei social", "Netiquette, disinformazione e benessere digitale"),
        ("cd_ecommerce", "Commercio elettronico", "Acquisti online, pagamenti digitali e truffe"),
        ("cd_open_data", "Open data e trasparenza", "Dati pubblici, accesso all'informazione e civic tech"),
        ("cd_gaming", "Videogiochi e gaming", "Generi, cultura e impatto sociale dei videogiochi"),
        ("cd_streaming", "Streaming e piattaforme", "Musica, video e contenuti on demand"),
        ("cd_intelligenza", "Comprensione dell'IA", "Funzionamento di base e impatto quotidiano"),
        ("cd_future", "Futuro digitale", "Metaverso, Web3 e tendenze tecnologiche emergenti"),
    ]),
    # Sicurezza
    ("sicurezza", [
        ("sic_cyber", "Sicurezza informatica", "Protezione di sistemi, reti e dati"),
        ("sic_fisica", "Sicurezza fisica", "Protezione di persone, edifici e infrastrutture"),
        ("sic_sanitaria", "Sicurezza sanitaria", "Prevenzione epidemie, igiene e salute pubblica"),
        ("sic_alimentare", "Sicurezza alimentare", "Contaminazioni, etichette e tracciabilità"),
        ("sic_lavoro", "Sicurezza sul lavoro", "Prevenzione infortuni e malattie professionali"),
        ("sic_stradale", "Sicurezza stradale", "Incidenti, norme e comportamenti"),
        ("sic_domestica", "Sicurezza domestica", "Prevenzione incendi, gas e rischi in casa"),
        ("sic_emergenza", "Gestione delle emergenze", "Protezione civile, piani di evacuazione e soccorso"),
        ("sic_finanziaria", "Sicurezza finanziaria", "Truffe, riciclaggio e stabilità del sistema"),
        ("sic_nazionale", "Sicurezza nazionale", "Difesa, intelligence e terrorismo"),
    ]),
    # Cittadinanza
    ("cittadinanza", [
        ("cit_costituzione", "Costituzione italiana", "Principi fondamentali, diritti e doveri"),
        ("cit_diritti", "Diritti umani", "Dichiarazioni universali e tutela internazionale"),
        ("cit_partecipazione", "Partecipazione democratica", "Voto, referendum e attivismo civico"),
        ("cit_europea", "Cittadinanza europea", "Diritti, libera circolazione e istituzioni UE"),
        ("cit_digitale", "Cittadinanza digitale", "Diritti e doveri nell'ambiente digitale"),
        ("cit_sostenibile", "Cittadinanza sostenibile", "Responsabilità ambientale e consumo critico"),
        ("cit_interculturale", "Cittadinanza interculturale", "Integrazione, pluralismo e dialogo"),
        ("cit_giovani", "Cittadinanza attiva dei giovani", "Volontariato, progetti e impegno sociale"),
        ("cit_globale", "Cittadinanza globale", "Solidarietà internazionale e diritti globali"),
        ("cit_storia", "Storia della cittadinanza", "Evoluzione del concetto dal mondo antico a oggi"),
    ]),
    # Attualità e società
    ("attualita_societa", [
        ("att_media", "Media e informazione", "Giornali, televisione, fake news e pluralismo"),
        ("att_migration", "Migrazioni", "Flussi, integrazione e politiche migratorie"),
        ("att_giustizia_sociale", "Giustizia sociale", "Disuguaglianze, inclusione e diritti civili"),
        ("att_ambiente", "Crisi ambientale", "Cambiamento climatico, eventi estremi e adattamento"),
        ("att_tecnologia", "Tecnologia e società", "Impatti dell'innovazione sulla vita quotidiana"),
        ("att_salute_pubblica", "Salute pubblica", "Pandemie, sanità e accesso alle cure"),
        ("att_economia_soc", "Economia e società", "Crisi, inflazione e welfare"),
        ("att_cultura", "Cultura contemporanea", "Tendenze, movimenti e dibattiti culturali"),
        ("att_generazioni", "Conflitto generazionale", "Giovani, anziani e trasmissione dei valori"),
        ("att_geopolitica", "Geopolitica attuale", "Equilibri di potere, guerre e diplomazia"),
    ]),
]

for parent, aree in aree_data_5:
    for a_id, a_label, a_desc in aree:
        add_node(a_id, a_label, "area", parent, a_desc)

area_count = len([n for n in nodes.values() if n['type']=='area'])
macro_count = len([n for n in nodes.values() if n['type']=='macroarea'])
print(f"Macroaree: {macro_count}, Aree: {area_count}")
print(f"Totale nodi livello 1-2: {macro_count + area_count}")

# ============================================================
# SOTTOAREE - parte 1 (prime 10 macroaree)
# ============================================================

sottoaree_data = [
    # === LINGUA ITALIANA ===
    ("li_storia", [
        ("li_st_origini", "Origini e volgare", "Dal latino alle prime attestazioni volgari"),
        ("li_st_dante", "Dante e la lingua letteraria", "La lingua di Dante e la sua influenza"),
        ("li_st_cinquecento", "Cinquecento e questione della lingua", "Bembo, Machiavelli e le proposte linguistiche"),
        ("li_st_ottocento", "Ottocento e unificazione", "Manzoni, l'unità d'Italia e la lingua nazionale"),
        ("li_st_novecento", "Novecento e neostandard", "Evoluzione della lingua nel Novecento"),
        ("li_st_contemporanea", "Italiano contemporaneo", "Lingua dei media, degli immigrati e del web"),
    ]),
    ("li_normativa", [
        ("li_no_accademia", "Accademia della Crusca", "Storia, vocabolario e normativa purista"),
        ("li_no_treccani", "Enciclopedia Treccani", "Lessicografia e normativa istituzionale"),
        ("li_no_regioni", "Normativa regionale", "Statuti linguistici e bilinguismo"),
        ("li_no_ue", "Italiano nelle istituzioni UE", "Ufficiale, traduzioni e terminologia comunitaria"),
    ]),
    ("li_lessico", [
        ("li_le_neologismi", "Neologismi", "Nuove parole e formazioni recenti"),
        ("li_le_stranierismi", "Stranierismi", "Prestiti, calchi e interferenze linguistiche"),
        ("li_le_regionalismi", "Regionalismi", "Lessico tipico delle diverse aree italiane"),
        ("li_le_tecnicismi", "Tecnicismi", "Terminologia settoriale e specialistica"),
        ("li_le_dialettismi", "Dialettalismi", "Voci dialettali entrate nell'italiano comune"),
    ]),
    ("li_varieta", [
        ("li_va_dialetti", "Dialetti italiani", "Classificazione e caratteristiche dei dialetti"),
        ("li_va_registri", "Registri comunicativi", "Lingua formale, informale, tecnica e poetica"),
        ("li_va_giovanile", "Lingua giovanile", "Gergo, slang e innovazione lessicale giovanile"),
        ("li_va_digitale", "Italiano digitale", "Linguaggio dei social, meme e abbreviazioni"),
    ]),
    ("li_ortografia", [
        ("li_or_accento", "Accento e accento grafico", "Uso dell'accento e sue regole"),
        ("li_or_maiuscole", "Uso delle maiuscole", "Regole di capitalizzazione"),
        ("li_or_punteggiatura", "Punteggiatura", "Uso di virgole, punti, due punti e trattini"),
        ("li_or_fonetica", "Fonetica italiana", "Fonemi, allofoni e trascrizione fonetica"),
    ]),
    ("li_uso", [
        ("li_us_media", "Lingua dei media", "Giornali, televisione e linguaggio giornalistico"),
        ("li_us_pubblica", "Lingua della pubblica amministrazione", "Burocratese e linguaggio amministrativo"),
        ("li_us_giuridica", "Lingua giuridica", "Terminologia e stile del diritto"),
        ("li_us_economica", "Lingua economica", "Lessico della finanza e dell'impresa"),
    ]),
    ("li_italiano_l2", [
        ("li_l2_metodologie", "Metodologie didattiche", "Approcci comunicativi e glottodidattica"),
        ("li_l2_certificazioni", "Certificazioni di italiano", "PLIDA, CILS, CELI e livelli QCER"),
        ("li_l2_errori", "Errori tipici", "Interferenze e difficoltà per specifiche L1"),
    ]),
    ("li_tecniche_scrittura", [
        ("li_ts_generi", "Generi testuali", "Saggio, articolo, recensione e racconto"),
        ("li_ts_stile", "Stile e registro", "Chiarezza, coesione e coerenza testuale"),
        ("li_ts_revisione", "Revisione e correzione", "Tecniche di editing e proofreading"),
    ]),

    # === GRAMMATICA E LINGUISTICA ===
    ("gl_fonologia", [
        ("gl_fo_fonemi", "Fonemi italiani", "Inventario fonemico e distribuzione"),
        ("gl_fo_sillaba", "Sillabazione", "Struttura della sillaba e dittonghi"),
        ("gl_fo_prosodia", "Prosodia", "Accento, intonazione e ritmo"),
        ("gl_fo_mutamento", "Mutamento fonetico", "Evoluzione storica dei suoni"),
    ]),
    ("gl_morfologia", [
        ("gl_mo_flessione", "Flessione nominale e verbale", "Desinenze, coniugazioni e declinazioni"),
        ("gl_mo_derivazione", "Formazione delle parole", "Prefissi, suffissi e composizione"),
        ("gl_mo_avverbi", "Avverbi e preposizioni", "Classificazione e uso"),
        ("gl_mo_pronomi", "Pronomi", "Personali, dimostrativi, relativi e riflessivi"),
        ("gl_mo_aggettivi", "Aggettivi e articoli", "Determinativi, indeterminativi e gradi"),
    ]),
    ("gl_sintassi", [
        ("gl_si_frase", "Struttura della frase", "Soggetto, predicato e complementi"),
        ("gl_si_subordinate", "Proposizioni subordinate", "Relative, temporali, causali e finali"),
        ("gl_si_periodo", "Periodo ipotetico", "Reale, potenziale e irrealizzabile"),
        ("gl_si_concordia", "Concordia grammaticale", "Accordo tra soggetto, verbo e attributo"),
        ("gl_si_passiva", "Costruzione passiva", "Uso, vincoli e alternativi"),
    ]),
    ("gl_semantica", [
        ("gl_se_significato", "Significato lessicale", "Denotazione, connotazione e polisemia"),
        ("gl_se_atto", "Atti linguistici", "Locuzioni, illocuzioni e perlocuzioni"),
        ("gl_se_pragmatica", "Pragmatica linguistica", "Contesto, implicature e presupposizioni"),
        ("gl_se_deissi", "Deissi", "Riferimento spaziale, temporale e personale"),
    ]),
    ("gl_tipologia", [
        ("gl_ti_romanze", "Lingue romanze", "Confronto tra italiano, francese, spagnolo, portoghese"),
        ("gl_ti_germaniche", "Lingue germaniche", "Inglese, tedesco e caratteristiche comuni"),
        ("gl_ti_slave", "Lingue slave", "Russo, polacco e strutture tipologiche"),
        ("gl_ti_classiche", "Lingue classiche", "Latino, greco e loro eredità"),
    ]),
    ("gl_sociolinguistica", [
        ("gl_so_variazione", "Variazione diatopica", "Dialetti e aree linguistiche"),
        ("gl_so_diastratica", "Variazione diastratica", "Livelli sociali e stratificazione"),
        ("gl_so_diamesica", "Variazione diamesica", "Scritto, parlato e digitale"),
        ("gl_so_pianificazione", "Pianificazione linguistica", "Politiche linguistiche e standard"),
    ]),
    ("gl_psicolinguistica", [
        ("gl_ps_acquisizione", "Acquisizione del linguaggio", "Fasi dello sviluppo linguistico"),
        ("gl_ps_bilinguismo", "Bilinguismo", "Apprendimento e uso di due lingue"),
        ("gl_ps_comprensione", "Comprensione del linguaggio", "Processi di parsing e interpretazione"),
        ("gl_ps_produzione", "Produzione del linguaggio", "Pianificazione e articolazione del parlato"),
    ]),
    ("gl_neurolinguistica", [
        ("gl_ne_afasia", "Afasie", "Tipologie, cause e riabilitazione"),
        ("gl_ne_cervello", "Aree cerebrali del linguaggio", "Broca, Wernicke e vie neurali"),
        ("gl_ne_dislessia", "Dislessia e DSA", "Basi neurali e interventi"),
    ]),
    ("gl_linguistica_computazionale", [
        ("gl_lc_nlp", "Elaborazione del linguaggio naturale", "Tokenizzazione, parsing e annotazione"),
        ("gl_lc_corpora", "Corpus linguistici", "Raccolte testuali e loro analisi"),
        ("gl_lc_tagger", "POS tagging e parsing", "Etichettatura morfosintattica automatica"),
        ("gl_lc_sentiment", "Analisi del sentiment", "Opinion mining e classificazione emotiva"),
    ]),
    ("gl_stilistica", [
        ("gl_st_figure", "Figure retoriche", "Schemi e tropi della tradizione classica"),
        ("gl_st_registro", "Analisi del registro", "Livelli di formalità e scelta lessicale"),
        ("gl_st_testo", "Analisi del testo", "Coesione, coerenza e struttura informativa"),
    ]),
]

for parent, sottoaree in sottoaree_data:
    for s_id, s_label, s_desc in sottoaree:
        add_node(s_id, s_label, "sottoarea", parent, s_desc)

sottoarea_count = len([n for n in nodes.values() if n['type']=='sottoarea'])
print(f"Sottoaree inserite finora: {sottoarea_count}")

# SOTTOAREE - parte 2 (Letteratura, Storia, Geografia, Matematica, Logica, Statistica, Fisica, Chimica)

sottoaree_data_2 = [
    # === LETTERATURA ===
    ("let_italiana", [
        ("let_it_duecento", "Letteratura duecentesca", "Scuola siciliana, dolce stil novo e comico"),
        ("let_it_trecento", "Letteratura trecentesca", "Dante, Petrarca, Boccaccio"),
        ("let_it_rinascimento", "Rinascimento", "Umanesimo, Machiavelli, Ariosto e Tasso"),
        ("let_it_barocco", "Barocco", "Marino, scientismo e letteratura barocca"),
        ("let_it_illuminismo", "Illuminismo", "Beccaria, Parini, Goldoni"),
        ("let_it_romanticismo", "Romanticismo", "Foscolo, Manzoni, Leopardi"),
        ("let_it_verismo", "Verismo e Decadentismo", "Verga, Pascoli, D'Annunzio"),
        ("let_it_novecento", "Novecento", "Croce, Svevo, Pirandello, Montale"),
        ("let_it_contemporanea", "Contemporanea", "Calvino, Eco, Ferrante e nuove voci"),
    ]),
    ("let_europea", [
        ("let_eu_francese", "Letteratura francese", "Dalla Chanson de geste al Nouveau Roman"),
        ("let_eu_inglese", "Letteratura inglese", "Shakespeare, romanzo vittoriano e modernismo"),
        ("let_eu_tedesca", "Letteratura tedesca", "Goethe, Romanticismo e letteratura contemporanea"),
        ("let_eu_russa", "Letteratura russa", "Dostoevskij, Tolstoj, Čechov e moderni"),
        ("let_eu_spagnola", "Letteratura spagnola", "Cervantes, Generación del '98 e oltre"),
    ]),
    ("let_mondiale", [
        ("let_mo_americana", "Letteratura americana", "Dalla letteratura coloniale al postmoderno"),
        ("let_mo_latinoamericana", "Letteratura latinoamericana", "Boom, realismo magico e contemporanei"),
        ("let_mo_asiatica", "Letterature asiatiche", "Cina, Giappone, India e tradizioni"),
        ("let_mo_africana", "Letterature africane", "Oralità, postcoloniale e diaspora"),
        ("let_mo_araba", "Letteratura araba", "Classica e contemporanea"),
    ]),
    ("let_poesia", [
        ("let_po_metrica", "Metrica italiana", "Endecasillabo, settenario e versi liberi"),
        ("let_po_lyrica", "Lirica", "Ode, sonetto, canzone, elegia"),
        ("let_po_epica", "Poesia epica", "Omero, Dante, epica moderna"),
        ("let_po_contemporanea", "Poesia contemporanea", "Avanguardie, ermetismo e poesia civile"),
    ]),
    ("let_narrativa", [
        ("let_na_romanzo", "Romanzo", "Storia, tipologie e tecniche narrative"),
        ("let_na_racconto", "Racconto e novella", "Breve, racconto lungo e forma breve"),
        ("let_na_fantascienza", "Fantascienza e fantasy", "Generi speculativi e mondi immaginari"),
        ("let_na_giallo", "Giallo e noir", "Detective story, thriller e hardboiled"),
    ]),
    ("let_teatro", [
        ("let_te_greco", "Teatro greco", "Tragedia, commedia e satira"),
        ("let_te_latino", "Teatro latino", "Plauto, Terenzio, Seneca"),
        ("let_te_italiano", "Teatro italiano", "Commedia dell'arte, Goldoni, Pirandello"),
        ("let_te_contemporaneo", "Teatro contemporaneo", "Drammaturgia e regia novecentesca e oltre"),
    ]),
    ("let_saggistica", [
        ("let_sa_critica", "Critica letteraria", "Metodi, scuole e interpretazioni"),
        ("let_sa_letteraria", "Saggistica letteraria", "Saggio d'arte, cultura e civiltà"),
        ("let_sa_filologica", "Filologia", "Ecdotica, stemmatica e critica del testo"),
    ]),
    ("let_generi", [
        ("let_ge_epica", "Epica", "Caratteristiche e tradizioni eroiche"),
        ("let_ge_lirica", "Lirica", "Espressione soggettiva e forme poetiche"),
        ("let_ge_drammatico", "Drammatico", "Teatro e rappresentazione scenica"),
        ("let_ge_narrativo", "Narrativo", "Prosa, racconto e romanzo"),
    ]),
    ("let_orale", [
        ("let_or_fiaba", "Fiaba", "Struttura, motivi e classificazione"),
        ("let_or_leggenda", "Leggenda e mito", "Tradizioni popolari e fondative"),
        ("let_or_fabula", "Fabula e apologo", "Racconti brevi con morale"),
    ]),
    ("let_contemporanea", [
        ("let_co_postmoderno", "Postmoderno italiano", "Calvino, Eco, narrativa ludica"),
        ("let_co_migranti", "Letteratura migrante", "Scrittori di origine straniera in Italia"),
        ("let_co_giovani", "Nuove generazioni", "Autori emergenti e tendenze"),
    ]),

    # === STORIA ===
    ("st_antica", [
        ("st_an_egitto", "Antico Egitto", "Civiltà, religioni e faraoni"),
        ("st_an_mesopotamia", "Mesopotamia", "Sumeri, Babilonesi e Assiri"),
        ("st_an_grecia", "Grecia antica", "Poleis, democrazia, filosofia e guerre persiane"),
        ("st_an_roma", "Roma antica", "Repubblica, impero, diritto e cristianesimo"),
        ("st_an_oriente", "Antico Oriente", "Persia, Fenici, Ebrei e civiltà preclassiche"),
    ]),
    ("st_medioevo", [
        ("st_me_alto", "Alto Medioevo", "Tardoantico, barbari, regni romano-germanici"),
        ("st_me_basso", "Basso Medioevo", "Comuni, signorie, università e crociate"),
        ("st_me_bizantino", "Impero bizantino", "Costantinopoli, giustizianeo e caduta"),
        ("st_me_islamico", "Mondo islamico medievale", "Espansione, califfati e cultura"),
    ]),
    ("st_moderna", [
        ("st_mo_rinascimento", "Rinascimento", "Umanesimo, Riforma, scoperte geografiche"),
        ("st_mo_assolutismo", "Assolutismo", "Sovranità assoluta e Stato moderno"),
        ("st_mo_rivoluzioni", "Rivoluzioni del Seicento-Settecento", "Inglese, americana, francese"),
        ("st_mo_illuminismo", "Illuminismo", "Ragione, progresso e riforme"),
    ]),
    ("st_contemporanea", [
        ("st_co_ottocento", "Ottocento", "Napoleone, Risorgimento, unità nazionali"),
        ("st_co_novecento", "Novecento", "Guerre mondiali, totalitarismi, guerra fredda"),
        ("st_co_post45", "Dopoguerra", "Ricostruzione, decolonizzazione, globalizzazione"),
        ("st_co_89", "Fine Novecento", "Caduta muri, nuovi equilibri, globalizzazione"),
    ]),
    ("st_italia", [
        ("st_it_antica", "Italia antica", "Etruschi, Magna Grecia, Roma"),
        ("st_it_medioevo", "Italia medievale", "Comuni, signorie, Stato della Chiesa"),
        ("st_it_rinascimento", "Italia rinascimentale", "Principati, arte, cultura"),
        ("st_it_risorgimento", "Risorgimento", "Unità d'Italia, patrioti e monarchia"),
        ("st_it_novecento", "Italia nel Novecento", "Fascismo, guerra, repubblica, boom economico"),
        ("st_it_contemporanea", "Italia contemporanea", "Dagli anni Ottanta a oggi"),
    ]),
    ("st_metodologia", [
        ("st_me_fonti", "Fonti storiche", "Tipologie, critica e interpretazione"),
        ("st_me_storiografia", "Storiografia", "Scuole, metodi e storici fondamentali"),
        ("st_me_orale", "Storia orale", "Testimonianze, memoria e metodologia"),
    ]),
    ("st_economica", [
        ("st_ec_capitalismo", "Storia del capitalismo", "Dalle origini alla globalizzazione"),
        ("st_ec_industriale", "Rivoluzione industriale", "Meccanizzazione, urbanizzazione, nuove classi"),
        ("st_ec_commercio", "Storia del commercio", "Rotte, mercanti e mercati globali"),
    ]),
    ("st_sociale", [
        ("st_so_classi", "Classi sociali", "Nobiltà, borghesia, proletariato, ceti medi"),
        ("st_so_famiglia", "Storia della famiglia", "Strutture, ruoli e trasformazioni"),
        ("st_so_genere", "Storia di genere", "Donne, mascolinità e studi gender"),
    ]),
    ("st_culturale", [
        ("st_cu_mentalita", "Storia delle mentalità", "Credenze, paure e rappresentazioni"),
        ("st_cu_libro", "Storia del libro", "Manoscritti, stampa, editoria"),
        ("st_cu_scuola", "Storia della scuola", "Istruzione, alfabetizzazione e università"),
    ]),
    ("st_militare", [
        ("st_mi_tattica", "Storia militare antica", "Falange, legione, cavalleria"),
        ("st_mi_moderna", "Guerre moderne", "Eserciti permanenti, guerre napoleoniche"),
        ("st_mi_contemporanea", "Guerre contemporanee", "Guerra totale, nucleare, asimmetrica"),
    ]),

    # === GEOGRAFIA ===
    ("geo_fisica", [
        ("geo_fi_rilievi", "Rilievi", "Montagne, pianure, altopiani e loro formazione"),
        ("geo_fi_climi", "Climi", "Classificazione, fattori e zone climatiche"),
        ("geo_fi_idrografia", "Idrografia", "Fiumi, laghi, ghiacciai e acque sotterranee"),
        ("geo_fi_vulcani", "Vulcani e terremoti", "Attività endogena e rischi"),
        ("geo_fi_suoli", "Suoli", "Formazione, tipologie e degradazione"),
    ]),
    ("geo_umana", [
        ("geo_u_popolazione", "Popolazione", "Distribuzione, densità, dinamiche demografiche"),
        ("geo_u_migrazioni", "Migrazioni", "Cause, flussi e impatti"),
        ("geo_u_insediamenti", "Insediamenti", "Urbano, rurale, suburbano e metropolitano"),
        ("geo_u_attivita", "Attività economiche", "Primario, secondario, terziario, quaternario"),
    ]),
    ("geo_politica", [
        ("geo_p_stati", "Stati e nazioni", "Sovranità, confini e forme di governo"),
        ("geo_p_union", "Unioni sovranazionali", "UE, ONU, NATO e organizzazioni"),
        ("geo_p_conflitti", "Conflitti territoriali", "Dispute di confine e geopolitica"),
        ("geo_p_regionalismo", "Regionalismo", "Autonomie, federalismi e decentralizzazione"),
    ]),
    ("geo_economica", [
        ("geo_e_risorse", "Risorse naturali", "Energetiche, minerarie, idriche e agricole"),
        ("geo_e_settori", "Settori produttivi", "Industria, agricoltura, servizi e turismo"),
        ("geo_e_commercio", "Commercio internazionale", "Rotte, accordi e flussi commerciali"),
        ("geo_e_sviluppo", "Sviluppo economico", "Indicatori, divari Nord-Sud e globalizzazione"),
    ]),
    ("geo_regionale", [
        ("geo_r_europa", "Europa", "Caratteristiche fisiche, umane e politiche"),
        ("geo_r_america", "Americhe", "Nord, Centro e Sud America"),
        ("geo_r_asia", "Asia", "Estremo Oriente, Medio Oriente, Asia centrale e meridionale"),
        ("geo_r_africa", "Africa", "Regioni, sfide e potenzialità"),
        ("geo_r_oceania", "Oceania", "Australia, Nuova Zelanda e isole del Pacifico"),
    ]),
    ("geo_italia", [
        ("geo_i_nord", "Italia settentrionale", "Pianura Padana, Alpi, città del Nord"),
        ("geo_i_centro", "Italia centrale", "Appennino, Toscana, Lazio, Umbria, Marche"),
        ("geo_i_sud", "Italia meridionale", "Mezzogiorno, isole, problemi e risorse"),
        ("geo_i_isole", "Isole italiane", "Sicilia, Sardegna e arcipelaghi minori"),
        ("geo_i_regioni", "Regioni italiane", "Caratteristiche specifiche delle 20 regioni"),
    ]),
    ("geo_europa", [
        ("geo_eu_occidentale", "Europa occidentale", "Francia, Germania, Benelux, Regno Unito"),
        ("geo_eu_mediterranea", "Europa mediterranea", "Italia, Spagna, Portogallo, Grecia"),
        ("geo_eu_orientale", "Europa orientale", "Balcani, Slavi, ex URSS europea"),
        ("geo_eu_settentrionale", "Europa settentrionale", "Scandinavia, Baltico, Islanda"),
    ]),
    ("geo_cartografia", [
        ("geo_c_tecniche", "Tecniche cartografiche", "Proiezioni, scale, simboli"),
        ("geo_c_gis", "Sistemi informativi geografici", "GIS, telerilevamento e dati spaziali"),
        ("geo_c_moderna", "Cartografia moderna", "Mappe digitali, GPS e openstreetmap"),
    ]),
    ("geo_ambientale", [
        ("geo_a_cambiamento", "Cambiamento climatico", "Cause, effetti e adattamento"),
        ("geo_a_biodiversita", "Biodiversità e habitat", "Ecosistemi, corridee e aree protette"),
        ("geo_a_rischi", "Rischi ambientali", "Alluvioni, siccità, incendi e frane"),
    ]),
    ("geo_urbana", [
        ("geo_u_citta", "Città e urbanizzazione", "Metropoli, megalopoli e smart city"),
        ("geo_u_pianificazione", "Pianificazione urbana", "Zonizzazione, trasporti e verde urbano"),
        ("geo_u_problemi", "Problemi urbani", "Inquinamento, degrado, periferie e gentrification"),
    ]),
]

for parent, sottoaree in sottoaree_data_2:
    for s_id, s_label, s_desc in sottoaree:
        add_node(s_id, s_label, "sottoarea", parent, s_desc)

sottoarea_count = len([n for n in nodes.values() if n['type']=='sottoarea'])
print(f"Sottoaree inserite finora: {sottoarea_count}")

# SOTTOAREE - parte 3 (Matematica, Logica, Statistica, Fisica, Chimica, Biologia, Medicina, Astronomia, Scienze Terra, Ambiente)

sottoaree_data_3 = [
    # === MATEMATICA ===
    ("mat_aritmetica", [
        ("mat_ar_numeri", "Numeri", "Naturali, interi, razionali, reali, complessi"),
        ("mat_ar_operazioni", "Operazioni", "Addizione, sottrazione, moltiplicazione, divisione, potenze"),
        ("mat_ar_divisibilita", "Divisibilità", "MCD, mcm, numeri primi, criteri"),
        ("mat_ar_frazioni", "Frazioni e percentuali", "Operazioni, proporzioni, calcolo percentuale"),
    ]),
    ("mat_algebra", [
        ("mat_al_equazioni", "Equazioni", "Lineari, quadratiche, sistemi"),
        ("mat_al_polinomi", "Polinomi", "Operazioni, scomposizione, Ruffini"),
        ("mat_al_strutture", "Strutture algebriche", "Gruppi, anelli, campi, spazi vettoriali"),
        ("mat_al_matrici", "Matrici", "Operazioni, determinante, rango, sistemi lineari"),
        ("mat_al_numeri_complessi", "Numeri complessi", "Forma algebrica, trigonometrica, operazioni"),
    ]),
    ("mat_geometria", [
        ("mat_ge_euclidea", "Geometria euclidea", "Piano, spazio, figure, dimostrazioni"),
        ("mat_ge_analitica", "Geometria analitica", "Rette, circonferenze, coniche, coordinate"),
        ("mat_ge_trasformazioni", "Trasformazioni geometriche", "Traslazioni, rotazioni, omotetie"),
        ("mat_ge_solidi", "Solidi geometrici", "Poliedri, corpi rotondi, volume e area"),
        ("mat_ge_non_euclidea", "Geometrie non euclidee", "Iperbolica, ellittica, curvature"),
    ]),
    ("mat_analisi", [
        ("mat_an_limiti", "Limiti", "Definizione, teoremi, forme indeterminate"),
        ("mat_an_derivate", "Derivate", "Definizione, regole, applicazioni"),
        ("mat_an_integrali", "Integrali", "Definiti, indefiniti, tecniche di integrazione"),
        ("mat_an_serie", "Serie numeriche", "Convergenza, criteri, serie note"),
        ("mat_an_funzioni", "Funzioni", "Dominio, segno, studio di funzione"),
    ]),
    ("mat_probabilita", [
        ("mat_pr_assiomi", "Assiomi della probabilità", "Kolmogorov, spazi campionari, eventi"),
        ("mat_pr_variabili", "Variabili casuali", "Discrete, continue, valore atteso, varianza"),
        ("mat_pr_distribuzioni", "Distribuzioni", "Binomiale, normale, di Poisson, esponenziale"),
        ("mat_pr_condizionata", "Probabilità condizionata", "Indipendenza, Bayes, formula delle probabilità totali"),
    ]),
    ("mat_statistica_matematica", [
        ("mat_st_stima", "Stima puntuale", "Metodi, proprietà degli stimatori"),
        ("mat_st_intervalli", "Intervalli di confidenza", "Costruzione e interpretazione"),
        ("mat_st_test", "Test d'ipotesi", "Errori, potenza, p-value"),
        ("mat_st_regressione", "Regressione", "Lineare semplice e multipla"),
    ]),
    ("mat_logica_matematica", [
        ("mat_lo_proposizionale", "Logica proposizionale", "Connettivi, tavole di verità, tautologie"),
        ("mat_lo_predicativa", "Logica predicativa", "Quantificatori, modelli, validità"),
        ("mat_lo_insiemi", "Teoria degli insiemi", "Operazioni, cardinalità, assiomi di ZFC"),
    ]),
    ("mat_storia", [
        ("mat_hi_antica", "Matematica antica", "Babilonesi, egizi, greci"),
        ("mat_hi_medioevo", "Matematica medievale", "Arabi, scolastica, al-Khwarizmi"),
        ("mat_hi_moderna", "Matematica moderna", "Cartesio, Newton, Leibniz, Euler"),
        ("mat_hi_contemporanea", "Matematica contemporanea", "Hilbert, Gödel, Bourbaki"),
    ]),
    ("mat_matematica_applicata", [
        ("mat_ap_modelli", "Modellizzazione", "Equazioni differenziali, sistemi dinamici"),
        ("mat_ap_ottimizzazione", "Ottimizzazione", "Ricerca operativa, programmazione lineare"),
        ("mat_ap_crittografia", "Crittografia", "Teoria dei numeri, RSA, curve ellittiche"),
    ]),
    ("mat_teoria_numeri", [
        ("mat_tn_primi", "Numeri primi", "Teorema fondamentale, distribuzione, congetture"),
        ("mat_tn_congruenze", "Congruenze", "Modulare, teorema cinese del resto"),
        ("mat_tn_diofantee", "Equazioni diofantee", "Metodi e teoremi classici"),
    ]),

    # === LOGICA ===
    ("log_formale", [
        ("log_fo_sintassi", "Sintassi", "Alfabeti, formule ben formate, grammatiche"),
        ("log_fo_semantica", "Semantica", "Interpretazioni, soddisfacibilità, validità"),
        ("log_fo_deduzione", "Sistemi deduttivi", "Assiomi, regole, teoremi"),
        ("log_fo_completeness", "Completezza e compattezza", "Teoremi di completezza, lemma di compattezza"),
    ]),
    ("log_proposizionale", [
        ("log_pr_tavole", "Tavole di verità", "Costruzione e verifica"),
        ("log_pr_forme", "Forme normali", "CNF, DNF, clausole di Horn"),
        ("log_pr_soddisfacibilita", "Soddisfacibilità", "SAT, algoritmi DPLL"),
    ]),
    ("log_predicativa", [
        ("log_pe_quantificatori", "Quantificatori", "Universale, esistenziale, unicità"),
        ("log_pe_modelli", "Modelli e strutture", "Dominio, interpretazione, isomorfismo"),
        ("log_pe_inferenza", "Inferenza", "Regole di deduzione naturale"),
    ]),
    ("log_modale", [
        ("log_mo_necessita", "Necessità e possibilità", "Operatori modali, semantica di Kripke"),
        ("log_mo_sistemi", "Sistemi modali", "K, T, S4, S5 e loro proprietà"),
        ("log_mo_temporale", "Logica temporale", "Futuro, passato, sempre, prima o poi"),
    ]),
    ("log_filosofica", [
        ("log_fi_paradossi", "Paradossi", "Russell, mentitore, insiemistici"),
        ("log_fi_verita", "Teorie della verità", "Corrispondenza, coerenza, pragmatica"),
        ("log_fi_riferimento", "Teorie del riferimento", "Frege, Russell, Kripke"),
    ]),
    ("log_informatica", [
        ("log_in_programmazione", "Programmazione logica", "Prolog, unificazione, risoluzione"),
        ("log_in_verifica", "Verifica formale", "Model checking, dimostrazione automatica"),
        ("log_in_tipi", "Teoria dei tipi", "Lambda calcolo tipato, Curry-Howard"),
    ]),
    ("log_argomentazione", [
        ("log_ar_schemi", "Schemi inferenziali", "Sillogismi, entimemi, analogie"),
        ("log_ar_fallacie", "Fallacie", "Formali, informali, retoriche"),
        ("log_ar_dialettica", "Dialettica", "Dialogo, confutazione, argomentazione persuasiva"),
    ]),
    ("log_decisione", [
        ("log_de_utilita", "Teoria dell'utilità", "Funzioni di utilità, preferenze"),
        ("log_de_giochi", "Teoria dei giochi", "Strategie, equilibri di Nash, dilemmi"),
        ("log_de_rischio", "Gestione del rischio", "Aversione al rischio, assicurazione"),
    ]),

    # === STATISTICA E PROBABILITÀ ===
    ("sp_descrittiva", [
        ("sp_de_indici", "Indici di posizione", "Media, mediana, moda, quantili"),
        ("sp_de_variabilita", "Indici di variabilità", "Varianza, deviazione standard, CV"),
        ("sp_de_forma", "Indici di forma", "Asimmetria, curtosi"),
        ("sp_de_grafici", "Rappresentazioni grafiche", "Istogrammi, boxplot, diagrammi"),
    ]),
    ("sp_inferenziale", [
        ("sp_in_stima", "Stima", "Puntuale, per intervallo, proprietà"),
        ("sp_in_test", "Test d'ipotesi", "Z-test, t-test, chi-quadro, ANOVA"),
        ("sp_in_campioni", "Dimensione campionaria", "Calcolo, potenza, errore"),
    ]),
    ("sp_probabilita", [
        ("sp_pr_assiomi", "Assiomi", "Kolmogorov, probabilità condizionata"),
        ("sp_pr_variabili", "Variabili casuali", "Discrete, continue, trasformazioni"),
        ("sp_pr_convergenza", "Convergenza", "Legge dei grandi numeri, teorema del limite centrale"),
    ]),
    ("sp_modelli", [
        ("sp_mo_regressione", "Regressione lineare", "Semplice, multipla, ipotesi"),
        ("sp_mo_anova", "ANOVA", "A un fattore, a due fattori, interazione"),
        ("sp_mo_logistica", "Regressione logistica", "Classificazione binaria, odds ratio"),
    ]),
    ("sp_campionamento", [
        ("sp_ca_semplice", "Campionamento casuale semplice", "Sorteggio, rappresentatività"),
        ("sp_ca_stratificato", "Campionamento stratificato", "Strati, allocazione"),
        ("sp_ca_cluster", "Campionamento a grappolo", "Cluster, stadio, vantaggi"),
    ]),
    ("sp_dati", [
        ("sp_da_pulizia", "Pulizia dati", "Outlier, missing values, standardizzazione"),
        ("sp_da_esplorativa", "Analisi esplorativa", "EDA, correlazioni, pattern"),
        ("sp_da_preparazione", "Preparazione", "Feature engineering, encoding, scaling"),
    ]),
    ("sp_bayesiana", [
        ("sp_ba_teorema", "Teorema di Bayes", "Formula, interpretazione, esempi"),
        ("sp_ba_priori", "Distribuzioni a priori", "Coniugate, non informative"),
        ("sp_ba_mc", "Metodi MCMC", "Gibbs, Metropolis-Hastings"),
    ]),
    ("sp_sperimentali", [
        ("sp_se_design", "Design sperimentale", "Fattori, livelli, randomizzazione"),
        ("sp_se_controllo", "Gruppi di controllo", "Placebo, doppio cieco"),
        ("sp_se_validita", "Validità interna ed esterna", "Bias, generalizzabilità"),
    ]),
    ("sp_applicazioni", [
        ("sp_ap_sondaggi", "Sondaggi d'opinione", "Metodologia, campione, errore"),
        ("sp_ap_demografia", "Demografia", "Natalità, mortalità, migrazioni"),
        ("sp_ap_mercato", "Ricerca di mercato", "Segmentazione, posizionamento"),
    ]),

    # === FISICA ===
    ("fis_meccanica", [
        ("fis_me_cinematica", "Cinematica", "Moto rettilineo, circolare, armonico"),
        ("fis_me_dinamica", "Dinamica", "Leggi di Newton, forze, attrito"),
        ("fis_me_statica", "Statica", "Equilibrio, momenti, baricentro"),
        ("fis_me_energia", "Energia e lavoro", "Cinetica, potenziale, conservazione"),
        ("fis_me_fluidi", "Fluidodinamica", "Pressione, principio di Archimede, Bernoulli"),
    ]),
    ("fis_termodinamica", [
        ("fis_te_leggi", "Leggi della termodinamica", "Zero, primo, secondo, terzo principio"),
        ("fis_te_gas", "Teoria cinetica dei gas", "Equazione di stato, Maxwell-Boltzmann"),
        ("fis_te_macchine", "Macchine termiche", "Cicli di Carnot, Otto, Diesel"),
        ("fis_te_entropia", "Entropia", "Definizione, irreversibilità, disordine"),
    ]),
    ("fis_elettromagnetismo", [
        ("fis_el_elettrostatica", "Elettrostatica", "Carica, campo, potenziale, condensatori"),
        ("fis_el_magnetismo", "Magnetismo", "Campo magnetico, forza di Lorentz, induzione"),
        ("fis_el_corrente", "Corrente elettrica", "Ohm, circuiti, Kirchhoff"),
        ("fis_el_ondem", "Onde elettromagnetiche", "Spettro, propagazione, applicazioni"),
    ]),
    ("fis_ottica", [
        ("fis_ot_riflessione", "Riflessione e rifrazione", "Leggi, specchi, lenti"),
        ("fis_ot_interferenza", "Interferenza e diffrazione", "Fenditure, reticoli, spettroscopia"),
        ("fis_ot_polarizzazione", "Polarizzazione", "Luce polarizzata, filtri, birifrangenza"),
    ]),
    ("fis_relativita", [
        ("fis_re_ristretta", "Relatività ristretta", "Simultaneità, dilatazione, contrazione"),
        ("fis_re_generale", "Relatività generale", "Spaziotempo, curvature, buchi neri"),
        ("fis_re_esperimenti", "Esperimenti classici", "Michelson-Morley, deflessione luce"),
    ]),
    ("fis_quantistica", [
        ("fis_qu_principi", "Principi fondamentali", "Sovrapposizione, entanglement, misura"),
        ("fis_qu_equazione", "Equazione di Schrödinger", "Forma, interpretazione, soluzioni"),
        ("fis_qu_atomica", "Struttura atomica", "Orbitali, numeri quantici, tavola periodica"),
        ("fis_qu_applicazioni", "Applicazioni", "Laser, transistor, imaging"),
    ]),
    ("fis_nucleare", [
        ("fis_nu_radioattivita", "Radioattività", "Alfa, beta, gamma, decadimento"),
        ("fis_nu_reazioni", "Reazioni nucleari", "Fissione, fusione, catena"),
        ("fis_nu_applicazioni", "Applicazioni", "Reattori, armi, medicina nucleare"),
    ]),
    ("fis_particelle", [
        ("fis_pa_standard", "Modello standard", "Quark, leptoni, bosoni, interazioni"),
        ("fis_pa_acceleratori", "Acceleratori", "LHC, rivelatori, scoperte"),
        ("fis_pa_beyond", "Oltre il modello standard", "Supersimmetria, stringhe, dark matter"),
    ]),
    ("fis_astrofisica", [
        ("fis_as_stelle", "Fisica stellare", "Struttura, evoluzione, nucleosintesi"),
        ("fis_as_buchi_neri", "Buchi neri", "Formazione, orizzonte degli eventi, radiazione Hawking"),
        ("fis_as_cosmologia", "Cosmologia fisica", "Big Bang, espansione, materia oscura"),
    ]),
    ("fis_storia", [
        ("fis_hi_antica", "Fisica antica", "Aristotele, Archimede, meccanica antica"),
        ("fis_hi_classica", "Rivoluzione scientifica", "Galileo, Newton, meccanica classica"),
        ("fis_hi_moderna", "Fisica moderna", "Einstein, Bohr, Heisenberg, rivoluzione quantistica"),
    ]),
]

for parent, sottoaree in sottoaree_data_3:
    for s_id, s_label, s_desc in sottoaree:
        add_node(s_id, s_label, "sottoarea", parent, s_desc)

sottoarea_count = len([n for n in nodes.values() if n['type']=='sottoarea'])
print(f"Sottoaree inserite finora: {sottoarea_count}")

# SOTTOAREE - parte 4 (Chimica, Biologia, Medicina, Astronomia, Scienze Terra, Ambiente, Informatica, IA, Ingegneria, Tecnologia)

sottoaree_data_4 = [
    # === CHIMICA ===
    ("chim_generale", [
        ("ch_ge_struttura", "Struttura atomica", "Atomo, numeri quantici, orbitali"),
        ("ch_ge_legami", "Legami chimici", "Ionico, covalente, metallico, legame a idrogeno"),
        ("ch_ge_stechiometria", "Stechiometria", "Moli, reazioni, bilanciamento"),
        ("ch_ge_stati", "Stati della materia", "Solido, liquido, gas, plasma"),
        ("ch_ge_soluzioni", "Soluzioni", "Concentrazione, proprietà colligative"),
    ]),
    ("chim_organica", [
        ("ch_or_idrocarburi", "Idrocarburi", "Alcani, alcheni, alchini, aromatici"),
        ("ch_or_funzionali", "Gruppi funzionali", "Alcoli, aldeidi, chetoni, acidi, ammine"),
        ("ch_or_isomeria", "Isomeria", "Strutturale, stereoisomeria, chirale"),
        ("ch_or_reazioni", "Reazioni organiche", "Sostituzione, addizione, eliminazione"),
        ("ch_or_biochimica", "Biochimica organica", "Carboidrati, lipidi, proteine, acidi nucleici"),
    ]),
    ("chim_inorganica", [
        ("ch_in_metalli", "Metalli", "Proprietà, reattività, leghe"),
        ("ch_in_non_metalli", "Non metalli", "Gas nobili, alogeni, ossigeno, azoto"),
        ("ch_in_composti", "Composti inorganici", "Ossidi, idrossidi, sali"),
        ("ch_in_coordinazione", "Chimica di coordinazione", "Complessi, ligandi, isomeria"),
    ]),
    ("chim_analitica", [
        ("ch_an_qualitativa", "Analisi qualitativa", "Identificazione di ioni e gruppi"),
        ("ch_an_quantitativa", "Analisi quantitativa", "Titrimetria, gravimetria"),
        ("ch_an_strumentale", "Analisi strumentale", "Spettroscopia, cromatografia, elettrochimica"),
    ]),
    ("chim_fisica", [
        ("ch_fi_termochimica", "Termochimica", "Entalpia, entropia, energia libera"),
        ("ch_fi_cinetica", "Cinetica chimica", "Velocità, catalisi, meccanismi"),
        ("ch_fi_equilibrio", "Equilibrio chimico", "Costante, principio di Le Chatelier"),
        ("ch_fi_elettrochimica", "Elettrochimica", "Pile, elettrolisi, potenziali"),
    ]),
    ("chim_biochimica", [
        ("ch_bi_enzimi", "Enzimi", "Catalisi, cinetica, regolazione"),
        ("ch_bi_metabolismo", "Metabolismo", "Glicolisi, ciclo di Krebs, fosforilazione ossidativa"),
        ("ch_bi_dna", "DNA e replicazione", "Struttura, polimerasi, mutazioni"),
        ("ch_bi_proteine", "Proteine", "Struttura, sintesi, folding"),
    ]),
    ("chim_ambientale", [
        ("ch_am_inquinanti", "Inquinanti chimici", "CO2, NOx, PM, PFAS"),
        ("ch_am_cicli", "Cicli biogeochimici", "Carbonio, azoto, fosforo, zolfo"),
        ("ch_am_green", "Chimica verde", "Principi, solventi, catalisi sostenibile"),
    ]),
    ("chim_materiali", [
        ("ch_ma_polimeri", "Polimeri", "Sintesi, proprietà, riciclaggio"),
        ("ch_ma_nanomateriali", "Nanomateriali", "Fullereni, nanotubi, proprietà"),
        ("ch_ma_ceramici", "Materiali ceramici", "Produzione, proprietà, applicazioni"),
    ]),
    ("chim_industriale", [
        ("ch_in_processi", "Processi industriali", "Haber-Bosch, contatto, cracking"),
        ("ch_in_petrolchimica", "Petrolchimica", "Raffinazione, prodotti, impatto"),
        ("ch_in_farmaceutica", "Chimica farmaceutica", "Sintesi, formulazione, qualità"),
    ]),
    ("chim_storia", [
        ("ch_hi_alchimia", "Alchimia", "Origini, simbolismo, trasmutazione"),
        ("ch_hi_moderna", "Chimica moderna", "Lavoisier, Dalton, Mendeleev"),
        ("ch_hi_contemporanea", "Chimica contemporanea", "Polimeri, farmaci, nanotecnologie"),
    ]),

    # === BIOLOGIA ===
    ("bio_botanica", [
        ("bio_bo_morfologia", "Morfologia vegetale", "Radici, fusti, foglie, fiori"),
        ("bio_bo_fisiologia", "Fisiologia vegetale", "Fotosintesi, traspirazione, nutrizione"),
        ("bio_bo_tassonomia", "Tassonomia vegetale", "Classificazione, famiglie, chiavi"),
        ("bio_bo_ecologia", "Ecologia vegetale", "Fitosociologia, successioni"),
    ]),
    ("bio_zoologia", [
        ("bio_zo_invertebrati", "Invertebrati", "Poriferi, cnidari, molluschi, artropodi"),
        ("bio_zo_vertebrati", "Vertebrati", "Pesci, anfibi, rettili, uccelli, mammiferi"),
        ("bio_zo_comportamento", "Etologia", "Comportamento istintivo, appreso, sociale"),
        ("bio_zo_tassonomia", "Tassonomia animale", "Classificazione, filogenesi"),
    ]),
    ("bio_genetica", [
        ("bio_ge_mendel", "Genetica classica", "Leggi di Mendel, ereditarietà"),
        ("bio_ge_molecolare", "Genetica molecolare", "DNA, RNA, trascrizione, traduzione"),
        ("bio_ge_umana", "Genetica umana", "Cromosomi, malattie ereditarie, test genetici"),
        ("bio_ge_ingegneria", "Ingegneria genetica", "CRISPR, OGM, terapia genica"),
    ]),
    ("bio_microbiologia", [
        ("bio_mi_batteri", "Batteriologia", "Struttura, metabolismo, patogenicità"),
        ("bio_mi_virologia", "Virologia", "Struttura, replicazione, vaccini"),
        ("bio_mi_micologia", "Micologia", "Funghi, lieviti, muffe"),
        ("bio_mi_parassitologia", "Parassitologia", "Protozoi, elminti, vettori"),
    ]),
    ("bio_ecologia", [
        ("bio_ec_popolazioni", "Ecologia delle popolazioni", "Dinamiche, crescita, regolazione"),
        ("bio_ec_comunita", "Ecologia delle comunità", "Competizione, predazione, simbiosi"),
        ("bio_ec_ecosistemi", "Ecologia degli ecosistemi", "Flussi di energia, cicli della materia"),
        ("bio_ec_conservazione", "Biologia della conservazione", "Specie a rischio, habitat, ripristino"),
    ]),
    ("bio_evolution", [
        ("bio_ev_darwin", "Teoria darwiniana", "Selezione naturale, adattamento"),
        ("bio_ev_speciazione", "Speciazione", "Modelli, isolamento, ibridazione"),
        ("bio_ev_filogenesi", "Filogenesi", "Alberi filogenetici, omologia, convergenza"),
        ("bio_ev_molecolare", "Evoluzione molecolare", "Orologi molecolari, genomi"),
    ]),
    ("bio_cellulare", [
        ("bio_ce_struttura", "Struttura cellulare", "Membrana, organelli, citoscheletro"),
        ("bio_ce_divisione", "Divisione cellulare", "Mitosi, meiosi, ciclo cellulare"),
        ("bio_ce_segnali", "Segnalazione cellulare", "Recettori, vie di trasduzione"),
    ]),
    ("bio_molecolare", [
        ("bio_mo_dna", "Struttura e funzione del DNA", "Doppia elica, replicazione"),
        ("bio_mo_rna", "RNA", "Tipi, funzioni, splicing"),
        ("bio_mo_proteine", "Sintesi proteica", "Ribosomi, codice genetico, modificazioni"),
    ]),
    ("bio_fisiologia", [
        ("bio_fi_apparati", "Apparati e sistemi", "Circolatorio, respiratorio, nervoso"),
        ("bio_fi_ormoni", "Sistema endocrino", "Ormoni, ghiandole, feedback"),
        ("bio_fi_immunitario", "Sistema immunitario", "Innata, adattativa, vaccini"),
    ]),
    ("bio_antropologia", [
        ("bio_an_ominidi", "Evoluzione degli ominidi", "Australopitechi, Homo, Neanderthal"),
        ("bio_an_biodiversita", "Biodiversità umana", "Variazione genetica, adattamenti"),
        ("bio_an_forense", "Antropologia forense", "Identificazione, osteologia"),
    ]),

    # === MEDICINA E SALUTE ===
    ("med_anatomia", [
        ("med_an_apparato", "Apparato scheletrico", "Ossa, articolazioni, muscoli"),
        ("med_an_nervoso", "Sistema nervoso", "Encefalo, midollo, nervi periferici"),
        ("med_an_cardiovascolare", "Sistema cardiovascolare", "Cuore, vasi, circolazione"),
        ("med_an_respiratorio", "Sistema respiratorio", "Vie aeree, polmoni, meccanica"),
        ("med_an_digerente", "Sistema digerente", "Tratto gastrointestinale, fegato, pancreas"),
    ]),
    ("med_fisiologia", [
        ("med_fi_cardio", "Fisiologia cardiovascolare", "Elettrocardiogramma, pressione, flusso"),
        ("med_fi_respiratoria", "Fisiologia respiratoria", "Ventilazione, scambi gassosi"),
        ("med_fi_renale", "Fisiologia renale", "Filtrazione, riassorbimento, equilibrio acido-base"),
        ("med_fi_neuro", "Neurofisiologia", "Potenziali d'azione, sinapsi, plasticità"),
    ]),
    ("med_patologia", [
        ("med_pa_generale", "Patologia generale", "Infiammazione, necrosi, iperplasia"),
        ("med_pa_oncologia", "Oncologia", "Carcinogenesi, tipi di tumore, terapie"),
        ("med_pa_cardiovascolari", "Malattie cardiovascolari", "Ictus, infarto, ipertensione"),
        ("med_pa_infettive", "Malattie infettive", "Batteriche, virali, fungine, parassitarie"),
    ]),
    ("med_farmacologia", [
        ("med_fa_farmacocinetica", "Farmacocinetica", "Assorbimento, distribuzione, metabolismo, eliminazione"),
        ("med_fa_farmacodinamica", "Farmacodinamica", "Recettori, agonisti, antagonisti"),
        ("med_fa_classi", "Classi farmacologiche", "Antibiotici, antinfiammatori, anticoagulanti"),
        ("med_fa_sviluppo", "Sviluppo farmaceutico", "Fasi cliniche, registrazione, farmacovigilanza"),
    ]),
    ("med_chirurgia", [
        ("med_ch_generale", "Chirurgia generale", "Principi, asepsi, tecniche base"),
        ("med_ch_specialita", "Specialità chirurgiche", "Cardiochirurgia, neurochirurgia, ortopedia"),
        ("med_ch_mininvasiva", "Chirurgia mininvasiva", "Laparoscopia, robotica, endoscopia"),
    ]),
    ("med_psichiatria", [
        ("med_ps_disturbi", "Disturbi psichiatrici", "Depressione, ansia, psicosi, bipolarismo"),
        ("med_ps_terapie", "Psicoterapie", "CBT, psicoanalisi, sistemica"),
        ("med_ps_farmacologiche", "Terapie farmacologiche", "Antidepressivi, antipsicotici, stabilizzatori"),
    ]),
    ("med_pediatria", [
        ("med_pe_sviluppo", "Sviluppo infantile", "Crescita, sviluppo psicomotorio"),
        ("med_pe_vaccini", "Vaccinazioni pediatriche", "Calendario, sicurezza, immunità"),
        ("med_pe_patologie", "Patologie pediatriche", "Malattie comuni, rare, croniche"),
    ]),
    ("med_prevenzione", [
        ("med_pr_igiene", "Igiene e sanità pubblica", "Epidemiologia, controllo delle malattie"),
        ("med_pr_vaccini", "Vaccinologia", "Tipi, efficacia, coperture"),
        ("med_pr_stili", "Stili di vita", "Alimentazione, attività fisica, sonno"),
    ]),
    ("med_nutrizione", [
        ("med_nu_macro", "Macronutrienti", "Carboidrati, proteine, lipidi"),
        ("med_nu_micro", "Micronutrienti", "Vitamine, minerali, oligoelementi"),
        ("med_nu_patologie", "Patologie nutrizionali", "Obesità, malnutrizione, disturbi alimentari"),
    ]),
    ("med_emergenza", [
        ("med_em_triage", "Triage", "Classificazione, priorità, codici"),
        ("med_em_rianimazione", "Rianimazione", "BLS, ACLS, defibrillazione"),
        ("med_em_trauma", "Traumatologia d'emergenza", "Politraumi, emorragie, shock"),
    ]),
]

for parent, sottoaree in sottoaree_data_4:
    for s_id, s_label, s_desc in sottoaree:
        add_node(s_id, s_label, "sottoarea", parent, s_desc)

sottoarea_count = len([n for n in nodes.values() if n['type']=='sottoarea'])
print(f"Sottoaree inserite finora: {sottoarea_count}")

# SOTTOAREE - parte 5 (Astronomia, Scienze Terra, Ambiente, Informatica, IA, Ingegneria, Tecnologia, Economia, Finanza, Diritto)

sottoaree_data_5 = [
    # === ASTRONOMIA ===
    ("astro_sistema_solare", [
        ("ast_so_pianeti", "Pianeti", "Terrestri, giganti gassosi, ghiacciati"),
        ("ast_so_sole", "Sole", "Struttura, attività, cicli"),
        ("ast_so_luna", "Luna", "Fasi, maree, esplorazione"),
        ("ast_so_piccoli", "Corpi minori", "Asteroidi, comete, meteoriti"),
    ]),
    ("astro_stelle", [
        ("ast_st_nascita", "Nascita stellare", "Nebulose, protostelle, disco protoplanetario"),
        ("ast_st_vita", "Vita delle stelle", "Sequenza principale, fusione, equilibrio"),
        ("ast_st_morte", "Morte stellare", "Giganti rosse, supernove, nane bianche"),
        ("ast_st_classificazione", "Classificazione stellare", "Diagramma HR, spettri, luminosità"),
    ]),
    ("astro_galassie", [
        ("ast_ga_tipi", "Tipi di galassie", "Ellittiche, spirali, irregolari"),
        ("ast_ga_struttura", "Struttura galattica", "Nucleo, bracci, alone, materia oscura"),
        ("ast_ga_cosmologia", "Cosmologia osservativa", "Espansione, fondo cosmico, big bang"),
    ]),
    ("astro_osservazione", [
        ("ast_os_telescopi", "Telescopi", "Rifrazione, riflessione, radio, spazio"),
        ("ast_os_fotometria", "Fotometria e spettroscopia", "Luce, spettri, redshift"),
        ("ast_os_cataloghi", "Cataloghi celesti", "Messier, NGC, SAO, coordinate"),
    ]),
    ("astro_esopianeti", [
        ("ast_es_metodi", "Metodi di rivelazione", "Transito, velocità radiale, microlensing"),
        ("ast_es_abitabilita", "Zona abitabile", "Definizione, criteri, esopianeti confermati"),
        ("ast_es_biosign", "Biosignatures", "Atmosfere, molecole, ricerca di vita"),
    ]),
    ("astro_astronautica", [
        ("ast_as_propulsione", "Propulsione spaziale", "Razzi, motori ionici, vele solari"),
        ("ast_as_orbitali", "Meccanica orbitale", "Orbite, manovre, lagrangiani"),
        ("ast_as_esplorazione", "Esplorazione umana", "Apollo, ISS, Marte, colonizzazione"),
    ]),

    # === SCIENZE DELLA TERRA ===
    ("st_geologia", [
        ("st_ge_rocce", "Rocce", "Ignee, sedimentarie, metamorfiche"),
        ("st_ge_minerali", "Minerali", "Classificazione, proprietà, cristallografia"),
        ("st_ge_tettonica", "Tettonica delle placche", "Placche, margini, deriva"),
        ("st_ge_stratigrafia", "Stratigrafia", "Principi, scale geologiche, datazione"),
    ]),
    ("st_vulcanologia", [
        ("st_vu_tipologie", "Tipi di vulcani", "A scudo, a cono, caldere, sottomarini"),
        ("st_vu_eruzioni", "Eruzioni", "Esplosività, colate, cenere"),
        ("st_vu_monitoraggio", "Monitoraggio", "Sismografi, gas, deformazioni"),
    ]),
    ("st_sismologia", [
        ("st_si_terremoti", "Terremoti", "Faglie, magnitudo, intensità"),
        ("st_si_ondes", "Onde sismiche", "P, S, superficiali, tomografia"),
        ("st_si_rischio", "Rischio sismico", "Pericolosità, vulnerabilità, esposizione"),
    ]),
    ("st_paleontologia", [
        ("st_pa_fossili", "Fossili", "Formazione, tafonomia, classificazione"),
        ("st_pa_dinosauri", "Dinosauri", "Evoluzione, estinzione, scoperte"),
        ("st_pa_uomo", "Evoluzione umana", "Australopitechi, Homo, utensili"),
    ]),
    ("st_oceanografia", [
        ("st_oc_correnti", "Correnti oceaniche", "Termoaline, superficiali, upwelling"),
        ("st_oc_maree", "Maree", "Forze, tipi, effetti costieri"),
        ("st_oc_fondali", "Fondali marini", "Dorsali, fossa, sedimenti"),
    ]),
    ("st_climatologia", [
        ("st_cl_fattori", "Fattori climatici", "Latitudine, altitudine, correnti"),
        ("st_cl_zone", "Zone climatiche", "Köppen, biomi, distribuzione"),
        ("st_cl_paleoclima", "Paleoclimatologia", "Ere glaciali, proxy, modelli"),
    ]),

    # === AMBIENTE ED ECOLOGIA ===
    ("amb_ecosistemi", [
        ("am_ec_forestali", "Ecosistemi forestali", "Boschi, foreste pluviali, taiga"),
        ("am_ec_acquatici", "Ecosistemi acquatici", "Dolci, salmastri, marini"),
        ("am_ec_agricoli", "Ecosistemi agricoli", "Colture, pascoli, agroecosistemi"),
        ("am_ec_urbane", "Ecosistemi urbani", "Città, infrastrutture verdi"),
    ]),
    ("amb_biodiversita", [
        ("am_bi_genetica", "Diversità genetica", "Variazione all'interno delle specie"),
        ("am_bi_specie", "Diversità specifica", "Ricchezza di specie, indici"),
        ("am_bi_ecosistemi", "Diversità ecosistemica", "Biomi, habitat, paesaggi"),
        ("am_bi_estinzione", "Estinzione", "Cause, tassi, specie a rischio"),
    ]),
    ("amb_cambiamento_climatico", [
        ("am_cc_gas", "Gas serra", "CO2, metano, N2O, effetto serra"),
        ("am_cc_impatti", "Impatti", "Temperature, eventi estremi, innalzamento mari"),
        ("am_cc_mitigazione", "Mitigazione", "Riduzione emissioni, carbon capture"),
        ("am_cc_adattamento", "Adattamento", "Infrastrutture, agricoltura, pianificazione"),
    ]),
    ("amb_inquinamento", [
        ("am_in_aria", "Inquinamento atmosferico", "PM, NOx, SO2, ozono"),
        ("am_in_acqua", "Inquinamento idrico", "Sostanze chimiche, plastiche, eutrofizzazione"),
        ("am_in_suolo", "Inquinamento del suolo", "Metalli pesanti, pesticidi, bonifiche"),
        ("am_in_rumore", "Inquinamento acustico", "Fonti, effetti, normative"),
    ]),
    ("amb_sostenibilita", [
        ("am_so_agenda", "Agenda 2030", "SDGs, indicatori, progressi"),
        ("am_so_economia", "Economia circolare", "Riuso, riciclo, upcycling"),
        ("am_so_edilizia", "Edilizia sostenibile", "Bioedilizia, certificazioni, efficienza"),
    ]),
    ("amb_energie_rinnovabili", [
        ("am_en_solare", "Solare", "Fotovoltaico, termico, concentrazione"),
        ("am_en_eolico", "Eolico", "Onshore, offshore, mini-eolico"),
        ("am_en_idro", "Idroelettrico", "Grandi dighe, mini-idro, pompaggio"),
        ("am_en_geotermia", "Geotermia", "Alta, media, bassa entalpia"),
    ]),

    # === INFORMATICA ===
    ("info_algoritmi", [
        ("in_al_complessita", "Complessità computazionale", "O grande, classi P, NP"),
        ("in_al_ordinamento", "Algoritmi di ordinamento", "QuickSort, MergeSort, HeapSort"),
        ("in_al_grafi", "Algoritmi su grafi", "BFS, DFS, Dijkstra, A*"),
        ("in_al_ricerca", "Algoritmi di ricerca", "Binaria, hash, indicizzazione"),
    ]),
    ("info_programmazione", [
        ("in_pr_paradigmi", "Paradigmi", "Imperativo, funzionale, OOP, logico"),
        ("in_pr_linguaggi", "Linguaggi", "Python, C, Java, JavaScript, Rust"),
        ("in_pr_strutture", "Strutture dati", "Array, liste, alberi, grafi, hash map"),
        ("in_pr_debugging", "Debugging", "Testing, profiling, refactoring"),
    ]),
    ("info_software", [
        ("in_sw_ciclo", "Ciclo di vita", "Waterfall, agile, DevOps"),
        ("in_sw_design", "Design pattern", "MVC, singleton, factory, observer"),
        ("in_sw_qualita", "Qualità del software", "Metriche, review, standard"),
    ]),
    ("info_architetture", [
        ("in_ar_cpu", "Processori", "Architettura, pipeline, cache, multicore"),
        ("in_ar_memoria", "Memoria", "RAM, ROM, SSD, gerarchie"),
        ("in_ar_bus", "Bus e interconnessioni", "PCIe, USB, Thunderbolt"),
    ]),
    ("info_sistemi_operativi", [
        ("in_so_processi", "Gestione processi", "Scheduling, concorrenza, deadlock"),
        ("in_so_memoria", "Gestione memoria", "Paging, segmentazione, virtual memory"),
        ("in_so_filesystem", "File system", "NTFS, ext4, APFS, permessi"),
    ]),
    ("info_reti", [
        ("in_re_tcpip", "Stack TCP/IP", "HTTP, DNS, DHCP, routing"),
        ("in_re_sicurezza", "Sicurezza di rete", "Firewall, VPN, IDS"),
        ("in_re_wireless", "Reti wireless", "WiFi, 5G, Bluetooth, LoRa"),
    ]),
    ("info_sicurezza_informatica", [
        ("in_si_crittografia", "Crittografia", "Simmetrica, asimmetrica, hash, TLS"),
        ("in_si_malware", "Malware", "Virus, worm, ransomware, trojan"),
        ("in_si_pentest", "Penetration testing", "Vulnerability assessment, ethical hacking"),
    ]),
    ("info_basi_dati", [
        ("in_bd_relazionali", "Database relazionali", "SQL, normalizzazione, ACID"),
        ("in_bd_nosql", "NoSQL", "Documentali, key-value, graph, column"),
        ("in_bd_ottimizzazione", "Ottimizzazione", "Indici, query plan, sharding"),
    ]),
    ("info_grafica", [
        ("in_gr_rendering", "Rendering", "Ray tracing, rasterizzazione, shaders"),
        ("in_gr_vr", "Realtà virtuale e aumentata", "Headset, tracking, interazione"),
        ("in_gr_animazione", "Animazione", "Rigging, keyframe, motion capture"),
    ]),
    ("info_storia", [
        ("in_hi_generazioni", "Generazioni di computer", "Valvole, transistor, circuiti integrati"),
        ("in_hi_internet", "Storia di Internet", "ARPANET, WWW, social media"),
        ("in_hi_pionieri", "Pionieri", "Turing, von Neumann, Hopper"),
    ]),

    # === INTELLIGENZA ARTIFICIALE ===
    ("ia_apprendimento", [
        ("ia_ap_supervisionato", "Apprendimento supervisionato", "Classificazione, regressione"),
        ("ia_ap_non_supervisionato", "Apprendimento non supervisionato", "Clustering, riduzione dimensionalità"),
        ("ia_ap_rinforzo", "Apprendimento per rinforzo", "Agenti, reward, policy"),
        ("ia_ap_valutazione", "Valutazione modelli", "Accuracy, precision, recall, F1, cross-validation"),
    ]),
    ("ia_deep_learning", [
        ("ia_dl_reti", "Reti neurali", "Perceptron, MLP, backpropagation"),
        ("ia_dl_cnn", "CNN", "Convoluzioni, pooling, transfer learning"),
        ("ia_dl_rnn", "RNN e LSTM", "Sequenze, memoria a lungo termine"),
        ("ia_dl_transformer", "Transformer", "Attention, BERT, GPT"),
    ]),
    ("ia_nlp", [
        ("ia_nl_token", "Tokenizzazione e parsing", "POS, dipendenze, NER"),
        ("ia_nl_semantica", "Semantica computazionale", "Word embeddings, sentiment, topic modeling"),
        ("ia_nl_generazione", "Generazione di testo", "Language models, prompting, fine-tuning"),
        ("ia_nl_traduzione", "Traduzione automatica", "MT, NMT, qualità"),
    ]),
    ("ia_visione", [
        ("ia_vi_riconoscimento", "Riconoscimento oggetti", "YOLO, R-CNN, segmentazione"),
        ("ia_vi_face", "Face recognition", "Detezione, embeddings, privacy"),
        ("ia_vi_medica", "Visione artificiale medica", "Diagnostica, imaging, radiologia"),
    ]),
    ("ia_ragionamento", [
        ("ia_ra_esperti", "Sistemi esperti", "Knowledge base, inference engine"),
        ("ia_ra_pianificazione", "Pianificazione", "STRIPS, PDDL, robotica"),
        ("ia_ra_kr", "Rappresentazione della conoscenza", "Ontologie, grafi, logica"),
    ]),
    ("ia_robotica", [
        ("ia_ro_percezione", "Percezione robotica", "Sensori, LIDAR, visione"),
        ("ia_ro_controllo", "Controllo", "Cinematica, dinamica, PID"),
        ("ia_ro_uomo", "Interazione uomo-robot", "Collaborativi, sicurezza, etica"),
    ]),
    ("ia_etica_ia", [
        ("ia_et_bias", "Bias algoritmici", "Dati, modelli, discriminazione"),
        ("ia_et_trasparenza", "Trasparenza", "Explainability, interpretability"),
        ("ia_et_privacy", "Privacy nell'IA", "Differenziale, federated learning"),
    ]),
    ("ia_generativa", [
        ("ia_ge_testo", "Generazione testo", "LLM, chatbot, creative writing"),
        ("ia_ge_immagini", "Generazione immagini", "GAN, diffusion models, DALL-E"),
        ("ia_ge_audio", "Generazione audio", "TTS, music generation, voice cloning"),
    ]),
    ("ia_multimodale", [
        ("ia_mu_fusione", "Fusione multimodale", "Early, late, joint fusion"),
        ("ia_mu_applicazioni", "Applicazioni", "Captioning, VQA, retrieval"),
    ]),
    ("ia_storia", [
        ("ia_hi_simbolica", "IA simbolica", "Logic-based, expert systems, GOFAI"),
        ("ia_hi_connessionista", "Connessionismo", "Perceptron, reti neurali, deep learning"),
        ("ia_hi_fondazionali", "Modelli fondazionali", "GPT, LLaMA, multimodali"),
    ]),

    # === INGEGNERIA ===
    ("ing_civile", [
        ("ing_ci_strutture", "Strutture", "Calcolo, cemento armato, acciaio"),
        ("ing_ci_geotecnica", "Geotecnica", "Terreni, fondazioni, sottosuolo"),
        ("ing_ci_idraulica", "Idraulica", "Acque, fognature, difese idrauliche"),
    ]),
    ("ing_meccanica", [
        ("ing_me_termomeccanica", "Termomeccanica", "Cicli termici, motori, turbomacchine"),
        ("ing_me_disegno", "Disegno meccanico", "CAD, CAM, tolleranze"),
        ("ing_me_materiali", "Tecnologia meccanica", "Lavorazioni, materiali, affaticamento"),
    ]),
    ("ing_elettrica", [
        ("ing_el_macchine", "Macchine elettriche", "Trasformatori, motori, generatori"),
        ("ing_el_trasmissione", "Trasmissione", "Linee, cabine, smart grid"),
        ("ing_el_elettronica", "Elettronica di potenza", "Convertitori, inverter, PWM"),
    ]),
    ("ing_elettronica", [
        ("ing_et_analogica", "Elettronica analogica", "Amplificatori, filtri, oscillatori"),
        ("ing_et_digitale", "Elettronica digitale", "Porte logiche, FPGA, microcontrollori"),
        ("ing_et_comunicazioni", "Elettronica delle comunicazioni", "Modulazione, demodulazione, antenne"),
    ]),
    ("ing_informatica", [
        ("ing_in_embedded", "Sistemi embedded", "RTOS, firmware, IoT"),
        ("ing_in_reti", "Reti di calcolatori", "Progettazione, sicurezza, prestazioni"),
        ("ing_in_software", "Ingegneria del software", "Requisiti, architettura, testing"),
    ]),
    ("ing_chimica", [
        ("ing_ch_reattori", "Reattori chimici", "Progettazione, cinetica, sicurezza"),
        ("ing_ch_separazione", "Operazioni di separazione", "Distillazione, estrazione, cristallizzazione"),
        ("ing_ch_processi", "Controllo di processo", "Automazione, PLC, SCADA"),
    ]),
    ("ing_aerospaziale", [
        ("ing_ae_aerodinamica", "Aerodinamica", "Flusso, resistenza, portanza"),
        ("ing_ae_propulsione", "Propulsione", "Turboreattori, propellenti, ioni"),
        ("ing_ae_strutture", "Strutture aerospaziali", "Materiali compositi, progettazione"),
    ]),
    ("ing_biomedica", [
        ("ing_bi_dispositivi", "Dispositivi medici", "Progettazione, normativa, qualità"),
        ("ing_bi_segnali", "Elaborazione segnali biomedici", "ECG, EEG, imaging"),
        ("ing_bi_biomeccanica", "Biomeccanica", "Protesi, ortesi, movimento umano"),
    ]),
    ("ing_ambientale", [
        ("ing_am_trattamento", "Trattamento rifiuti", "Riciclo, compostaggio, termovalorizzazione"),
        ("ing_am_acque", "Gestione acque", "Potabilizzazione, depurazione, reti"),
        ("ing_am_monitoraggio", "Monitoraggio ambientale", "Sensori, modelli, reporting"),
    ]),
    ("ing_gestionale", [
        ("ing_ge_logistica", "Logistica", "Supply chain, magazzino, trasporti"),
        ("ing_ge_ottimizzazione", "Ottimizzazione", "Ricerca operativa, simulazione"),
        ("ing_ge_progetti", "Gestione progetti", "PMI, PMBOK, agile"),
    ]),

    # === TECNOLOGIA ===
    ("tec_telecomunicazioni", [
        ("te_te_5g", "Reti 5G", "Architettura, frequenze, applicazioni"),
        ("te_te_fibra", "Fibra ottica", "FTTH, FTTC, tecnologie"),
        ("te_te_satellitare", "Comunicazioni satellitari", "LEO, GEO, banda larga"),
    ]),
    ("tec_nanotecnologie", [
        ("te_na_materiali", "Nanomateriali", "Grafene, nanotubi, quantum dots"),
        ("te_na_medicina", "Nanomedicina", "Drug delivery, imaging, terapia"),
        ("te_na_elettronica", "Nanoelettronica", "Transistor molecolari, memristori"),
    ]),
    ("tec_biotecnologie", [
        ("te_bi_farmaceutica", "Biotecnologie farmaceutiche", "Proteine ricombinanti, vaccini"),
        ("te_bi_agricole", "Biotecnologie agricole", "OGM, marker assistiti, colture"),
        ("te_bi_industriali", "Biotecnologie industriali", "Biocatalisi, bioplastica"),
    ]),
    ("tec_materiali_avanzati", [
        ("te_ma_compositi", "Materiali compositi", "Fibra di carbonio, ceramici"),
        ("te_ma_memoria", "Materiali a memoria di forma", "Nitinol, applicazioni"),
        ("te_ma_superconduttori", "Superconduttori", "Alte temperature, applicazioni"),
    ]),
    ("tec_stampa_3d", [
        ("te_3d_tecniche", "Tecniche", "FDM, SLA, SLS, DMLS"),
        ("te_3d_materiali", "Materiali", "PLA, ABS, resine, metalli"),
        ("te_3d_applicazioni", "Applicazioni", "Prototipazione, medicina, edilizia"),
    ]),
    ("tec_quantistica", [
        ("te_qu_computer", "Computer quantistici", "Qubit, porte, algoritmi"),
        ("te_qu_comunicazione", "Comunicazione quantistica", "Teletrasporto, crittografia"),
        ("te_qu_sensori", "Sensori quantistici", "Metrologia, imaging, navigazione"),
    ]),
    ("tec_industria_4", [
        ("te_i4_iot", "Internet delle cose industriale", "Sensori, connettività, edge"),
        ("te_i4_digital_twin", "Digital twin", "Gemelli digitali, simulazione"),
        ("te_i4_manutenzione", "Manutenzione predittiva", "AI, sensori, prognostica"),
    ]),
    ("tec_wearable", [
        ("te_we_salute", "Wearable per la salute", "Smartwatch, ECG continuo, glucosio"),
        ("te_we_sport", "Wearable sportivi", "GPS, accelerometri, analisi performance"),
        ("te_we_ar", "Realtà aumentata indossabile", "Smart glasses, HUD, applicazioni"),
    ]),
    ("tec_droni", [
        ("te_dr_tipi", "Tipi di droni", "Multirotore, fixed-wing, ibridi"),
        ("te_dr_applicazioni", "Applicazioni", "Agricoltura, ispezione, consegne"),
        ("te_dr_normativa", "Normativa", "ENAC, regole di volo, privacy"),
    ]),
    ("tec_blocchi", [
        ("te_bl_bitcoin", "Bitcoin", "Protocollo, mining, wallet"),
        ("te_bl_ethereum", "Ethereum", "Smart contract, DeFi, NFT"),
        ("te_bl_applicazioni", "Applicazioni blockchain", "Supply chain, identità, voting"),
    ]),

    # === ECONOMIA ===
    ("eco_micro", [
        ("ec_mi_domanda", "Domanda e offerta", "Curve, equilibrio, elasticità"),
        ("ec_mi_consumatore", "Teoria del consumatore", "Utilità, preferenze, vincolo di bilancio"),
        ("ec_mi_impresa", "Teoria dell'impresa", "Costi, ricavi, profitto, mercati"),
        ("ec_mi_concorrenza", "Concorrenza", "Perfetta, monopolistica, oligopolio, monopolio"),
    ]),
    ("eco_macro", [
        ("ec_ma_pil", "PIL e contabilità nazionale", "Definizione, metodi, limiti"),
        ("ec_ma_inflazione", "Inflazione", "Cause, misurazione, effetti"),
        ("ec_ma_disoccupazione", "Disoccupazione", "Tipi, cause, politiche"),
        ("ec_ma_politiche", "Politiche macroeconomiche", "Fiscale, monetaria, cambio"),
    ]),
    ("eco_storia", [
        ("ec_hi_mercantilismo", "Mercantilismo", "Accumulazione, colonie, bilancia commerciale"),
        ("ec_hi_industriale", "Rivoluzione industriale", "Capitalismo, fabbrica, proletariato"),
        ("ec_hi_contemporanea", "Economia contemporanea", "Globalizzazione, crisi, digital economy"),
    ]),
    ("eco_sviluppo", [
        ("ec_sv_poverta", "Povertà", "Misure, cause, riduzione"),
        ("ec_sv_disuguaglianza", "Disuguaglianza", "Gini, Palma, Kuznets"),
        ("ec_sv_sostenibile", "Sviluppo sostenibile", "Pilastro economico, sociale, ambientale"),
    ]),
    ("eco_internazionale", [
        ("ec_in_commercio", "Commercio internazionale", "Vantaggi comparati, barriere, WTO"),
        ("ec_in_cambi", "Tassi di cambio", "Fissi, fluttuanti, parità"),
        ("ec_in_bilancia", "Bilancia dei pagamenti", "Conto corrente, capitale, riserve"),
    ]),
    ("eco_lavoro", [
        ("ec_la_mercato", "Mercato del lavoro", "Domanda, offerta, salario"),
        ("ec_la_disoccupazione", "Disoccupazione", "Frizionale, strutturale, ciclica"),
        ("ec_la_politiche", "Politiche attive", "Formazione, sussidi, incentivi"),
    ]),
    ("eco_pubblica", [
        ("ec_pu_spesa", "Spesa pubblica", "Tipi, efficienza, debito"),
        ("ec_pu_tasse", "Tassazione", "Dirette, indirette, progressività"),
        ("ec_pu_beni", "Beni pubblici", "Definizione, free rider, provision"),
    ]),
    ("eco_ambientale", [
        ("ec_am_esternalita", "Esternalità", "Negative, positive, internalizzazione"),
        ("ec_am_valutazione", "Valutazione ambientale", "Costi, benefici, contingent valuation"),
        ("ec_am_mercati", "Mercati delle emissioni", "Cap and trade, carbon tax"),
    ]),
    ("eco_comportamentale", [
        ("ec_co_bias", "Bias cognitivi", "Ancoraggio, conferma, iperbolico"),
        ("ec_co_prospect", "Prospect theory", "Perdite, guadagni, aversione"),
        ("ec_co_nudge", "Nudge", "Scelte architetturali, default"),
    ]),
    ("eco_monetaria", [
        ("ec_mo_banche", "Banche centrali", "Mandato, strumenti, indipendenza"),
        ("ec_mo_politiche", "Politiche monetarie", "Tassi, QE, forward guidance"),
        ("ec_mo_crises", "Crisi finanziarie", "Bolle, panico, contagio"),
    ]),

    # === FINANZA ===
    ("fin_mercati", [
        ("fi_me_azionari", "Mercati azionari", "Borse, indici, quotazioni"),
        ("fi_me_obbligazionari", "Mercati obbligazionari", "Titoli di Stato, corporate bond"),
        ("fi_me_derivati", "Derivati", "Future, option, swap"),
        ("fi_me_fondi", "Fondi comuni", "Azionari, obbligazionari, bilanciati"),
    ]),
    ("fin_banche", [
        ("fi_ba_intermediazione", "Intermediazione", "Raccolta, erogazione, spread"),
        ("fi_ba_regolamentazione", "Regolamentazione", "Basilea, vigilanza, stress test"),
        ("fi_ba_digitale", "Banca digitale", "Fintech, open banking, neobanche"),
    ]),
    ("fin_investimenti", [
        ("fi_in_portafogli", "Teoria dei portafogli", "Diversificazione, frontiera efficiente"),
        ("fi_in_valutazione", "Valutazione titoli", "DCF, multipli, analisi fondamentale"),
        ("fi_in_tecniche", "Analisi tecnica", "Trend, supporti, indicatori"),
    ]),
    ("fin_corporate", [
        ("fi_co_valutazione", "Valutazione aziendale", "DCF, multipli, asset-based"),
        ("fi_co_struttura", "Struttura del capitale", "Debito, equity, WACC"),
        ("fi_co_ma", "M&A", "Fusioni, acquisizioni, sinergie"),
    ]),
    ("fin_assicurazioni", [
        ("fi_as_rischio", "Gestione del rischio", "Identificazione, quantificazione, transfer"),
        ("fi_as_prodotti", "Prodotti assicurativi", "Vita, danni, RC, salute"),
        ("fi_as_attuariale", "Matematica attuariale", "Premi, riserve, mortalità"),
    ]),
    ("fin_fintech", [
        ("fi_ft_pagamenti", "Pagamenti digitali", "Wallet, P2P, contactless"),
        ("fi_ft_robo", "Robo-advisory", "Algoritmi, allocazione, costi"),
        ("fi_ft_crowdfunding", "Crowdfunding", "Equity, lending, reward"),
    ]),
    ("fin_contabilita", [
        ("fi_co_principi", "Principi contabili", "IFRS, OIC, bilancio"),
        ("fi_co_analisi", "Analisi di bilancio", "Indici, flussi, reporting"),
        ("fi_co_revisione", "Revisione contabile", "Audit, risk, compliance"),
    ]),
    ("fin_tassazione", [
        ("fi_ta_dirette", "Imposte dirette", "IRPEF, IRES, patrimoniali"),
        ("fi_ta_indirette", "Imposte indirette", "IVA, accise, bollo"),
        ("fi_ta_pianificazione", "Pianificazione fiscale", "Risparmio, elusione, evasione"),
    ]),
    ("fin_cripto", [
        ("fi_cr_bitcoin", "Bitcoin", "Protocollo, halving, store of value"),
        ("fi_cr_ethereum", "Ethereum", "Smart contract, gas, DeFi"),
        ("fi_cr_regolamentazione", "Regolamentazione crypto", "MiCA, exchange, stablecoin"),
    ]),
    ("fin_macro", [
        ("fi_ma_debito", "Debito pubblico", "Sostenibilità, spread, rating"),
        ("fi_ma_bce", "Politiche BCE", "Tassi, QE, TLTRO"),
        ("fi_ma_fiscal", "Politica fiscale", "Deficit, surplus, multiplicatore"),
    ]),

    # === DIRITTO ===
    ("dir_costituzionale", [
        ("di_co_principi", "Principi costituzionali", "Sovranità, libertà, uguaglianza"),
        ("di_co_istituzioni", "Istituzioni", "Parlamento, governo, presidente"),
        ("di_co_diritti", "Diritti fondamentali", "Civili, politici, sociali"),
    ]),
    ("dir_privato", [
        ("di_pr_persone", "Persone e famiglia", "Stato civile, matrimonio, filiazione"),
        ("di_pr_proprieta", "Proprietà e diritti reali", "Possesso, usufrutto, servitù"),
        ("di_pr_contratti", "Contratti", "Obbligazioni, responsabilità, tipologie"),
    ]),
    ("dir_penale", [
        ("di_pe_reati", "Teoria del reato", "Fatto, antigiuridicità, colpevolezza"),
        ("di_pe_sanzioni", "Sanzioni penali", "Pena, misure di sicurezza, alternative"),
        ("di_pe_procedura", "Procedura penale", "Indagini, processo, esecuzione"),
    ]),
    ("dir_amministrativo", [
        ("di_am_atti", "Atti amministrativi", "Tipi, invalidità, ricorsi"),
        ("di_am_beni", "Beni pubblici", "Demanio, patrimonio, disponibilità"),
        ("di_am_servizi", "Servizi pubblici", "Appalti, concessioni, PPP"),
    ]),
    ("dir_lavoro", [
        ("di_la_contratto", "Contratto di lavoro", "Tipi, clausole, risoluzione"),
        ("di_la_sicurezza", "Sicurezza sul lavoro", "D.Lgs. 81/08, responsabilità"),
        ("di_la_sindacale", "Diritto sindacale", "Rappresentanza, contrattazione, sciopero"),
    ]),
    ("dir_commerciale", [
        ("di_co_imprese", "Diritto delle imprese", "Società, fallimento, concordato"),
        ("di_co_concorrenza", "Concorrenza", "Antitrust, abuso, merger"),
        ("di_co_bancario", "Diritto bancario", "Contratti, trasparenza, usura"),
    ]),
    ("dir_internazionale", [
        ("di_in_fonti", "Fonti", "Trattati, consuetudine, principi generali"),
        ("di_in_soggetti", "Soggetti", "Stati, organizzazioni, individui"),
        ("di_in_diritti", "Diritti umani", "Dichiarazioni, convenzioni, corti"),
    ]),
    ("dir_ue", [
        ("di_ue_istituzioni", "Istituzioni UE", "Parlamento, Commissione, Consiglio, Corte"),
        ("di_ue_fonti", "Fonti del diritto UE", "Regolamenti, direttive, decisioni"),
        ("di_ue_mercato", "Mercato interno", "Libera circolazione, concorrenza, stato di diritto"),
    ]),
    ("dir_ambientale", [
        ("di_am_norme", "Normativa ambientale", "Direttive, decreti, regolamenti"),
        ("di_am_valutazione", "Valutazione di impatto", "VIA, VAS, AIA"),
        ("di_am_responsabilita", "Responsabilità ambientale", "Danno, risarcimento, ripristino"),
    ]),
    ("dir_tributario", [
        ("di_tr_imposte", "Imposte", "Dirette, indirette, tasse, contributi"),
        ("di_tr_accertamento", "Accertamento", "Verifica, rettifica, accertamento"),
        ("di_tr_contenzioso", "Contenzioso tributario", "Ricorso, giudice, riscossione"),
    ]),
]

for parent, sottoaree in sottoaree_data_5:
    for s_id, s_label, s_desc in sottoaree:
        add_node(s_id, s_label, "sottoarea", parent, s_desc)

sottoarea_count = len([n for n in nodes.values() if n['type']=='sottoarea'])
print(f"Sottoaree inserite finora: {sottoarea_count}")
