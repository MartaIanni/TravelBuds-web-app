from main_app import app, db
from backend.orm.models import UserORM, TripORM
from werkzeug.security import generate_password_hash

users_data = [
    {
        "uid": 1,
        "name": "Giulio",
        "surname": "Gorcia",
        "username": "giuliogorcia",
        "password": "giulio_gorcia",
        "birthdate": "01/01/1990",
        "gender": "/static/man.jpg",
        "is_coordinator": False
    },
    {
        "uid": 2,
        "name": "Marta",
        "surname": "Iannì",
        "username": "martaianni",
        "password": "marta_ianni",
        "birthdate": "04/01/1996",
        "gender": "/static/woman.jpg",
        "is_coordinator": True
    },
    {
        "uid": 3,
        "name": "Claudio",
        "surname": "Bitto",
        "username": "claudiobitto",
        "password": "claudio_bitto",
        "birthdate": "03/10/2004",
        "gender": "/static/man.jpg",
        "is_coordinator": True
    },
]

trips_data = [
    {
        "destination": "Tokyo",
        "description": "Un viaggio di sette notti a Tokyo, tra modernità e tradizione. Dalle luci di Shinjuku ai templi di Asakusa, passando per Harajuku e Shibuya. Esperienze culinarie, panorami mozzafiato e un'escursione alla scoperta della storia giapponese. Un'avventura tra cultura pop, tecnologia e tradizioni.",
        "subtitle": "Tradizione e futurismo",
        "tour": "Arrivo a Tokyo e trasferimento in hotel, seguito da una passeggiata a Shinjuku tra i vicoli di Omoide Yokocho e Kabukicho, con cena in un izakaya. Il secondo giorno include la visita al tempio Sensō-ji ad Asakusa, e esplorazione di Akihabara. Il terzo giorno si parte per il Meiji Jingu e Harajuku, con shopping a Omotesando e vista panoramica a Shibuya. Il quarto giorno è dedicato all’arte a Ueno, seguito da shopping a Ginza e una cena in un ristorante stellato. Il quinto giorno si esplorano Kamakura o Nikko. Il sesto giorno si visita Odaiba e Tsukiji per sushi fresco. Ultima giornata di relax a Yanaka e panorami dalla Tokyo Tower prima della partenza.",
        "start": "03/04/2025",
        "end": "10/04/2025",
        "max_seats": 10,
        "free_seats": 10,
        "transport_price": 500,
        "stay_price": 2000,
        "act_price": 650,
        "card_img_path": "/static/tokyo.jpg",
        "bg_img_path": "/static/tk_bg.jpg",
        "is_published": True,
        "coord_id": 2  
    },
    {
        "destination": "Le alpi",
        "description": "3 giorni sulle Alpi ci offriranno panorami mozzafiato, con trekking tra vette e laghi cristallini. Si soggiorna in rifugi alpini, esplorando pittoreschi villaggi di montagna e assaporando piatti tipici. Le serate si concludono con passeggiate sotto le stelle in un’atmosfera serena.",
        "subtitle": "Tra Vette e Villaggi",
        "tour": "Il nostro viaggio sulle Alpi inizia con un’arrivo in un rifugio alpino, seguito da un'escursione tra sentieri panoramici, dove si ammirano le vette maestose e i laghi cristallini. Il secondo giorno prevede una giornata di trekking, esplorando i pittoreschi villaggi di montagna, con sosta per assaporare piatti tipici locali come polenta, formaggi e spezzatini. Nel pomeriggio, si prosegue con una passeggiata nei boschi o un'escursione in funivia per panorami mozzafiato. La serata si conclude con una cena tradizionale in rifugio e una passeggiata sotto le stelle. L'ultimo giorno, si visita un altro villaggio e si rilassa prima del rientro.",
        "start": "20/12/2025",
        "end": "23/12/2025",
        "max_seats": 10,
        "free_seats": 8,
        "transport_price": 150,
        "stay_price": 300,
        "act_price": 450,
        "card_img_path": "/static/alps.jpg",
        "bg_img_path": "/static/a_bg.jpg",
        "is_published": True,
        "coord_id": 3  
    },
    {
        "destination": "Scozia",
        "description": "Un weekend in Scozia offre castelli iconici come Edinburgh e Stirling, paesaggi mozzafiato delle Highlands e una visita al Loch Ness. Si esplora Edimburgo con il Royal Mile e si assapora la cucina tipica, immersi nella storia e nelle tradizioni scozzesi.",
        "subtitle": "Tra Castelli e Highlands",
        "tour": "Si inizia con l'esplorazione di Edimburgo, visitando il Royal Mile e il maestoso Edinburgh Castle. Il sabato è dedicato alla visita del Castello di Stirling e dei suoi dintorni storici. La domenica, si esplorano le Highlands, ammirando paesaggi mozzafiato, e si visita il misterioso Loch Ness. Il viaggio si conclude con una tappa in un pub tradizionale, per assaporare la cucina locale, tra piatti come il haggis e il whisky scozzese. Un'avventura tra storia, tradizioni e bellezze naturali che rende questo weekend indimenticabile.",
        "start": "04/04/2025",
        "end": "06/04/2025",
        "max_seats": 10,
        "free_seats": 10,
        "transport_price": 290,
        "stay_price": 400,
        "act_price": 200,
        "card_img_path": "/static/scotland.jpg",
        "bg_img_path": "/static/s_bg.jpg",
        "is_published": True,
        "coord_id": 2  
    },
    {
        "destination": "Bangkok",
        "description": "Un viaggio a Bangkok di 6 giorni offre templi storici come Wat Pho e Wat Arun, mercati vivaci e cucina locale. Si esplorano i quartieri come Khao San Road, si naviga sul fiume Chao Phraya e si visita il mercato galleggiante, completando l'esperienza con un'escursione fuori città.",
        "subtitle": "Città di templi e modernità",
        "tour": "All’arrivo a Bangkok, trasferimento in hotel e visita di Khao San Road, famosa per street food e locali tipici. Il secondo giorno esplorazione dei templi Wat Pho e Wat Arun, seguita da un giro in barca sul fiume Chao Phraya. Il terzo giorno visita ai mercati galleggianti di Damnoen Saduak e Maeklong, dove i treni attraversano le bancarelle. Il quarto giorno si esplorano le rovine di Ayutthaya, l’antica capitale del Siam, e si conclude con una serata in un rooftop bar. Il quinto giorno si visita Chinatown, con le sue spezie e templi, e si prova un massaggio tradizionale. Il sesto giorno è dedicato allo shopping nei grandi centri commerciali e alla zona moderna di Sukhumvit. L’ultimo giorno offre un'ultima passeggiata prima del rientro.",
        "start": "10/03/2025",
        "end": "17/03/2025",
        "max_seats": 10,
        "free_seats": 0,
        "transport_price": 340,
        "stay_price": 840,
        "act_price": 300,
        "card_img_path": "/static/bangkok.jpg",
        "bg_img_path": "/static/bk_bg.jpg",
        "is_published": True,
        "coord_id": 3  
    },
    {
        "destination": "Marocco",
        "description": "Un viaggio in Marocco offre un’immersione tra tradizioni, colori e profumi. Si esplorano le vivaci strade di Marrakech, le montagne dell'Atlante e i villaggi berberi, con un’escursione nel deserto e una visita a Essaouira. Tra souk, cucina locale e notti sotto le stelle, è un'esperienza indimenticabile.",
        "subtitle": "Cuore del Nord Africa",
        "tour": "Arrivo in Marocco con trasferimento in hotel e accoglienza del gruppo. La prima serata si trascorre nella vivace Medina di Marrakech, tra il souk e una cena tradizionale in riad. Il secondo giorno visita alla Moschea Koutoubia, al Palazzo Bahia e ai Giardini Majorelle, seguito da tempo libero in città. Il terzo giorno escursione nel deserto di Agafay, con giro in cammello e pranzo panoramico, poi rientro a Marrakech per un hammam. Il quarto giorno esplorazione dell'Atlante e dei villaggi berberi. L'ultimo giorno si visita Essaouira, con pranzo a base di pesce fresco e rientro a Marrakech per un'ultima serata nella piazza Jemaa el-Fna.",
        "start": "10/03/2026",
        "end": "15/03/2026",
        "max_seats": 10,
        "free_seats": 9,
        "transport_price": 430,
        "stay_price": 600,
        "act_price": 400,
        "card_img_path": "/static/morocco.jpg",
        "bg_img_path": "/static/m_bg.jpg",
        "is_published": True,
        "coord_id": 3  
    },
    {
        "destination": "New York",
        "description": "Immergiti nell’energia unica della città che non dorme mai. Tra la maestosa Statua della Libertà, il fascino di Times Square, il verde di Central Park e il Ponte di Brooklyn, vivrai emozioni indimenticabili. Con un coordinatore esperto, scoprirai sapori globali e panorami mozzafiato, per un’esperienza autentica e ricca di connessioni. New York ti aspetta!",
        "subtitle": "La città che non dorme mai",
        "tour": "All'arrivo a New York, il trasferimento porta all’hotel di Manhattan, dove il coordinatore accoglie il gruppo. La serata inizia con una passeggiata a Times Square e una cena di benvenuto. Il giorno successivo include la visita alla Statua della Libertà, al Memoriale dell’11 Settembre e una serata libera. Il terzo giorno, passeggiata a Central Park e visita al Museo di Storia Naturale, seguita da shopping sulla Fifth Avenue. L’ultimo giorno esplora Brooklyn e attraversa il ponte omonimo, concludendo con una vista panoramica dal tramonto dall’Empire State Building e una cena di arrivederci.",
        "start": "20/01/2026",
        "end": "24/01/2026",
        "max_seats": 10,
        "free_seats": 10,
        "transport_price": 780,
        "stay_price": 1100,
        "act_price": 400,
        "card_img_path": "/static/newyork.jpg",
        "bg_img_path": "/static/ny_bg.jpg",
        "is_published": True,
        "coord_id": 2  
    },
]

#Context manager di Flask per accedere al db
with app.app_context():
    for u in users_data:
        user = UserORM(
            name=u["name"],
            surname=u["surname"],
            username=u["username"],
            password=generate_password_hash(str(u["password"])),
            birthdate=u["birthdate"],
            gender=u["gender"],
            is_coordinator=u["is_coordinator"]
        )
        db.session.add(user)
    db.session.commit()

    for t in trips_data:
        trip = TripORM(**t)
        db.session.add(trip)
    db.session.commit()

print("DB popolato con utenti e viaggi!")