# All site content. Every text that differs by language is written as T("English", "Ελληνικά").
# Names and song titles that stay the same in both languages are plain strings.
# Edit this file, then run build.py to regenerate the site.


def T(en, el):
    return {"en": en, "el": el}


CDN = "https://images.squarespace-cdn.com/content/v1/67b51908870e605d6a390286/"

SITE = {
    "name": "Giorgos Batzios",
    "role": T("Audio, sound engineer – musician", "Ηχολήπτης, sound engineer – μουσικός"),
    "fields": [T("Theater", "Θέατρο"), T("Live", "Live"), T("Studio recording", "Ηχογράφηση"),
               T("Mixing", "Μίξη"), T("Composing", "Σύνθεση")],
    "email": "Gbatzios.work@gmail.com",
    "phone": "+30 6955608021",
    "url": "https://www.giorgosbatzios.com",
}

# Free key from web3forms.com (sent to your email). Empty = the form opens the visitor's email app instead.
FORM_KEY = ""

SOCIAL = [
    ("Instagram", "https://www.instagram.com/giorgos_batzios/"),
    ("YouTube", "https://www.youtube.com/@angvazio"),
    ("Facebook", "https://www.facebook.com/giorgos.batzios.RC/"),
    ("LinkedIn", "https://www.linkedin.com/in/giorgos-batzios-34b12595/"),
    ("Linktree", "https://linktr.ee/gbatzios24b"),
]

IMG = {
    "home1": CDN + "c781f87b-f3be-4f1f-aec6-15f2e97702da/KBB_6031+fixed.jpg",
    "home2": CDN + "af7de53e-baf2-4db4-a420-f50eb8d1fbe3/KBA_7502.jpg",
    "studio": CDN + "8011977b-8665-4ca3-a531-60e90772beab/KBA_7508+fixed.jpg",
    "music": CDN + "a4a5e401-004f-4983-82d6-00835958c902/KBB_6113+fixed+%281%29.jpg",
    "contact": CDN + "7bdd032e-3067-4176-93ad-885e41cf49e5/KBB_5979+fixed+%281%29.jpg",
}

# ---------------------------------------------------------------- Theater
# Roles and venues are translated through these lists.
ROLES = {
    "Sound mixing": "Μίξη ήχου",
    "Lights programming": "Προγραμματισμός φώτων",
    "Qlab AV programming": "Προγραμματισμός AV σε Qlab",
    "Qlab programming": "Προγραμματισμός Qlab",
    "SCS programming": "Προγραμματισμός SCS",
    "Projection mapping": "Projection mapping",
    "Music composing": "Σύνθεση μουσικής",
    "Ableton programming": "Προγραμματισμός Ableton",
    "Run": "Εκτέλεση παράστασης",
}
V_MCF = T("Michael Cacoyannis Foundation", "Ίδρυμα Μιχάλης Κακογιάννης")
V_TOUR = T("Greek tour", "Περιοδεία")
V_CORONET = T("Coronet Theater", "Θέατρο Coronet")

# year, title (Greek, same in both languages), venue/tour, roles, link, poster
THEATER = [
    (2025, "Οι Θεοί του Ολύμπου", T("Christmas Theater", "Christmas Theater"), ["Qlab AV programming", "Run"],
     "https://www.more.com/gr-el/tickets/theater/oi-theoi-tou-olympou-kai-i-gennisi-tou-kosmou/",
     CDN + "8071fca4-a2e6-4ccd-bbdf-714d6ced99cf/cropped-image-%281%29.jpg"),
    (2025, "Ο Γιάννης το Βόδι", V_MCF, ["Sound mixing", "Lights programming", "Run"],
     "https://www.ticketservices.gr/event/mcf-o-giannis-to-voudi/?lang=el",
     CDN + "0efc2f17-76d1-4d38-ba11-e752f3335a55/b_46423_or_Voudi-Poster-1200x900-1.jpg"),
    (2025, "Η Θάλασσα και ο Γέρος", V_TOUR, ["Sound mixing", "Projection mapping", "Run"],
     "https://www.ticketservices.gr/event/i-thalassa-kai-o-geros-2025/?lang=el",
     CDN + "af5f919d-e118-4d09-b33d-9fda26e8e8ce/i-thalassa-kai-o-geros-scaled.jpg"),
    (2025, "Η Ζωή και ο Θάνατος του Καραβέλα", V_MCF, ["Sound mixing", "Lights programming", "Run"],
     "https://www.ticketservices.gr/event/mcf-i-zoi-kai-o-thanatos-tou-karavela/?lang=el",
     CDN + "0226bdc7-4215-411b-a11e-6377ec584eea/b_44809_or_SITE-POST-PHOTO.jpg"),
    (2025, "Αντιγόνη", T("Athens Concert Hall (Megaron)", "Μέγαρο Μουσικής Αθηνών"),
     ["Music composing", "Ableton programming", "Sound mixing", "Run"],
     "https://www.megaron.gr/event/dramatiki-scholi-odeiou-athinon-antigoni/",
     CDN + "6be27aa0-1e2a-48a1-acd0-fde18b067e8e/MAY-25-%CE%91%CE%9D%CE%A4%CE%99%CE%93%CE%9F%CE%9D%CE%97-%CE%A9%CE%94%CE%95%CE%99%CE%9F-2-site.jpg"),
    (2024, "Μπαμπάδες με Ρούμι", V_TOUR, ["Sound mixing", "Lights programming", "Run"],
     "https://www.more.com/gr-el/tickets/theater/aliki/mpampades-me-roumi-3os-xronos/",
     CDN + "6f21702d-66d1-4fee-9e90-8a3035e9a6e0/foto-mpampades.jpg"),
    (2024, "18/9", V_MCF, ["Sound mixing", "Lights programming", "Qlab programming", "Run"],
     "https://www.ticketservices.gr/event/mcf-dekaokto-enatou-2025/?lang=el",
     CDN + "d6f22f4c-e991-4686-884a-7ba785a7926c/b_45977_or_189_jan_site_post_1200x900.jpg"),
    (2024, "Καθαρίστρια", V_CORONET, ["Sound mixing", "Run"],
     "https://www.ticketservices.gr/event/katharistria/?lang=el",
     CDN + "d32a20b0-acec-4b3c-b047-4348a874ed67/b_43303_or_ka8aris.jpg"),
    (2024, "Τα Τελευταία Φεγγάρια", V_CORONET, ["Sound mixing", "Run"],
     "https://www.more.com/gr-el/tickets/theater/ta-teleutaia-feggaria/",
     CDN + "1749a751-bd3d-4314-aeca-14a634ab9e95/1701864077056.jpg"),
    (2024, "Το Μπουφάν της Χάρλεϊ", V_CORONET, ["Sound mixing", "Qlab programming", "Run"],
     "https://www.coronettheater.gr/%CF%80%CE%B1%CF%81%CE%B1%CF%83%CF%84%CE%AC%CF%83%CE%B5%CE%B9%CF%82/%CF%84%CE%BF-%CE%BC%CF%80%CE%BF%CF%85%CF%86%CE%AC%CE%BD-%CF%84%CE%B7%CF%82-%CF%87%CE%AC%CF%81%CE%BB%CE%B5%CF%85",
     CDN + "efb594e1-c544-48a5-b68b-a5faaf029b6b/XARLEY-Poster.jpg"),
    (2023, "Παρασκευή και Δεκατρείς", V_TOUR, ["Sound mixing", "Run"],
     "https://www.athinorama.gr/theatre/performance/paraskeui_kai_13-10076434/",
     CDN + "ab1c6d71-8c9b-442a-aea8-d8faf1bbd8ca/aed6947c-screenshot-1007.jpg"),
    (2023, "Μέχρι Τελικής Πτώσεως", V_TOUR, ["Sound mixing", "SCS programming", "Run"],
     "https://www.athinorama.gr/theatre/performance/mexri_telikis_ptoseos-10078650/",
     CDN + "52ee000d-9d68-4235-8dda-72c0b9a785da/viva500x500.jpg"),
]

# ---------------------------------------------------------------- Studio
STUDIO_CATS = ["Recording", "Mixing", "Production", "Video Edit", "Custom Sound Library"]
CATS_EL = {"Recording": "Ηχογράφηση", "Mixing": "Μίξη", "Production": "Παραγωγή",
           "Video Edit": "Μοντάζ βίντεο", "Custom Sound Library": "Βιβλιοθήκη ήχων"}
R, M, P, V, C = STUDIO_CATS

KONTAKT_NOTE = T(
    "For this song I made a custom Kontakt library using only sounds that my car makes. The entire production is made only with this library and the female vocals on top. This was part of my thesis for my music technology bachelor.",
    "Για αυτό το τραγούδι έφτιαξα μια δική μου βιβλιοθήκη Kontakt χρησιμοποιώντας μόνο ήχους που κάνει το αυτοκίνητό μου. Ολόκληρη η παραγωγή έγινε μόνο με αυτή τη βιβλιοθήκη και τα γυναικεία φωνητικά από πάνω. Ήταν μέρος της πτυχιακής μου εργασίας στο Music Technology.",
)
# title, date, categories, youtube id, note, old squarespace slug
STUDIO = [
    ("Drive Away – Roney K", "2025-06-27", [R, M, P, C], "t2Nq7QioShc", KONTAKT_NOTE, "drive-away-roney-k"),
    ("NowHere – Από το πουθενά (official video clip)", "2023-02-27", [R, M], "xBnGjYXvChY", None, "how-to-use-twitter-blocks-g9mnf-4n8yt-hjwyw"),
    ("784L – Moves", "2022-08-29", [R], "gb8elP0FGQs", None, "fkm3x26rbd8za7age87ehc3k5c6cdz"),
    ("ταφρομι – Δεν Ξέρω", "2022-07-10", [R, M], "fI5x_M13HKM", None, "zel8n7tx9d3ss6t746273jphcj3lkc"),
    ("ταφρομι x Drog – Όσα (Prod. CXLVII)", "2022-03-20", [R], "UxLbrRdIyD0", None, "44ntd7btyfl95y5hz2r3ttypdxlyw4"),
    ("Drog – Ποιός (Official Music Video)", "2022-02-04", [R], "lT4HVZaaLN0", None, "saturday-morning-flow-xw6jw-zjh87"),
    ("ATOM – Hold On (Official Music Video)", "2021-08-01", [R], "gi6gEntZaCY", None, "sunday-morning-flow-wwkfj-zslm6"),
    ("Daniel Se – Fiesta (prod. by Just EvAn) Official Music Video", "2021-06-16", [R], "Q_dpMUxtTck", None, "monday-morning-flow-c5f9z-yhkcy"),
    ("NowHere – Ιδέα (Video Clip)", "2021-04-22", [R, M, P], "c4VO4xzGtzA", None, "it-is-nhsde-3akh4-2d2ch"),
    ("784L – Πρώτα θα πέσεις", "2021-03-05", [R], "qnYJoyOpQMU", None, "xmyfc72rcy8ee96jg9kal6jym63szg"),
    ("HOT STAFF – Happy (funk cover) | Quarantine Edition", "2021-02-15", [M, V], "vj_UaDglAsk", None, "planet-earth-mejnx-d2a8y-gb6mj"),
    ("Κοίτα με – Labrina Manou – Frozen 2 / Show Yourself (Greek)", "2021-01-21", [R, M, V], "79i8t_34P_0", None, "blj2djf2h3ht6tk2jrpmed4ey5tglp"),
    ("Daniel Se – «Καύλα & Μελάνι» Official Music Video (Prod. B-Spot)", "2020-12-27", [R, M, P, V], "f7FGA_umC44", None, "thursday-morning-flow-xay84-r35ma"),
    ("Drog – Η Άγχος (Official Music Video)", "2020-12-06", [R, M, P, V], "u8Z0DK2mTEs", None, "friday-morning-flow-6esng-dyffs"),
    ("Daniel Se – Ατέλεια (Prod. B-Spot) Official Music Video", "2020-11-23", [R, M, P, V], "t7BKH2e_P9s", None, "hosted-with-custom-z9ehj-dwh9x-w8ee8"),
    ("Dream On – Daniel Se ft. Sofía (Prod. B-Spot) Official Music Video", "2020-08-16", [R, M, P], "YhofpDYpBMY", None, "wednesday-morning-flow-bd32w-wbjn4"),
    ("Prima Vista – Sofía (Video Clip)", "2020-08-10", [R, M, P, V], "WtC4xYX2dCo", None, "pka2tn8sgzetmmryazfll9yh5hynfh"),
    ("B-Spot – No Mercy {House} (Sax: Angel Cure)", "2020-07-14", [R, M, P, V], "bbaLCCXcs9U", None, "8agb29ggxgw9845r9rpp49klbgcsk3"),
    ("In Your Eyes – Sofía (The Weeknd Cover)", "2020-05-29", [R, M], "cZqRUSYdMBE", None, "daily-calm-yyhd4-ajaee"),
    ("Η άκρη του ορίζοντα – MICE The Swing Band (Quarantine Session #3)", "2020-05-03", [R, M, V], "9iv26e58UHE", None, "how-to-create-an-under-construction-page-nmhkn-et8z6-yhr99"),
    ("Όταν το ανοίξεις – MICE The Swing Band / Μάκης Δημάκης Swing Remake (Quarantine Session #2)", "2020-04-26", [R, M, V], "cQ0nJ9nLRLY", None, "john-mcenroe-does-voice-over-now-zpk5h-tc9nt-bn9x6"),
    ("Αφού το θες – MICE The Swing Band (Quarantine Session #1)", "2020-04-13", [R, M, V], "-5hiflGz-38", None, "everything-to-sell-anything-427ge-88xsk-zc9f6"),
    ("Daniel Se – Κατάθεση (prod. B-Spot) Official Video", "2020-03-21", [R], "xTITAPpuZxY", None, "new-video-k65jc-eyepy"),
]
# YouTube id of the Studio video shown large at the top of the Studio page
FEATURED_STUDIO = "t7BKH2e_P9s"  # Daniel Se – Ατέλεια

# ---------------------------------------------------------------- Music
MUSIC_ROLES = {
    "Composing": "Σύνθεση", "Lyrics": "Στίχοι", "Instrumentation": "Ενορχήστρωση", "Recording": "Ηχογράφηση",
    "Mixing": "Μίξη", "Production": "Παραγωγή", "Piano": "Πιάνο", "Bass": "Μπάσο", "Video editing": "Μοντάζ βίντεο",
}
# title, roles, media type, media id, note
MUSIC = [
    ("Roney K – If I Die", ["Composing", "Lyrics", "Instrumentation", "Recording", "Mixing", "Production"], "sc", "2122617141", KONTAKT_NOTE),
    ("Roney K – Drive Away", ["Composing", "Lyrics", "Instrumentation", "Recording", "Mixing", "Production"], "sc", "2122617681", KONTAKT_NOTE),
    ("Sofia – Prima Vista", ["Composing", "Instrumentation", "Recording", "Mixing", "Production"], "yt", "WtC4xYX2dCo", None),
    ("MICE The Swing Band – Η Άκρη του Ορίζοντα", ["Composing", "Instrumentation", "Piano", "Bass", "Recording", "Mixing", "Video editing"], "yt", "9iv26e58UHE", None),
    ("MICE The Swing Band – Τα Χριστούγεννα των MICE", ["Composing", "Instrumentation", "Piano", "Bass"], "yt", "so0gVD3iMxQ", None),
    ("MICE The Swing Band – Όπως Παλιά (swing cover)", ["Instrumentation", "Piano", "Bass"], "yt", "deyOzAIEfTc", None),
    ("MICE The Swing Band – Όταν το Ανοίξεις (swing cover)", ["Instrumentation", "Piano", "Bass", "Recording", "Mixing", "Video editing"], "yt", "cQ0nJ9nLRLY", None),
    ("MICE The Swing Band – Αφού το Θες (swing cover)", ["Instrumentation", "Piano", "Bass"], "yt", "-5hiflGz-38", None),
    ("B-Spot – No Mercy", ["Composing", "Instrumentation", "Production", "Recording", "Mixing", "Video editing"], "yt", "bbaLCCXcs9U", None),
]

# ---------------------------------------------------------------- Music technology projects
# block kinds: ("p", T) ("h", T) ("img", url, T caption or None) ("yt", id) ("link", url, T label) ("ul", [T..]) ("mono", text)
DL_FREE = T("Download the device for free on maxforlive.com", "Κατεβάστε το device δωρεάν στο maxforlive.com")

MAX4LIVE = [
    {
        "slug": "next-loop", "old": "project-one-ephnc-8z4hc", "title": "Next Loop",
        "cover": CDN + "1739979589787-126PNGM874XRR947WLC4/NEXT+LOOP+PROMO.jpg",
        "summary": T("A looping device for Ableton Live.", "Device για looping στο Ableton Live."),
        "download": ("https://maxforlive.com/library/device/11549/next-loop", DL_FREE),
        "blocks": [
            ("p", T("This device was made for looping inside Ableton Live. It can be added as a Max for Live device and does the following.",
                    "Αυτό το device δημιουργήθηκε για χρήση looping στο περιβάλλον του Ableton Live. Μπορεί να προστεθεί σαν M4L device και να εκτελεί τις παρακάτω διαδικασίες.")),
            ("p", T("The first button works as start/stop. It reads the first clip on the selected track: if there is no clip it starts recording one, and if a clip is already recording it stops the recording.",
                    "Το πρώτο button λειτουργεί σαν start/stop, διαβάζει το πρώτο clip στο selected track, άμα δεν υπάρχει clip ξεκινάει να ηχογραφεί το clip, εάν βρισκόμαστε σε ηχογράφηση και έχει δημιουργηθεί clip τότε σταματάει την ηχογράφηση.")),
            ("p", T("The second button works as a looper and does the following:", "Το δεύτερο button λειτουργεί σαν looper και κάνει τις εξής διαδικασίες:")),
            ("ul", [
                T("Finds the selected track.", "Αναγνωρίζει ποιο είναι το selected track."),
                T("If there is no clip, it arms the selected track and starts recording the first clip.",
                  "Εάν δεν υπάρχει clip, οπλίζει το selected track και ξεκινάει να ηχογραφεί το πρώτο clip."),
                T("Pressed again, it disarms the selected track and stops its recording, then arms and selects the next track and starts recording there.",
                  "Εάν ξαναπατηθεί αφοπλίζει το selected track, σταματάει την ηχογράφησή του, οπλίζει και κάνει select το επόμενο track και ξεκινάει την ηχογράφησή του."),
                T("If the next track already has a clip, it doesn't erase it; it simply starts playing it.",
                  "Εάν στο επόμενο track υπάρχει clip δεν το σβήνει, απλά ξεκινάει την αναπαραγωγή του."),
            ]),
            ("h", T("The device's code", "Ο κώδικας του device")),
            ("img", CDN + "7ca44fad-13b1-4569-96c4-158a375c42f0/ANAGWRISH.png", T("Finding the selected track", "Αναγνώριση selected track")),
            ("img", CDN + "4c5ad565-a7c8-4750-824c-9b884d4b53c2/2ND.png", T("Finding the first clip and changing the selected track", "Αναγνώριση πρώτου clip και αλλαγή selected track")),
            ("img", CDN + "5fb3a4b8-4e31-46b3-a114-128a1344ac9b/3RD.png",
             T("Disarming the previous track, arming the next one, stopping the previous recording and starting the next",
               "Αφόπλιση προηγούμενου track, οπλισμός επόμενου track, stop recording προηγούμενου track, start recording επόμενου track")),
        ],
    },
    {
        "slug": "split-me-plz", "old": "project-one-ephnc-8z4hc-29tz4", "title": "Split Me Plz",
        "cover": CDN + "1740019137451-SVX3QXWXUUV2TDBVHBF9/Artwork.jpg",
        "summary": T("Splits a recorded drum clip into separate tracks automatically.", "Χωρίζει αυτόματα ένα ρυθμικό clip σε ξεχωριστά tracks."),
        "download": ("https://maxforlive.com/library/device/11569/split-me-plz", DL_FREE),
        "blocks": [
            ("p", T("This device was made to solve a problem many producers have in Ableton.",
                    "Αυτό το device δημιουργήθηκε για να λύσει ένα κοινό πρόβλημα μεταξύ πολλών παραγωγών στο Ableton.")),
            ("p", T("Say you're jamming in an Ableton session and record a nice drum groove. The next step is mixing it, so you duplicate the track once for every drum element you used and delete everything but one element from each copy. This device does that for you automatically.",
                    "Ας πούμε ότι τζαμάρεις σε ένα Ableton session και γράφεις ένα ωραίο ρυθμικό σε τύμπανα. Η επόμενη κίνηση είναι να το μιξάρεις, οπότε αντιγράφεις το κανάλι όσες φορές είναι και τα ρυθμικά στοιχεία που χρησιμοποίησες και αρχίζεις να αφαιρείς από κάθε κανάλι όλα τα ρυθμικά στοιχεία εκτός από ένα. Αυτό το device κάνει αυτή τη διαδικασία αυτόματα για εσένα.")),
            ("p", T("Add the device to the track, press the button, and it splits the track's first clip into as many tracks as there are drum elements in your recording.",
                    "Προσθέτεις το device στο επιθυμητό track, πατάς το κουμπί και το device χωρίζει το πρώτο clip του track σε τόσα tracks όσα και τα ρυθμικά στοιχεία που έχεις ηχογραφήσει.")),
            ("p", T("For now it only works in Session view and hasn't been tested on Ableton versions older than 12.0.5, so it may not run correctly there.",
                    "Προς το παρόν λειτουργεί μόνο σε session mode και δεν έχει δοκιμαστεί σε Ableton χαμηλότερης έκδοσης από 12.0.5, οπότε ενδέχεται να υπάρχουν προβλήματα κατά την εκτέλεσή του.")),
            ("h", T("The device's code", "Ο κώδικας του device")),
            ("img", CDN + "9b68befa-2a7a-4d3c-b44c-8d04b47ab107/SPLIT+ME+PLZ+1.0.2.png", T("Split Me Plz 1.0.2", "Split Me Plz 1.0.2")),
        ],
    },
]

ARDUINO = [
    {
        "slug": "video-selector-console", "old": "project-one-ephnc-sfz9g", "title": "Video Selector Console",
        "cover": CDN + "1739979437839-0HNXAM38EHK2GXE70MZY/PXL_20250104_002407741%7E2.jpg",
        "summary": T("A console for switching ensemble and recording room in real time.", "Κονσόλα επιλογής σχήματος και χώρου ηχογράφησης σε πραγματικό χρόνο."),
        "blocks": [
            ("p", T("In my 5th semester at Metropolitan College, a team of four of us was formed for the Public Project course. We decided to research how the acoustics of a room affect a recording, so we recorded 3 different ensembles in 7 different rooms. While preparing the presentation, I built this console.",
                    "Κατά το 5ο εξάμηνο της φοίτησής μου στο Μητροπολιτικό Κολλέγιο δημιουργήθηκε μια ομάδα 4 ατόμων για το μάθημα του Public Project. Κατά το εξάμηνο αυτό εγώ και η ομάδα μου αποφασίσαμε να ερευνήσουμε τον τρόπο με τον οποίο επηρεάζει η ακουστική του χώρου μία ηχογράφηση. Έτσι ηχογραφήσαμε 3 διαφορετικά σχήματα σε 7 διαφορετικούς χώρους. Κατά την προετοιμασία για την παρουσίαση του project κατασκεύασα αυτήν την κονσόλα.")),
            ("p", T("The idea is that each listener picks the ensemble they want to hear with one of the 3 buttons in the top row, and then, while the piece is playing, switches in real time between the rooms it was recorded in.",
                    "Η λογική πίσω από την κονσόλα είναι ότι ο κάθε χρήστης μπορεί να επιλέξει το σχήμα που θέλει να ακούσει επιλέγοντας ένα από τα 3 πλήκτρα στην επάνω σειρά και να αλλάξει σε πραγματικό χρόνο, ενώ εκτελείται το μουσικό έργο, τον χώρο στον οποίο γίνεται η ηχογράφηση.")),
            ("p", T("The console uses 10 illuminated push buttons and 2 Arduino Uno boards.",
                    "Για τη δημιουργία της κονσόλας χρησιμοποιήθηκαν 10 illuminated push buttons και 2 Arduino Uno.")),
            ("h", T("Wiring", "Συνδεσμολογία")),
            ("img", CDN + "a9b22726-c9ad-4f9e-bdfe-e0fe35709607/Buttons.png", T("Button wiring", "Συνδεσμολογία πλήκτρων")),
            ("img", CDN + "a46ea05c-7fd8-48a9-81b2-e4a0a14fefc5/Leds.png", T("LED wiring", "Συνδεσμολογία led")),
            ("h", T("Code", "Κώδικας")),
            ("link", "https://amcstudent-my.sharepoint.com/:f:/g/personal/gbatzios24b_amcstudent_edu_gr/ElOqmdb6-59JmWfn0q_2t_YBMl58NthO66sr9qn3Flrzog?e=Gqkt0g",
             T("allButtonsMASTER: code for the master Arduino", "allButtonsMASTER: ο κώδικας για το master Arduino")),
            ("link", "https://amcstudent-my.sharepoint.com/:f:/g/personal/gbatzios24b_amcstudent_edu_gr/EtZfvqNLmhNCrEbY7R1QVGwBEkcbTTEx97y1Y4LSSALILg?e=YMk5oP",
             T("allButtonsSLAVE: code for the slave Arduino", "allButtonsSLAVE: ο κώδικας για το slave Arduino")),
            ("img", CDN + "25a05a01-b99c-4dba-a527-6072f7edcd8b/PXL_20250104_002436135%7E3.jpg", T("Inside the box", "Φωτογραφία από το εσωτερικό του κουτιού")),
            ("h", T("The console in use", "Η κονσόλα σε εφαρμογή")),
            ("yt", "D3MhJLErvU4"),
        ],
    },
    {
        "slug": "interactive-live-performance-system", "old": "project-one-f5w4d-gewle", "title": "Interactive Live Performance System",
        "cover": CDN + "1740023071709-RKVDQE92G4UG3NTFEB8B/Screenshot+2025-02-20+054410.png",
        "summary": T("Arduino sensors that control Ableton through Max MSP.", "Arduino και σένσορες που ελέγχουν το Ableton μέσω Max MSP."),
        "blocks": [
            ("p", T("In my 5th semester at Metropolitan College, for the course \u201cMusic Technology and Production\u201d, I built a system of an Arduino and sensors that, through Max MSP, drive controls in Ableton. This way, when I interact with the sensors in front of me, I can control the DAW's parameters live.",
                    "Κατά το 5ο εξάμηνο της φοίτησής μου στο Μητροπολιτικό Κολλέγιο, για τους σκοπούς του μαθήματος «Music Technology and Production» δημιούργησα ένα σύστημα από Arduino και σένσορες τα οποία μέσω της Max MSP τροφοδοτούν ρυθμιστικά του προγράμματος Ableton, έτσι ώστε όταν εγώ αλληλεπιδρώ με τους σένσορες μπροστά μου να μπορώ εν δυνάμει να χειρίζομαι τις παραμέτρους του DAW.")),
            ("p", T("I used an Arduino Uno Rev3 as the mainboard. The sensors I chose are:", "Ως mainboard χρησιμοποίησα το Arduino Uno Rev3. Οι σένσορες που αποφάσισα να χρησιμοποιήσω είναι:")),
            ("ul", [
                T("The HC-SR04 ultrasonic sensor, which sends ultrasonic pulses and receives their reflection. From the time between sending and receiving, the Arduino returns the distance of the nearest object from the sensor.",
                  "Ο HC-SR04 Ultrasonic Sensor, ο οποίος στέλνει υπερηχητικά σήματα και στη συνέχεια λαμβάνει πίσω την ανάκλαση του σήματος. Υπολογίζοντας τη διαφορά χρόνου αναπαραγωγής και ακρόασης, το Arduino επιστρέφει στον χρήστη την απόσταση που έχει το πιο κοντινό αντικείμενο από τον σένσορα."),
                T("The MPU6050, a three-axis accelerometer and gyroscope. For this project I use the gyroscope, meaning the sensor's angle on each axis, not its acceleration.",
                  "Ο MPU6050 Accelerometer, ένα επιταχυνσιόμετρο και γυροσκόπιο τριών αξόνων. Για το συγκεκριμένο project με ενδιαφέρει η λειτουργία του γυροσκοπίου, δηλαδή η γωνία που έχει ο σένσορας σε κάθε άξονα και όχι η επιτάχυνσή του."),
                T("The Waveshare liquid level sensor, which uses vertical metal contacts and the conductivity of water so the Arduino can return a value based on how deep the sensor sits in the liquid.",
                  "Ο Waveshare Liquid Level Sensor, ο οποίος χρησιμοποιώντας κατακόρυφες μεταλλικές επαφές και αξιοποιώντας την αγωγιμότητα του νερού, επιτρέπει στο Arduino να επιστρέψει στον χρήστη την τιμή ανάλογα με τη στάθμη του υγρού μέσα στο οποίο βρίσκεται ο σένσορας."),
            ]),
            ("p", T("First I read the setup guide for each sensor:", "Πρώτα διάβασα τις οδηγίες εγκατάστασης για τον κάθε σένσορα:")),
            ("link", "https://maker.pro/arduino/tutorial/how-to-interface-arduino-and-the-mpu-6050-sensor", T("maker.pro: MPU-6050", "maker.pro: MPU-6050")),
            ("link", "https://www.waveshare.com/wiki/Liquid_Level_Sensor", T("waveshare.com: Liquid Level Sensor", "waveshare.com: Liquid Level Sensor")),
            ("link", "https://projecthub.arduino.cc/Isaac100/getting-started-with-the-hc-sr04-ultrasonicsensor-7cabe1", T("projecthub.arduino.cc: HC-SR04", "projecthub.arduino.cc: HC-SR04")),
            ("h", T("Wiring", "Συνδεσμολογία")),
            ("p", T("Then I found the diagrams with the correct wiring.", "Μετά βρήκα τα διαγράμματα με τη σωστή συνδεσμολογία.")),
            ("img", CDN + "6995f475-e466-49c2-a2fc-42072d946ab1/DISTANCE+ARDUINO+CONNECTION.png",
             T("HC-SR04 ultrasonic sensor. I used digital pins 12 and 13 instead of 9 and 10 as shown in the picture.",
               "HC-SR04 Ultrasonic Sensor. Για τη σύνδεση χρησιμοποίησα τα digital pins 12, 13 και όχι τα 9, 10 όπως φαίνεται στην εικόνα.")),
            ("img", CDN + "c07c74cf-4738-4764-baba-8ea0ae993144/Screenshot+2025-03-08+003122.png", T("MPU6050 accelerometer", "MPU6050 Accelerometer")),
            ("img", CDN + "9f9c0f1c-4bd8-4ddf-9aac-c6f72122eb7d/LIQUID+ARDUINO+CONNECTION.jpg", T("Waveshare liquid level sensor", "Waveshare Liquid Level Sensor")),
            ("p", T("Unlike the other two sensors, the MPU6050 had no pins ready for connection, so for the first test I connected it with crocodile clips.",
                    "Ο MPU6050 δεν είχε έτοιμα pins για σύνδεση όπως οι άλλοι δύο σένσορες, οπότε για την αρχική δοκιμή τον σύνδεσα με καλώδια τύπου κροκοδειλάκι.")),
            ("img", CDN + "874c4c3d-f560-45f0-8426-5d289cc58daa/PXL_20241223_190656481.jpg", T("First test of the MPU6050", "Αρχική δοκιμή του MPU6050")),
            ("p", T("Then I soldered on the header that came with the sensor.", "Στη συνέχεια έκανα συγκόλληση του εξαρτήματος με το οποίο ήρθε ο σένσορας.")),
            ("img", CDN + "5edd2db0-3e51-4154-9b46-9bf22a451a9e/PXL_20241224_210733357.jpg", T("Soldering", "Συγκόλληση")),
            ("h", T("Code", "Κώδικας")),
            ("p", T("I connected each sensor to the Arduino separately and looked for its code. I found example code for each sensor in the Arduino IDE library.",
                    "Συνέδεσα τον κάθε σένσορα ξεχωριστά επάνω στο Arduino και άρχισα να ψάχνω τον εκάστοτε κώδικα. Μέσα από το library του Arduino IDE βρήκα τους κώδικες για τον κάθε σένσορα.")),
            ("p", T("I tested each sensor on its own, and once they all worked I merged the three programs into one so all three sensors could run at the same time.",
                    "Δοκίμασα τον κάθε σένσορα ξεχωριστά και αφού είδα ότι δουλεύουν ξεκίνησα να συγχωνεύω τους 3 κώδικες σε έναν, έτσι ώστε να μπορέσω να λειτουργήσω και τους 3 σένσορες ταυτόχρονα.")),
            ("p", T("Based on the photos, I then drew my own diagram with all three sensors connected to the Arduino at once.",
                    "Στη συνέχεια, με βάση τις φωτογραφίες, δημιούργησα ένα δικό μου διάγραμμα κατά το οποίο και οι τρεις σένσορες συνδέονται ταυτόχρονα επάνω στο Arduino.")),
            ("img", CDN + "1f17d8fe-83a1-4e50-9682-e4bfa1f04c4e/CIRCUT.png", T("The final circuit", "Το τελικό κύκλωμα")),
            ("p", T("As a result, all 3 sensors worked together, and the serial output printed this every 10 ms:",
                    "Ως αποτέλεσμα οι 3 σένσορες δούλεψαν ταυτόχρονα και στο serial output έλαβα το εξής κάθε 10ms:")),
            ("mono", "Distance: 400   Water level: 3   angleX: -0.62   angleY: -1.39   angleZ: -36.12"),
            ("p", T("Distance is the ultrasonic sensor's reading in centimetres from 0 to 400, Water level is the water level from 0 to 650, and angle X, Y, Z are the gyroscope's angles on each axis, from about -90 to +90.",
                    "Όπου Distance είναι η απόσταση του ultrasonic σένσορα σε εκατοστά από 0 έως 400, Water level είναι η στάθμη του νερού από 0 έως 650, και angle X, Y, Z είναι η γωνία στην οποία βρίσκεται το γυροσκόπιο σε κάθε άξονα, από -90 έως +90 περίπου.")),
            ("h", T("The system in use", "Το σύστημα σε χρήση")),
            ("yt", "t4Y2T5BCWVQ"),
        ],
    },
    {
        "slug": "dmx-rgb-controller", "old": "project-one-f5w4d-gewle-6b7sb", "title": "DMX RGB Controller",
        "cover": CDN + "1741376048534-2OJCH369MTWLNIB78QT7/Screenshot+2025-03-07+213334.png",
        "summary": T("A small DMX controller for an LED strip.", "Μικρός DMX controller για ταινία led."),
        "blocks": [
            ("p", T("This project started when we added a DMX LED strip to the break room at my work. It didn't make sense to tie up a whole DMX console just to control one strip, so I built a DMX controller that also takes up much less space.",
                    "Το παρόν project δημιουργήθηκε διότι προσθέσαμε μία led DMX ταινία στον χώρο αναψυχής της εργασίας μου. Επειδή δεν θα ήταν συνετό να δεσμεύσουμε μια ολόκληρη DMX κονσόλα για τον χειρισμό αυτής της ταινίας, αποφάσισα να φτιάξω ένα DMX controller το οποίο καταλαμβάνει και πολύ λιγότερο χώρο.")),
            ("img", CDN + "e8993880-86cb-4f97-8bfd-2e07d435cd35/PXL_20250221_154347384.jpg", None),
            ("h", T("The controller in use", "Η κονσόλα σε χρήση")),
            ("yt", "KXpWEysbz70"),
        ],
    },
    {
        "slug": "multi-computer-midi-button", "old": "project-one-f5w4d-gewle-853dn", "title": "Multi-Computer MIDI Button",
        "cover": CDN + "1741376475313-FWMK3ZPGMGJDFYTDDRRV/PXL_20250222_000159434.jpg",
        "summary": None,
        "blocks": [
            ("img", CDN + "281d863b-938d-4544-bd04-35d8788e2824/PXL_20250221_211244325.jpg", None),
        ],
    },
    {
        "slug": "midi-stomp-button", "old": "project-one-f5w4d-gewle-6b7sb-t5lr7", "title": "MIDI Stomp Button",
        "cover": CDN + "1741376549602-Y2HU26L1YCRJQENDUEH9/PXL_20250227_170422963.jpg",
        "summary": T("A foot switch for looping in Ableton.", "Πλήκτρο ποδιού για looping στο Ableton."),
        "blocks": [
            ("p", T("In the video below you can see the button used for looping in Ableton:", "Στο παρακάτω βίντεο μπορείτε να δείτε το πλήκτρο σε χρήση looping στο Ableton:")),
            ("yt", "Pj3tPOVM-bk"),
        ],
    },
]

PLUGINS = [
    {
        "slug": "telestage", "old": "telestage", "title": "TeleStage",
        "cover": CDN + "6c732005-f1b9-4012-be2b-99aca801e0b7/splash_bg.png",
        "summary": T("Hybrid Spatial Emulation Audio Engine v1.0.1", "Hybrid Spatial Emulation Audio Engine v1.0.1"),
        "download": ("https://drive.google.com/drive/folders/1kKskBe6eCKh7mOTI4CPJs8PbRfFex0bB?usp=sharing", T("Download TeleStage", "Κατεβάστε το TeleStage")),
        "blocks": [
            ("p", T("TeleStage is a 3D spatial mixer and reverb engine that rethinks how instruments are positioned in a mix.",
                    "Το TeleStage είναι ένας 3D spatial mixer και reverb engine που αλλάζει τον τρόπο με τον οποίο τοποθετούνται τα όργανα μέσα σε μια μίξη.")),
            ("p", T("Most spatial audio plugins only allow you to place a sound source somewhere inside a virtual room. TeleStage takes a different approach: it gives you the ability to place and configure the microphones. Instead of just panning a sound, you are constructing a complete studio recording setup within an unlimited virtual space.",
                    "Τα περισσότερα spatial audio plugins σου επιτρέπουν μόνο να τοποθετήσεις μια πηγή ήχου κάπου μέσα σε ένα εικονικό δωμάτιο. Το TeleStage ακολουθεί διαφορετική προσέγγιση: σου δίνει τη δυνατότητα να τοποθετήσεις και να ρυθμίσεις τα μικρόφωνα. Αντί απλώς να κάνεις pan σε έναν ήχο, στήνεις ένα ολόκληρο setup ηχογράφησης στούντιο μέσα σε έναν απεριόριστο εικονικό χώρο.")),
            ("p", T("By using a cross-track network, TeleStage brings individual channels from across your DAW onto one shared stage without complex routing or multiple heavy reverb instances. It calculates the exact acoustic geometry between your instruments and your virtual microphones, combining accurate early reflections with a natural reverb tail to capture how your mix actually behaves in a physical room.",
                    "Μέσω ενός δικτύου ανάμεσα στα κανάλια, το TeleStage φέρνει ξεχωριστά κανάλια από όλο το DAW σου σε μία κοινή σκηνή, χωρίς περίπλοκο routing ή πολλά βαριά reverb. Υπολογίζει την ακριβή ακουστική γεωμετρία ανάμεσα στα όργανα και στα εικονικά μικρόφωνα, συνδυάζοντας ακριβείς πρώιμες ανακλάσεις με μια φυσική ουρά αντήχησης, ώστε να αποδίδει πώς συμπεριφέρεται πραγματικά η μίξη σου μέσα σε έναν φυσικό χώρο.")),
        ],
    },
]

# ---------------------------------------------------------------- Home: selected work
# title, kicker, line, link (site path), image
SELECTED = [
    ("Αντιγόνη", T("Theater · Athens Concert Hall, 2025", "Θέατρο · Μέγαρο Μουσικής Αθηνών, 2025"),
     T("Original music, Ableton programming and sound mixing.", "Σύνθεση μουσικής, προγραμματισμός Ableton και μίξη ήχου."),
     "/theater/", THEATER[4][5]),
    ("TeleStage", T("DAW plugin · 2026", "DAW plugin · 2026"),
     T("My 3D spatial mixer and reverb: you place the microphones, not just the sounds.",
       "Ο δικός μου 3D spatial mixer και reverb: τοποθετείς τα μικρόφωνα, όχι μόνο τους ήχους."),
     "/daw-plugins/telestage/", PLUGINS[0]["cover"]),
    ("Drive Away", T("Production · Custom Kontakt library", "Παραγωγή · Δική μου βιβλιοθήκη Kontakt"),
     T("A whole production built only from the sounds of my car.", "Μια ολόκληρη παραγωγή φτιαγμένη μόνο από τους ήχους του αυτοκινήτου μου."),
     "/music/", CDN + "4ed05501-cae9-435d-a4ed-df85cdf4cc60/Screenshot+2025-11-14+174025.png"),
]

# ---------------------------------------------------------------- Academic portfolio
METRO = T("Metropolitan College", "Μητροπολιτικό Κολλέγιο")
AKMI = T("AKMI Institution", "ΙΕΚ ΑΚΜΗ")
REPORT = T("Report PDF", "Αναφορά PDF")
# title, institution, video link, report link(s) (label,url), thumbnail
ACADEMIC = [
    (T("Ableton – Arduino – Resolume – DMX live performance", "Ableton – Arduino – Resolume – DMX live performance"), METRO,
     "https://www.youtube.com/watch?v=6aN2xGOzOHY",
     [(REPORT, "https://drive.google.com/file/d/1cuRRTa8AWUro0lh2Y89iFstgeiZpZfqA/view?usp=sharing")],
     CDN + "3dd0b2da-3c5f-421a-8188-edc5d583293d/maxresdefault.jpg"),
    (T("Car sounds Kontakt library", "Βιβλιοθήκη Kontakt με ήχους αυτοκινήτου"), T("Metropolitan College · Thesis", "Μητροπολιτικό Κολλέγιο · Πτυχιακή"),
     None,
     [(T("Project files", "Αρχεία project"), "https://drive.google.com/drive/folders/1275N_4kwX0jqjN8l_VBaVzwC7LytYnlG?usp=sharing")],
     CDN + "4ed05501-cae9-435d-a4ed-df85cdf4cc60/Screenshot+2025-11-14+174025.png"),
    (T("Ableton live performance", "Live performance με Ableton"), METRO,
     "https://www.youtube.com/watch?v=Qbx1qjhvTgs",
     [(REPORT, "https://drive.google.com/file/d/1pQWnkkimusWfDEFqE5tSnUGRqr8ATENh/view?usp=sharing")],
     CDN + "8e76f8e1-498a-4181-b7d1-97a0a6c89ad2/Screenshot+2025-02-23+001457.png"),
    (T("Live performance with Arduino and Max MSP", "Live performance με Arduino και Max MSP"), METRO,
     "https://www.youtube.com/watch?v=t4Y2T5BCWVQ",
     [(REPORT, "https://drive.google.com/file/d/1pQWnkkimusWfDEFqE5tSnUGRqr8ATENh/view?usp=sharing")],
     CDN + "469d379b-2e04-423f-85ac-7e6547c415c6/Screenshot+2025-02-23+001553.png"),
    (T("Live performance with Resolume Arena", "Live performance με Resolume Arena"), METRO,
     "https://www.youtube.com/watch?v=3_HeCPmrUng",
     [(REPORT, "https://drive.google.com/file/d/1pQWnkkimusWfDEFqE5tSnUGRqr8ATENh/view?usp=sharing")],
     CDN + "74eaa421-6de6-4e1f-94ef-13b02e963e56/Screenshot+2025-02-23+001648.png"),
    (T("Foley project 1", "Foley project 1"), AKMI,
     "https://akmimoodle-my.sharepoint.com/:f:/g/personal/gbatzios_iekakmi_edu_gr/Ek7DY5dWN7xAoPSP8ceAY6ABitsPt6DVOeYFKZEYdmUnCw?e=g8DmrN",
     [], CDN + "3ee0da3d-abe4-459d-a50b-3895e2f28e65/Screenshot+2025-02-23+002603.png"),
    (T("Foley project 2", "Foley project 2"), AKMI,
     "https://akmimoodle-my.sharepoint.com/:f:/g/personal/gbatzios_iekakmi_edu_gr/EqPbaENjCGpArQwbSqK5UlwBFEdf199AteHumQ9bVVeRKw?e=cJqWjI",
     [], CDN + "8fa98a77-246f-4087-a57d-a8a0c2679bf3/Screenshot+2025-02-23+002226.png"),
    (T("Final project: composition, recording and mixing of my song", "Τελικό project: σύνθεση, ηχογράφηση και μίξη δικού μου τραγουδιού"), AKMI,
     "https://akmimoodle-my.sharepoint.com/:f:/g/personal/gbatzios_iekakmi_edu_gr/EjHC948lcCRBqjgesMVD3NMBPcmb9TV1SXU7SQ07Ql99ow?e=0f5xEh",
     [], CDN + "826cee32-3367-4ff0-b605-01eb87fbade9/Screenshot+2025-02-23+002732.png"),
]

# ---------------------------------------------------------------- CV
ATHENS = T("Athens", "Αθήνα")
GREECE = T("Greece", "Ελλάδα")
CV = {
    "objective": T("My professional objective is to leverage my diverse skill set and extensive experience for the technical, as well as the artistic aspects of Audio, Sound and Music.",
                   "Επαγγελματικός μου στόχος είναι να αξιοποιήσω το ευρύ φάσμα δεξιοτήτων και την εμπειρία μου τόσο στην τεχνική όσο και στην καλλιτεχνική πλευρά του ήχου και της μουσικής."),
    # title, kind, company, place, when, description
    "work": [
        ("Christmas Theater", T("Theater venue", "Θέατρο"), "Roadies", ATHENS, T("May 2025 – Today", "Μάιος 2025 – Σήμερα"),
         T("Sound mixing for theatrical shows and live music shows. Audio-visual cues programming. Audio-visual equipment setup and operation.",
           "Μίξη ήχου για θεατρικές παραστάσεις και live μουσικές εμφανίσεις. Προγραμματισμός οπτικοακουστικών cues. Στήσιμο και χειρισμός οπτικοακουστικού εξοπλισμού.")),
        (T("Theatrical Tour 2025", "Θεατρική περιοδεία 2025"), None, "Roadies", GREECE, T("Jul 2025 – Sep 2025", "Ιούλ 2025 – Σεπ 2025"),
         T("Sound mixing and projection mapping. Theatrical tour for 10 venues in Greek islands.",
           "Μίξη ήχου και projection mapping. Θεατρική περιοδεία σε 10 χώρους στα ελληνικά νησιά.")),
        ("\"Michalis Kakogiannis\"", T("Cultural institution", "Πολιτιστικό ίδρυμα"), "Roadies", ATHENS, T("May 2024 – May 2025", "Μάιος 2024 – Μάιος 2025"),
         T("Sound mixing for theatrical shows and live music shows. Show lights programming and operation. Audio-visual cues programming.",
           "Μίξη ήχου για θεατρικές παραστάσεις και live μουσικές εμφανίσεις. Προγραμματισμός και χειρισμός φώτων παράστασης. Προγραμματισμός οπτικοακουστικών cues.")),
        (T("Theatrical Tour 2024", "Θεατρική περιοδεία 2024"), None, "Athenian Theaters", GREECE, T("Jun 2024 – Sep 2024", "Ιούν 2024 – Σεπ 2024"),
         T("Sound mixing and audio equipment operation, theatrical tour for 34 venues in Greece.",
           "Μίξη ήχου και χειρισμός ηχητικού εξοπλισμού, θεατρική περιοδεία σε 34 χώρους στην Ελλάδα.")),
        ("Coronet Theater", T("Theater venue", "Θέατρο"), "Coronet Theater", ATHENS, T("Sep 2023 – May 2024", "Σεπ 2023 – Μάιος 2024"),
         T("Sound mixing for theatrical shows. Theater shows light design and operation.",
           "Μίξη ήχου για θεατρικές παραστάσεις. Σχεδιασμός και χειρισμός φωτισμού παραστάσεων.")),
        ("The Golden Hall", T("Mall live venue", "Χώρος live σε εμπορικό κέντρο"), "LifeWorks Productions", ATHENS, T("Oct 2022 – May 2023", "Οκτ 2022 – Μάιος 2023"),
         T("Sound mixing for live jazz shows.", "Μίξη ήχου για live jazz εμφανίσεις.")),
    ],
    "education": [
        (T("Music Technology", "Music Technology"), T("Bachelor of Arts", "Πτυχίο (BA)"),
         T("University of East London through Metropolitan College of Greece", "University of East London μέσω του Μητροπολιτικού Κολλεγίου"), ATHENS, "2022 – 2025",
         T("The BA (Hons) Music Technology & Production at Metropolitan College is focused on Digital Technology and New Technologies, preparing students who wish to follow a career in Music Production for the opportunities and challenges of the 21st century.",
           "Το BA (Hons) Music Technology & Production του Μητροπολιτικού Κολλεγίου εστιάζει στην ψηφιακή τεχνολογία και τις νέες τεχνολογίες, προετοιμάζοντας όσους θέλουν να ακολουθήσουν καριέρα στη μουσική παραγωγή για τις ευκαιρίες και τις προκλήσεις του 21ου αιώνα.")),
        (T("Sound Engineering", "Τεχνικός Ήχου"), T("Diploma", "Δίπλωμα"), T("IEK AKMI", "ΙΕΚ ΑΚΜΗ"), ATHENS, "2022 – 2024",
         T("This program provided a comprehensive understanding of sound engineering principles, including live mixing, studio mixing, hardware and software for music production and audio editing.",
           "Το πρόγραμμα έδωσε ολοκληρωμένη γνώση των αρχών της ηχοληψίας: live μίξη, μίξη στούντιο, hardware και software για μουσική παραγωγή και επεξεργασία ήχου.")),
        (T("Music High School", "Μουσικό Σχολείο"), T("Diploma", "Απολυτήριο"), T("Music School of Komotini", "Μουσικό Σχολείο Κομοτηνής"), T("Komotini", "Κομοτηνή"), "2012 – 2015",
         T("The music school taught me the fundamentals of music through a series of instruments, while also providing the essential music theory I needed at the time.",
           "Το μουσικό σχολείο μου έμαθε τις βάσεις της μουσικής μέσα από διάφορα όργανα, μαζί με τη θεωρία της μουσικής που χρειαζόμουν τότε.")),
    ],
    "skills": [T("Recording", "Ηχογράφηση"), T("Mixing", "Μίξη"), T("Video editing", "Μοντάζ βίντεο"), T("Show lights programming", "Προγραμματισμός φώτων παράστασης"),
               T("Arduino programming", "Προγραμματισμός Arduino"), T("Max4Live devices programming", "Προγραμματισμός Max4Live devices"), T("Qlab programming", "Προγραμματισμός Qlab")],
    "certifications": [
        ("Dante Levels 1, 2 and 3", "Audinate"),
        ("YouTube Music Rights Management", "YouTube"),
        ("Fundamentals of Digital Marketing", "Google"),
        ("The Technology of Music Production", "Berklee College of Music"),
        ("The Art of Music Production", "Berklee College of Music"),
        ("Developing Your Musicianship", "Berklee College of Music"),
        ("Audio Engineering Program of Studies", "Pearson"),
    ],
    "software": [
        ("Cubase", "Steinberg"), ("Live", "Ableton"), ("Max", "Cycling '74"), ("Pro Tools", "Avid"),
        ("Qlab", "Figure 53"), ("SCS", "Show Cue Systems"), ("LA Network Manager", "L-Acoustics"),
        ("Soundvision", "L-Acoustics"), ("ArmoniaPlus", "Powersoft"), ("Light Factory / NEO", "Dream Solutions"),
        ("Glypheo", "Anomes SARL"), ("Photoshop", "Adobe"), ("Premiere Pro", "Adobe"), ("Lightroom", "Adobe"),
    ],
    "mixers": [
        ("Allen & Heath", "QU Series, SQ Series, dLive"),
        ("Yamaha", "QL Series"),
        ("Midas", "M Series"),
        ("Behringer", "X Series"),
    ],
}
